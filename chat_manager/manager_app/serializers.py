from rest_framework import serializers
from manager_app import models


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Chat
        fields = ['id', 'chat_source', 'source_chat_id', 'name']


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


class EmployeeSerializer(serializers.ModelSerializer):
    accounts = SlugRelatedGetOrCreateField(
        many=True,
        queryset=models.EmployeeAccount.objects.all(),
        slug_field='name'
    )
    class Meta:
        model = models.Employee
        fields = ['id', 'name', 'surname', 'accounts']


class ModelResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ModelResponse
        fields = ['id', 'date', 'chat', 'text']

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


class ModelResponseStrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ModelResponseStrategy
        fields = ['id', '']

class GenerationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GenerationSettings
        fields = ['id', '']

class TaskScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TaskSchedule
        fields = ['id', 'content_chat', 'source_chat_id',
                  'next_run_time', 'time_period_in_hours',
                  'interval_hours', 'timestamp']
