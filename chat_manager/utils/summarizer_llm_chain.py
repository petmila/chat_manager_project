from encodings.utf_8 import encode
import logging
from decouple import config
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.llms import LlamaCpp
from langchain_core.output_parsers import StrOutputParser

from utils.text_splitter import MessageChunkSplitter

# DEFAULT_PROMPT="""
# <|begin_of_text|><|start_header_id|>system<|end_header_id|>
# Ты — Сайга, русскоязычный автоматический ассистент. Ты разговариваешь с людьми и помогаешь им.
# <|eot_id|><|start_header_id|>user<|end_header_id|>
# Kратко и тезисно резюмируй переданный текст
# Формируя резюме, руководствуйся следующими правилами: указывай пунктами все важные задачи и кто их должен сделать, всегда пиши на русском языке, не пиши больше 3 предложений и не включай инструкции в финальный результат
# Используй только html теги для форматирования, не вставляй прямые цитаты из текста в ответ
# Текст: {text}
# <|eot_id|><|start_header_id|>assistant<|end_header_id|>
# Резюме:
# """
# DEFAULT_PROMPT = """
# <|begin_of_text|><|start_header_id|>system<|end_header_id|>
# Ты — Сайга, русскоязычный автоматический ассистент. Ты разговариваешь с людьми и помогаешь им, используя HTML-теги для форматирования своих ответов.
# <|eot_id|><|start_header_id|>user<|end_header_id|>
# Кратко и тезисно резюмируй переданный текст по следующим правилам:
# <ul>
# <li>Перечисли все запланированные задачи и их исполнителей.</li>
# <li>Используй не более 3 предложений.</li>
# <li>Не включай инструкции и не цитируй текст напрямую.</li>
# <li>Отвечай строго на русском языке.</li>
# <li>Имена исполнителей передавай с тегами в формате @имя</li>
# </ul>
# Текст: {text}
# <|eot_id|><|start_header_id|>assistant<|end_header_id|>
# Резюме:
# """
DEFAULT_PROMPT = """
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
Ты — Сайга, русскоязычный автоматический ассистент. Ты разговариваешь с людьми и помогаешь им.
<|eot_id|><|start_header_id|>user<|end_header_id|>
Кратко и тезисно резюмируй переданный диалог в корпоративном чате.

Формируя резюме, следуй этим правилам:
- Указывай *все важные задачи* и *их исполнителей*.
- Пиши *на русском языке*.
- Не пиши больше **трёх предложений**.
- Не включай инструкции в финальный результат.
- Не вставляй *прямые цитаты* из текста в ответ.

Используй только **Markdown** для форматирования (жирный, курсив, списки, цитаты и т.п.)
Диалог: {text}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
**Резюме:**
"""



class Summarizer:
    def __init__(self,
                 max_ctx_size: int = 8192,
                 model_path: str = config("MODEL_PATH"),
                 template: str = DEFAULT_PROMPT):
        kwargs = {"model_path": model_path, "n_ctx": max_ctx_size,
                  "max_tokens": max_ctx_size,
                  "n_gpu_layers": 10, "n_batch": max_ctx_size,
                  "temperature": 0.2}

        self._model_instance = LlamaCpp(**kwargs)
        self.text_splitter = MessageChunkSplitter()

        self.prompt = PromptTemplate(template=template, input_variables=["text"])
        self.chain = self.prompt | self._model_instance | StrOutputParser()

    def generate_summary(self, text_chunk: str) -> str:
        try:
            return self.chain.invoke({"text": text_chunk})
        except Exception as e:
            logging.error(f"Ошибка при генерации резюме: {e}")
            return "[Ошибка при генерации]"

    def interact(self, query: list[dict]) -> str:
        chunks = self.text_splitter.split_text(query)
        logging.info(f"Разбито на {len(chunks)} чанков")
        summaries = []
        for i, chunk in enumerate(chunks, 1):
            summary = self.generate_summary(chunk)
            logging.info(f"Обработан чанк {i}/{len(chunks)}")
            summaries.append(summary)

        logging.info("Финальное резюме")
        return "\n".join(summaries)