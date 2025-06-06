import datetime

from django import db
from django.test import TestCase
from rest_framework.generics import get_object_or_404

from manager_app.models import Chat, EmployeeAccount, Message, ChatSource


class ChatTestCase(TestCase):
    @classmethod
    def setUp(cls):
        EmployeeAccount.objects.create(
            nickname="employee_1",
            source=ChatSource.telegram,
        )
        EmployeeAccount.objects.create(
            nickname="employee_2",
            source=ChatSource.mattermost,
        )
        Chat.objects.create(
            chat_source=ChatSource.telegram,
            source_chat_id=1342468259,
            name="chat_1",
        )
        Chat.objects.create(
            chat_source=ChatSource.mattermost,
            source_chat_id=1342468257,
            name="chat_2",
        )

    def test_get_chats_employee_nickname__no_messages_no_access_to_chat(self):
        """ """
        employee = get_object_or_404(EmployeeAccount, nickname="employee_1")
        messages = Message.objects.filter(employee_account=employee).order_by('timestamp')

        self.assertEqual(0, messages.count())

    def test_get_chats_employee_nickname__one_telegram_chat(self):
        """ """
        employee = get_object_or_404(EmployeeAccount, nickname="employee_1")
        chat_1 = Chat.objects.filter(name="chat_1").first()
        Message.objects.create(
            timestamp=datetime.datetime.now(),
            text="Test message",
            employee_account=employee,
            chat=chat_1,
            source_message_id=1342468345,
            reply_source_message_id=None,
        )

        messages = Message.objects.filter(employee_account=employee).order_by('timestamp')

        self.assertEqual("chat_1", messages.first().chat.name)
        self.assertEqual(1, messages.count())
        self.assertEqual(chat_1, messages.first().chat)

    def test_get_chats_employee_nickname__one_mattermost_chat(self):
        """ """
        employee = get_object_or_404(EmployeeAccount, nickname="employee_2")
        chat_2 = Chat.objects.filter(name="chat_2").first()
        Message.objects.create(
            timestamp=datetime.datetime.now(),
            text="Test message",
            employee_account=employee,
            chat=chat_2,
            source_message_id=1342468345,
            reply_source_message_id=None,
        )
        messages = Message.objects.filter(employee_account=employee).order_by('timestamp')

        self.assertEqual("chat_2", messages.first().chat.name)
        self.assertEqual(1, messages.count())
        self.assertEqual(chat_2, messages.first().chat)

    def test_create_chat__chat_created(self):
        """"""
        Chat.objects.create(
            chat_source=ChatSource.mattermost,
            source_chat_id=1342468220,
            name="chat_3",
        )
        chat = Chat.objects.filter(name="chat_3").first()
        self.assertEqual(ChatSource.mattermost, chat.chat_source)
        self.assertEqual('1342468220', chat.source_chat_id)

    def test_get_chat_by_source_chat_id(self):
        """"""
        chat = Chat.objects.filter(source_chat_id=1342468259).first()
        self.assertEqual("chat_1", chat.name)

    def test_delete_chat__chat_not_in_all_chats(self):
        """"""
        chat = Chat.objects.filter(source_chat_id=1342468259).first()
        chat.delete()
        self.assertNotIn(chat, Chat.objects.all())

    def test_delete_chat__all_chat_messages_deleted(self):
        """"""
        employee = get_object_or_404(EmployeeAccount, nickname="employee_2")
        chat_2 = Chat.objects.filter(name="chat_2").first()
        Message.objects.create(
            timestamp=datetime.datetime.now(),
            text="Test message",
            employee_account=employee,
            chat=chat_2,
            source_message_id=1342468345,
            reply_source_message_id=None,
        )
        messages = Message.objects.filter(chat=chat_2)
        chat_2.delete()
        self.assertNotIn(messages, Message.objects.all())

    def test_delete_chat__employee_account_not_deleted(self):
        """"""
        employee = get_object_or_404(EmployeeAccount, nickname="employee_2")
        chat_2 = Chat.objects.filter(name="chat_2").first()
        Message.objects.create(
            timestamp=datetime.datetime.now(),
            text="Test message",
            employee_account=employee,
            chat=chat_2,
            source_message_id=1342468345,
            reply_source_message_id=None,
        )
        chat_2.delete()
        self.assertIn(employee, EmployeeAccount.objects.all())
