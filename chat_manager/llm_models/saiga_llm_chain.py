from decouple import config
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.llms import LlamaCpp
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


class SaigaModel:
    def __init__(self):
        max_ctx_size = 8192
        kwargs = {"model_path": config("MODEL_PATH"), "n_ctx": max_ctx_size, "max_tokens": max_ctx_size,
                  "n_gpu_layers": 10, "n_batch": max_ctx_size,
                  "temperature": 0.5}

        self._model_instance = LlamaCpp(**kwargs)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=4096, chunk_overlap=50, length_function=len)

    def generate_summary(self, text_chunk):
        # """Формируя резюме, руководствуйся следующими правилами: - указывай пунктами все важные задачи и кто их должен сделать - всегда пиши на русском языке и кратко - не пиши больше семи предложений и не включай инструкции в генерацию
        # """
        # template = """
        # Kратко и тезисно резюмируй переданный текст, выделяя задачи, которые озвучиваются в диалогах.
        # ```{текст}```
        # резюме:
        # """
        template = """
        <|begin_of_text|><|start_header_id|>system<|end_header_id|>
        Ты — Сайга, русскоязычный автоматический ассистент. Ты разговариваешь с людьми и помогаешь им.
        <|eot_id|><|start_header_id|>user<|end_header_id|>
        Kратко и тезисно резюмируй переданный текст, выделяя задачи, которые озвучиваются в диалогах
        Формируя резюме, руководствуйся следующими правилами: - указывай пунктами все важные задачи и кто их должен сделать - всегда пиши на русском языке и кратко - не пиши больше семи предложений и не включай инструкции в генерацию
        ```{текст}```
        <|eot_id|><|start_header_id|>assistant<|end_header_id|>
        Резюме:
        """
        prompt = PromptTemplate(template=template, input_variables=["text"])
        chain = prompt | self._model_instance | StrOutputParser()
        return chain.invoke(text_chunk)

    # def summary_of_summaries(self, summaries):
    #     template = """
    #     Систематизируй переданный текст в список с отдельными пунктами
    #     ```{текст}```
    #     Итоговое резюме:
    #     """
    #     prompt = PromptTemplate(template=template, input_variables=["text"])
    #     llm_chain = LLMChain(prompt=prompt, llm=self._model_instance)
    #
    #     summary = llm_chain.run(summaries)
    #     return summary

    def interact(self, query):
        # chunks = self.text_splitter.split_text(query)
        # chunk_summaries = []

        # for chunk in chunks:
        summary = self.generate_summary(query)
            # chunk_summaries.append(summary)

        # combined_summary = " ".join(chunk_summaries)
        # summary = self.summary_of_summaries(combined_summary)
        return summary
