from decouple import config
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.llms import LlamaCpp


class SaigaModel:
    def __init__(self):
        max_ctx_size = 4096
        kwargs = {"model_path": config("MODEL_PATH"), "n_ctx": max_ctx_size, "max_tokens": max_ctx_size,
                  "n_gpu_layers": 1000, "n_batch": max_ctx_size}
        self._model_instance = LlamaCpp(**kwargs)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=4096, chunk_overlap=50, length_function=len)

    def generate_summary(self, text_chunk):
        template = """
        расскажи о кем разговаривали и к каким выводам пришли люди в тексте ниже и предоставь мне резюме чата 
        формируя резюме, руководствуйся следующими правилами:
        - указывай все важные задачи, которые кто-то должен сделать
        - описывай тему и задачи чата и сообщений
        - дополняй информацией о конкретном человеке, который предоставил информацию
        - никогда не приводи конкретные цитаты людей, оформляй текст в виде описания сообщений
        ```{текст}```
        резюме:
        """
        prompt = PromptTemplate(template=template, input_variables=["text"])
        llm_chain = LLMChain(prompt=prompt, llm=self._model_instance)

        summary = llm_chain.run(text_chunk)
        return summary

    def interact(self, query):
        chunks = self.text_splitter.split_text(query)
        chunk_summaries = []

        for chunk in chunks:
            summary = self.generate_summary(chunk)
            chunk_summaries.append(summary)

        combined_summary = "\n".join(chunk_summaries)
        summary = self.generate_summary(combined_summary)
        return summary
