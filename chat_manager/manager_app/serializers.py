from rest_framework import serializers
from manager_app import models
import django_celery_beat.models as celery_beat


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Chat
        fields = ['id', 'chat_source', 'source_chat_id', 'name']
        extra_kwargs = {
            'name': {'help_text': 'Название чата'},
            'chat_source': {'help_text': 'Источник чата - название мессенджера'},
            'source_chat_id': {'help_text': 'Идентификатор чата в мессенджере источнике'},
        }


class SlugRelatedGetOrCreateField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        queryset = self.get_queryset()
        try:
            obj, created = queryset.get_or_create(**data)
            return obj
        except (TypeError, ValueError):
            self.fail("invalid")

    def to_representation(self, obj):
        """Возвращает только значение slug_field, а не весь объект"""
        return getattr(obj, self.slug_field)


class EmployeeAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EmployeeAccount
        fields = ['id', 'nickname', 'source']
        extra_kwargs = {
            'nickname': {'help_text': 'Никнейм сотрудника в мессенджере источнике'},
            'source': {'help_text': 'Источник аккаунта - название мессенджера'},
        }


class EmployeeSerializer(serializers.ModelSerializer):
    accounts = SlugRelatedGetOrCreateField(
        many=True,
        queryset=models.EmployeeAccount.objects.all(),
        slug_field='name'
    )

    class Meta:
        model = models.Employee
        fields = ['id', 'name', 'surname', 'accounts']
        extra_kwargs = {
            'name': {'help_text': 'Полное имя сотрудника'},
            'surname': {'help_text': 'Фамилия сотрудника'},
            'accounts': {'help_text': 'Все существующие аккаунты данного сотрудника'},
        }


class ModelResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ModelResponse
        fields = ['id', 'date', 'chat', 'text']
        extra_kwargs = {
            'date': {'help_text': 'Дата генерации резюме'},
            'chat': {'help_text': 'Чат, диалог которого суммаризировался'},
            'text': {'help_text': 'Сгенерированное резюме'},
        }


class MessageSerializer(serializers.ModelSerializer):
    employee_account = SlugRelatedGetOrCreateField(
        many=False,
        queryset=models.EmployeeAccount.objects.all(),
        slug_field='nickname'
    )
    chat = SlugRelatedGetOrCreateField(
        many=False,
        queryset=models.Chat.objects.all(),
        slug_field='source_chat_id'
    )

    class Meta:
        model = models.Message
        fields = ['id', 'timestamp', 'text', 'employee_account', 'chat', 'source_message_id', 'reply_source_message_id']
        extra_kwargs = {
            'timestamp': {'help_text': 'Время отправки сообщения'},
            'chat': {'help_text': 'Чат, в который пришло сообщение'},
            'text': {'help_text': 'Текст сообщения'},
            'employee_account': {'help_text': ''},
            'source_message_id': {'help_text': ''},
            'reply_source_message_id': {'help_text': ''},
        }

class ModelResponseStrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ModelResponseStrategy
        fields = ['id', '']


class GenerationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GenerationSettings
        fields = ['id', '']


class PeriodicTaskSerializer(serializers.ModelSerializer):
    interval = SlugRelatedGetOrCreateField(
        many=False,
        queryset=celery_beat.IntervalSchedule.objects.all(),
        slug_field='id'
    )

    class Meta:
        model = celery_beat.PeriodicTask
        fields = ['id', 'name', 'interval', 'task', 'kwargs', 'start_time']
        extra_kwargs = {
            'name': {'help_text': ''},
            'task': {'help_text': ''},
            'start_time': {'help_text': 'Время начала выполнения задачи'},
            'interval': {'help_text': ''},
            'kwargs': {'help_text': ''},
        }