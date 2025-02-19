import datetime
from django.db import models

class ChatSource(models.TextChoices):
    telegram = 'Telegram', 'telegram'
    mattermost = 'Mattermost', 'mattermost'

class GenerationSettings(models.Model):
    frequency = models.DurationField(verbose_name="Frequency")
    timestamp = models.TimeField(verbose_name="Time")

class EmployeeAccount(models.Model):
    id = models.AutoField(primary_key=True)
    nickname = models.CharField(unique=True)
    source = models.CharField(choices=ChatSource, max_length=20, default=ChatSource.telegram)
    # settings = models.ForeignKey(PrivateChatSettings, on_delete=models.CASCADE)

class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name="Name", max_length=200, null=True)
    surname = models.CharField(verbose_name="Surname", max_length=200, null=True)
    accounts = models.ForeignKey(EmployeeAccount, on_delete=models.CASCADE, null=True)


class ModelResponseStrategy(models.Model):
    strategy_name = models.CharField(verbose_name="Name", max_length=200)
    prompt_template = models.TextField(verbose_name="Prompt Template",
                                       default="""Сделай краткое тезисное резюме, расскажи, о кем разговаривали и к каким выводам пришли люди в тексте ниже:
                                        ```{текст}```
                                        Резюме:
                                       """)
    n_context = models.IntegerField(verbose_name="n_context", default=4096)



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

    def __str__(self):
        if self.reply_source_message_id is not None:
            return f"{self.employee_account.nickname} написал {self.text} в ответ на "
        return f"{self.employee_account.nickname} написал {self.text}\n"


class ModelResponse(models.Model):
    text = models.TextField(verbose_name="text")
    date = models.DateField(verbose_name="time", default=datetime.date.today)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    response_strategy = models.ForeignKey(ModelResponseStrategy, on_delete=models.CASCADE, null=True)

# class TaskSchedule(models.Model):
#     chat_for_summary = models.ForeignKey(Chat, on_delete=models.CASCADE)
#     chat_to_respond = models.ForeignKey(Chat, on_delete=models.CASCADE)
#     datetime = models.DateTimeField(default=datetime.datetime.now)
#
#     time_period_in_days = models.IntegerField(verbose_name="period", default=1)
#     interval_in_hours = models.IntegerField(verbose_name="interval", default=1)
#     frequency = models.DurationField(verbose_name="Frequency")
#     timestamp = models.TimeField(verbose_name="Time")