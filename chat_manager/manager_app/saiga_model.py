import os

# model_path = "D:/STUDY_WORK/MILA/llama-2-7b-chat.Q2_K.gguf"
# print(os.path.exists(model_path))
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


def get_message_tokens(model, role, content):
    message_tokens = model.tokenize(content.encode("utf-8"))
    message_tokens.insert(1, ROLE_TOKENS[role])
    message_tokens.insert(2, LINEBREAK_TOKEN)
    message_tokens.append(model.token_eos())
    return message_tokens


def get_system_tokens(model):
    system_message = {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
    return get_message_tokens(model, **system_message)


def interact(query, top_k=30, top_p=0.9, temperature=0.2, repeat_penalty=1.1):
    model = Llama(
        model_path=config("MODEL_PATH"),
        n_ctx=2000,
        n_parts=1,
    )
    system_tokens = get_system_tokens(model)
    tokens = system_tokens
    model.eval(tokens)

    message_tokens = get_message_tokens(model=model, role="user", content=query)
    role_tokens = [model.token_bos(), BOT_TOKEN, LINEBREAK_TOKEN]
    tokens += message_tokens + role_tokens
    generator = model.generate(
            tokens,
            top_k=top_k,
            top_p=top_p,
            temp=temperature,
            repeat_penalty=repeat_penalty
    )
    output = ''
    for token in generator:
        token_str = model.detokenize([token]).decode("utf-8", errors="ignore")
        tokens.append(token)
        if token == model.token_eos():
            break
        output += token_str
    return output



# def answer_query(query):
#     model = Llama(model_path=model_path)
#
#     # Prompt creation
#     system_message = "You are a helpful assistant"
#     user_message = query
#
#     prompt = f"""<s>[INST] <<SYS>>{system_message}<</SYS>>{user_message} [/INST]"""
#
#     # Model parameters
#     max_tokens = 200
#
#     # Run the model
#     output = model(prompt, max_tokens=max_tokens, echo=True)
#
#     # Print the model output
#     return output
