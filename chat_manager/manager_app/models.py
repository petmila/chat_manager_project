import datetime
from django.db import models
from pgvector.django import VectorField
from pgvector.django import HnswIndex
from utils import text_preprocess

class ChatSource(models.TextChoices):
    telegram = 'Telegram', 'telegram'
    mattermost = 'Mattermost', 'mattermost'

class ModelFileExtension(models.TextChoices):
    gguf = 'GGUF', 'gguf'

class GenerationSettings(models.Model):
    frequency = models.DurationField(verbose_name="Frequency")
    timestamp = models.TimeField(verbose_name="Time")

class EmployeeAccount(models.Model):
    id = models.AutoField(primary_key=True)
    nickname = models.CharField(unique=True)
    source = models.CharField(choices=ChatSource, max_length=20, default=ChatSource.telegram)

class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name="Name", max_length=200, null=True)
    surname = models.CharField(verbose_name="Surname", max_length=200, null=True)
    accounts = models.ForeignKey(EmployeeAccount, on_delete=models.CASCADE, null=True)


class ModelResponseStrategy(models.Model):
    strategy_name = models.CharField(verbose_name="Name", max_length=200)
    model_name = models.CharField(verbose_name="Model Name", max_length=255, default="model-q4_K")
    model_file_extension = models.CharField(verbose_name="Model File Extension",
                                            choices=ModelFileExtension, max_length=20,
                                            default=ModelFileExtension.gguf)
    prompt_template = models.TextField(verbose_name="Prompt Template",
                                       default="""Сделай краткое тезисное резюме, расскажи, о кем разговаривали и к каким выводам пришли люди в тексте ниже:
                                        ```{текст}```
                                        Резюме:
                                       """)
    n_context = models.IntegerField(verbose_name="n_context", default=8192)



class Chat(models.Model):
    source_chat_id = models.CharField(verbose_name="Source Chat ID", max_length=200, null=True, unique=True)
    chat_source = models.CharField(choices=ChatSource, max_length=20, default=ChatSource.telegram)
    name = models.CharField(verbose_name="Name", max_length=200)
    generation_settings = models.ForeignKey(GenerationSettings, on_delete=models.CASCADE, null=True)

class Message(models.Model):
    timestamp = models.DateTimeField(default=datetime.datetime.now)
    text = models.TextField()
    employee_account = models.ForeignKey(EmployeeAccount, on_delete=models.CASCADE, null=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    source_message_id = models.IntegerField(verbose_name="Source Message ID", null=True)
    reply_source_message_id = models.IntegerField(verbose_name="Reply Source Message ID", null=True)

    def format(self):
        # if self.reply_source_message_id is not None:
        #     return {"message": self.text,
        #             "nickname": self.employee_account.nickname,
        #             "replying": ""}
        return {"message": text_preprocess.demojize(self.text),
                "nickname": self.employee_account.nickname}

class MessageEmbedding(models.Model):
    message = models.OneToOneField(Message, on_delete=models.CASCADE)
    embedding = VectorField(
        dimensions=768,
         help_text="Vector embeddings of the file content",
         null=True,
         blank=True
    )
    class Meta:
        indexes = [
            HnswIndex(
                name="clip_l14_vectors_index",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            )
        ]


class ModelResponse(models.Model):
    text = models.TextField(verbose_name="text")
    date = models.DateField(verbose_name="time", default=datetime.date.today)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    response_strategy = models.ForeignKey(ModelResponseStrategy, on_delete=models.CASCADE, null=True)
