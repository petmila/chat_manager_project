import json
import datetime

import rest_framework.permissions
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import TemplateView
from rest_framework.decorators import permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import llm_models.saiga_model
import llm_models.text_preprocess
import llm_models.saiga_llm_chain
from llm_models.text_preprocess import preprocess
from manager_app import models, serializers
from manager_app.saiga_model import interact
from django.http import HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status


class EmployeeListView(generics.ListCreateAPIView):
    # permission_classes = (IsAuthenticated, )
    queryset = models.Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer


class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = (IsAuthenticated,)
    queryset = models.Employee.objects.all()
    lookup_field = 'credentials.nickname'
    serializer_class = serializers.EmployeeSerializer

class MessageListView(generics.ListCreateAPIView):
    # permission_classes = (IsAuthenticated, )
    queryset = models.Message.objects.all()
    serializer_class = serializers.MessageSerializer

    def create(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
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
    # permission_classes = (IsAuthenticated,)
    queryset = models.Message.objects.all()
    # lookup_field = 'credentials.nickname'
    serializer_class = serializers.MessageSerializer

class ModelResponseListView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = models.ModelResponse.objects.all()
    serializer_class = serializers.ModelResponseSerializer

    def create(self, request, *args, **kwargs):
        """
        :param request:
            source_chat_id -
            # time_period -
        :param args:
        :param kwargs:
        :return:
        """
        # datetime_ = request.data['time_period']
        chat = models.Chat.objects.filter(source_chat_id=request.data['source_chat_id']).first()
        messages = models.Message.objects.filter(chat=chat)
        queryset = [
            str(message)
            if message.reply_source_message_id is None
            else models.Message.objects.filter(source_message_id=message.reply_source_message_id).first()
            for message in messages
        ]
        model = llm_models.saiga_model.SaigaModel()
        result = model.interact(
            f"Сделай тезисное резюме информации в данном диалоге из корпоративного чата: {queryset} \n Резюме:")
        data = {'text': result, 'date': datetime.date.today(), 'chat': chat.id}
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

# class NoteListView(generics.ListCreateAPIView):
#     permission_classes = (IsAuthenticated, )
#     queryset = models.Note.objects.all()
#     serializer_class = serializers.NoteSerializer
#
# class NoteDetailView(generics.RetrieveUpdateDestroyAPIView):
#     permission_classes = (IsAuthenticated,)
#     queryset = models.Note.objects.all()
#     lookup_field = ''
#     serializer_class = serializers.NoteSerializer

#
# class HashTagListView(generics.ListAPIView):
#     permission_classes = (IsAuthenticated, )
#     queryset = models.HashTag.objects.all()
#     serializer_class = serializers.HashTagSerializer


class ModelResponseStrategyListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = models.ModelResponseStrategy.objects.all()
    serializer_class = serializers.ModelResponseStrategySerializer


class GenerationSettingsListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = models.GenerationSettings.objects.all()
    serializer_class = serializers.GenerationSettingsSerializer

class LlamaTestView(TemplateView):
    def post(self, request, **kwargs):
        model = llm_models.saiga_llm_chain.SaigaModel()
        result = model.interact(request.POST['text'])
        return JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False})
