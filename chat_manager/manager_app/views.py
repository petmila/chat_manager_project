import datetime
import json

from django.http import JsonResponse
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

import utils.saiga_model
import utils.text_preprocess
import django_celery_beat.models as celery_beat
import utils.saiga_llm_chain
from utils.text_preprocess import preprocess
from manager_app import models, serializers
from rest_framework import generics, status
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiTypes

from manager_app.models import EmployeeAccount


@extend_schema(tags=["Сотрудники"])
class EmployeeListView(generics.ListCreateAPIView):
    permission_classes = (IsAdminUser,)
    queryset = models.Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer


@extend_schema(tags=["Сотрудники"])
class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAdminUser,)
    queryset = models.Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer


@extend_schema(tags=["Сотрудники"])
class EmployeeAccountListView(generics.ListCreateAPIView):
    permission_classes = (IsAdminUser,)
    queryset = models.EmployeeAccount.objects.all()
    serializer_class = serializers.EmployeeAccountSerializer


@extend_schema(tags=["Сотрудники"])
class EmployeeAccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAdminUser,)
    lookup_field = 'nickname'
    queryset = models.EmployeeAccount.objects.all()
    serializer_class = serializers.EmployeeAccountSerializer


@extend_schema(tags=["Сообщения"])
class MessageListView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
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


class MessagesByDateView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.MessageSerializer

    @extend_schema(
        tags=["Сообщения"],
        description="Фильтрация сообщений по дате",
        parameters=[
            OpenApiParameter(name='date', type=str, location=OpenApiParameter.PATH, description='Дата'),
        ],
        responses={200: OpenApiTypes.OBJECT}
    )
    def get(self, request, date):
        messages = models.Message.objects.filter(timestamp=date).order_by('timestamp')
        return Response(messages)


@extend_schema(tags=["Сообщения"])
class MessageDetailView(generics.DestroyAPIView):
    permission_classes = (IsAdminUser,)
    queryset = models.Message.objects.all()
    serializer_class = serializers.MessageSerializer


@extend_schema(tags=["Резюме"])
class ModelResponseListView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = models.ModelResponse.objects.all()
    serializer_class = serializers.ModelResponseSerializer

    def create(self, request, *args, **kwargs):
        chat = models.Chat.objects.filter(source_chat_id=request.data['source_chat_id']).first()
        first_date = request.data['first_date']
        last_date = request.data['last_date']
        messages = models.Message.objects.filter(chat=chat,
                                                 timestamp__range=(first_date, last_date)).order_by('timestamp')
        data = utils.perform_summary.perform_summary(messages=messages, chat_id=chat.id)

        serializer = serializers.ModelResponseSerializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError:
            return Response({"errors": (serializer.errors,)},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data, status=status.HTTP_200_OK)


class ModelResponseByDateView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ModelResponseSerializer

    @extend_schema(
        tags=["Резюме"],
        description="Фильтрация резюме по дате",
        parameters=[
            OpenApiParameter(name='date', type=str, location=OpenApiParameter.PATH, description='Дата'),
        ],
        responses={200: OpenApiTypes.OBJECT}
    )
    def get(self, request, date):
        messages = models.ModelResponse.objects.filter(date=date).order_by('timestamp')
        return Response(messages)


@extend_schema(tags=["Резюме"])
class ModelResponseDetailView(generics.DestroyAPIView):
    permission_classes = (IsAdminUser,)
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


@extend_schema(tags=["Чаты"])
class ChatListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ChatSerializer
    queryset = models.Chat.objects.all()


@extend_schema(tags=["Чаты"])
class ChatDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAdminUser,)
    lookup_field = 'name'
    queryset = models.Chat.objects.all()
    serializer_class = serializers.ChatSerializer


@extend_schema(tags=["Резюме"])
class ModelResponseDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = models.ModelResponse.objects.all()
    lookup_field = 'date'
    serializer_class = serializers.ModelResponseSerializer


class ChatsByEmployeeNicknameView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Чаты"],
        summary="Чаты по нику сотрудника",
        description="Возвращает список ID чатов, связанных с сотрудником.",
        parameters=[
            OpenApiParameter(name='nickname', type=str, location=OpenApiParameter.PATH, description='Ник сотрудника'),
        ],
        responses={200: OpenApiTypes.OBJECT}
    )
    def get(self, request, nickname):
        employee = get_object_or_404(EmployeeAccount, nickname=nickname)
        messages = models.Message.objects.filter(employee_account=employee).order_by('timestamp')
        chat_data = {}
        for message in messages:
            chat_data[message.chat.name] = message.chat.source_chat_id

        return Response(chat_data)


@extend_schema(tags=["Автоматизированные генерации"])
class PeriodicTaskView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = celery_beat.PeriodicTask.objects.all()
    serializer_class = serializers.PeriodicTaskSerializer

    def create(self, request, *args, **kwargs):
        request.data["kwargs"]["content_chat"] = models.Chat.objects.get(
            source_chat_id=request.data["kwargs"]["content_chat"]).id
        request.data["kwargs"] = json.dumps((request.data["kwargs"]))
        serializer = serializers.PeriodicTaskSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError:
            return Response({"errors": (serializer.errors,)},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(request.data, status=status.HTTP_200_OK)


@extend_schema(tags=["Автоматизированные генерации"])
class PeriodicTaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    lookup_field = 'name'
    queryset = celery_beat.PeriodicTask.objects.all()
    serializer_class = serializers.PeriodicTaskSerializer


class LlamaTestView(TemplateView):
    def post(self, request, **kwargs):
        model = utils.saiga_llm_chain.SaigaModel()
        result = model.interact(request.POST['text'])
        return JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False})
