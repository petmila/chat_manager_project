from datetime import datetime

from llama_index.core import SimpleDirectoryReader, get_response_synthesizer, SummaryIndex, Settings, PromptTemplate
from llama_index.core import DocumentSummaryIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from decouple import config
# from langchain.chains.llm import LLMChain
# from langchain_core.prompts import PromptTemplate
# from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.llms import LlamaCpp
from llama_index.core import Document
from nltk.corpus.reader import documents

max_ctx_size = 4096
kwargs = {"model_path": config("MODEL_PATH"), "n_ctx": max_ctx_size, "max_tokens": max_ctx_size,
                  "n_gpu_layers": 1000, "n_batch": max_ctx_size}
model_instance = LlamaCpp(**kwargs)
text_splitter = SentenceSplitter(chunk_size=4096, chunk_overlap=50)
Settings.embed_model = HuggingFaceEmbedding()
Settings.llm = model_instance
# Settings.embed_model = "local"
new_summary_tmpl_str = (
    "Контекстная информация из нескольких источников приведена ниже.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Учитывая информацию из нескольких источников, а не предварительные знания ответьте на вопрос ниже. Всегда отвечайте на русском языке.\n"
    "Запрос: {query_str}\n"
    "Отвечать: "
)
new_summary_tmpl = PromptTemplate(new_summary_tmpl_str)
response_synthesizer = get_response_synthesizer(
        response_mode=ResponseMode.TREE_SUMMARIZE, use_async=True, summary_template=new_summary_tmpl
)


def summary_index(text, doc_id):
    doc_summary_index = DocumentSummaryIndex.from_documents(
        documents=[Document(text=text, doc_id=doc_id)],
        llm=model_instance,
        transformations=[text_splitter],
        response_synthesizer=response_synthesizer,
        show_progress=True,
    )
    return doc_summary_index.get_document_summary(doc_id)


print(summary_index("""Fyodor Urlapov
@iamkrisanit добрый вечер. Будем ли мы завтра рассказывать по составленным к завтра презентациям? Или завтрашняя презентация - это лишь способ аггрегации информации, которую просто вы посмотрите в целях проверки дз?
18:43
Кристина
In reply to this message
Федор, добрый вечер! Планировали кратко заслушать презентации, чтобы я дала ОС по выбранным проектам, так как в итоге для них у вас будет разрабатываться БМ на финальной презентации
👍
18:45
Fyodor Urlapov
Хорошо, спасибо
👍
Сурен Вартанов invited anttoinettae
24 February 2024
09:28
Кристина
Отправляю список 55 бизнес-моделей (с описание и примером компаний), который поможет определить модель/модели коммерциализации выбранной компании.
09:36""", str(datetime.today())))