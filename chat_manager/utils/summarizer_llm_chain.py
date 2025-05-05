from encodings.utf_8 import encode
import logging
from decouple import config
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.llms import LlamaCpp
from langchain_core.output_parsers import StrOutputParser

import text_splitter

class Summarizer:
    def __init__(self,
                 max_ctx_size: int = 8192,
                 model_path: str = config("MODEL_PATH"),
                 template: str = config("DEFAULT_PROMPT")):
        kwargs = {"model_path": model_path, "n_ctx": max_ctx_size,
                  "max_tokens": max_ctx_size,
                  "n_gpu_layers": 10, "n_batch": max_ctx_size,
                  "temperature": 0.2}

        self._model_instance = LlamaCpp(**kwargs)
        self.text_splitter = text_splitter.MessageChunkSplitter()

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