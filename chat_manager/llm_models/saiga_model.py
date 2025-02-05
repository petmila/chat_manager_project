from decouple import config
from llama_cpp import Llama

SYSTEM_PROMPT = "Ты — Сайга, русскоязычный автоматический ассистент. Ты разговариваешь с людьми и помогаешь им."
SYSTEM_TOKEN = 1788
USER_TOKEN = 1404
BOT_TOKEN = 9225
LINEBREAK_TOKEN = 13

ROLE_TOKENS = {
    "user": USER_TOKEN,
    "bot": BOT_TOKEN,
    "system": SYSTEM_TOKEN
}

class SaigaModel:
    def __init__(self):
        self._model_instance = Llama(
            model_path=config("MODEL_PATH"),
            n_ctx=4096,
            n_parts=1,
            n_batch=126,
        )

    def get_message_tokens(self, role, content):
        message_tokens = self._model_instance.tokenize(content.encode("utf-8"))
        message_tokens.insert(1, ROLE_TOKENS[role])
        message_tokens.insert(2, LINEBREAK_TOKEN)
        message_tokens.append(self._model_instance.token_eos())
        return message_tokens

    def get_system_tokens(self, system_prompt):
        system_message = {
            "role": "system",
            "content": system_prompt
        }
        return self.get_message_tokens(**system_message)

    def interact(self, query, top_k=30, top_p=0.9, temperature=0.2, repeat_penalty=1.1):
        system_prompt = SYSTEM_PROMPT
        system_tokens = self.get_system_tokens(system_prompt)
        tokens = system_tokens
        self._model_instance.eval(tokens)

        message_tokens = self.get_message_tokens(role="user", content=query)
        role_tokens = [self._model_instance.token_bos(), BOT_TOKEN, LINEBREAK_TOKEN]
        tokens += message_tokens + role_tokens
        generator = self._model_instance.generate(
            tokens,
            top_k=top_k,
            top_p=top_p,
            temp=temperature,
            repeat_penalty=repeat_penalty
        )
        output = ''
        for token in generator:
            token_str = self._model_instance.detokenize([token]).decode("utf-8", errors="ignore")
            tokens.append(token)
            if token == self._model_instance.token_eos():
                break
            output += token_str
        return output
