import datetime

from django.http import JsonResponse
from django.views.generic import TemplateView
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import llm_models.saiga_model
import llm_models.text_preprocess
import llm_models.saiga_llm_chain
from llm_models.text_preprocess import preprocess
from manager_app import models, serializers
from rest_framework import generics, status


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
        datetime_ = request.data['time_period']
        chat = models.Chat.objects.filter(source_chat_id=request.data['source_chat_id']).first()
        messages = models.Message.objects.filter(chat=chat, timestamp__day=datetime_).order_by('timestamp')
        queryset = [
            str(message)
            if message.reply_source_message_id is None
            else str(message) + str(
                models.Message.objects.filter(source_message_id=message.reply_source_message_id).first())
            for message in messages
        ]

        print('-'.join(queryset))

        # model = llm_models.saiga_llm_chain.SaigaModel()
        # result = model.interact('-'.join(queryset))
        #
        #
        data = {
            # 'text': result,
            'date': datetime.date.today(), 'chat': chat.id}
        # serializer = serializers.ModelResponseSerializer(data=data)
        # try:
        #     serializer.is_valid(raise_exception=True)
        #     serializer.save()
        # except ValidationError:
        #     return Response({"errors": (serializer.errors,)},
        #                     status=status.HTTP_400_BAD_REQUEST)
        # else:
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


class LlamaTestView(TemplateView):
    def post(self, request, **kwargs):
        model = llm_models.saiga_llm_chain.SaigaModel()
        result = model.interact(request.POST['text'])
        return JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False})
