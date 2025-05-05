from typing import List
from transformers import GPT2TokenizerFast

class MessageChunkSplitter:
    def __init__(self, max_tokens_per_chunk: int = 3500):
        self.max_tokens = max_tokens_per_chunk
        self.tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

    def split_text(self, messages: List[dict]) -> List[str]:
        chunks = []
        current_chunk = []
        current_tokens = 0

        for message in messages:
            formatted = self._format_message(message["author"], message["text"])
            message_tokens = len(self.tokenizer.encode(formatted))

            if current_tokens + message_tokens > self.max_tokens:
                chunks.append("\n".join(current_chunk))
                current_chunk = [formatted]
                current_tokens = message_tokens
            else:
                current_chunk.append(formatted)
                current_tokens += message_tokens

        if current_chunk:
            chunks.append("\n".join(current_chunk))
        return chunks

    def _format_message(self, author: str, text: str) -> str:
        return f"<b>{author}:</b> {text}"

