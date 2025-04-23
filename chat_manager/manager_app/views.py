import datetime

from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views import View
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import llm_models.saiga_model
import llm_models.text_preprocess
import django_celery_beat.models as celery_beat
import llm_models.saiga_llm_chain
from llm_models.text_preprocess import preprocess
from manager_app import models, serializers
from rest_framework import generics, status

from manager_app.models import EmployeeAccount


class EmployeeListView(generics.ListCreateAPIView):
    queryset = models.Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer


class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer


class MessageListView(generics.ListCreateAPIView):
    queryset = models.Message.objects.all()
    serializer_class = serializers.MessageSerializer

    def create(self, request, *args, **kwargs):
        is_employee_in_this_chat: bool = False
        account = models.EmployeeAccount.objects.filter(nickname=request.data['forward_from']).first()
        # message is forwarded
        if account is not None:
            messages = models.Message.objects.filter(employee_account=account).order_by('timestamp')
            for message in messages:
                if str(message.chat.source_chat_id) == str(request.data['chat']['source_chat_id']):
                    is_employee_in_this_chat = True
            if is_employee_in_this_chat:
                request.data['employee_account']['nickname'] = request.data['forward_from']
            else:
                request.data['text'] = 'согласно словам ' + request.data['forward_from'] + ' ' + request.data['text']
        request.data['text'] = preprocess(request.data['text'])
        serializer = serializers.MessageSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError:
            return Response({"errors": (serializer.errors,)},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(request.data, status=status.HTTP_200_OK)


class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Message.objects.all()
    serializer_class = serializers.MessageSerializer


class ModelResponseListView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = models.ModelResponse.objects.all()
    serializer_class = serializers.ModelResponseSerializer

    def create(self, request, *args, **kwargs):
        first_date = request.data['first_date']
        last_date = request.data['last_date']
        chat = models.Chat.objects.filter(source_chat_id=request.data['source_chat_id']).first()

        messages = models.Message.objects.filter(chat=chat,
                                                 timestamp__range=(first_date, last_date)).order_by('timestamp')
        queryset = [
            str(message)
            # if message.reply_source_message_id is None
            # else str(message) + str(
            #     models.Message.objects.filter(source_message_id=message.reply_source_message_id).first())
            for message in messages
        ]

        print('-'.join(queryset))

        model = llm_models.saiga_llm_chain.SaigaModel()
        result = model.interact('-'.join(queryset))

        data = {
            'text': result,
            'date': datetime.date.today(), 'chat': chat.id}
        serializer = serializers.ModelResponseSerializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError:
            return Response({"errors": (serializer.errors,)},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data, status=status.HTTP_200_OK)


class ModelResponseDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = models.ModelResponse.objects.all()
    lookup_field = 'date'
    serializer_class = serializers.ModelResponseSerializer


class ModelResponseStrategyListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = models.ModelResponseStrategy.objects.all()
    serializer_class = serializers.ModelResponseStrategySerializer


class GenerationSettingsListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = models.GenerationSettings.objects.all()
    serializer_class = serializers.GenerationSettingsSerializer


class ChatListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ChatSerializer
    queryset = models.Chat.objects.all()


class ChatsByEmployeeNicknameView(View):
    def get(self, request, nickname):
        employee = get_object_or_404(EmployeeAccount, nickname=nickname)
        messages = models.Message.objects.filter(employee_account=employee).order_by('timestamp')
        chat_data = {}
        for message in messages:
            chat_data[message.chat.name] = message.chat.source_chat_id

        return JsonResponse(chat_data, safe=False)

class PeriodicTaskView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = celery_beat.PeriodicTask.objects.all()
    serializer_class = serializers.PeriodicTaskSerializer

    def create(self, request, *args, **kwargs):
        request.data['kwargs']['content_chat'] = models.Chat.objects.get(source_chat_id=request.data['kwargs']['content_chat']).id
        request.data['kwargs'] = str(request.data['kwargs'])
        serializer = serializers.PeriodicTaskSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError:
            return Response({"errors": (serializer.errors,)},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(request.data, status=status.HTTP_200_OK)

class LlamaTestView(TemplateView):
    def post(self, request, **kwargs):
        model = llm_models.saiga_llm_chain.SaigaModel()
        result = model.interact(request.POST['text'])
        return JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False})
