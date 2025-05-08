from django.urls import path
from manager_app.views import (ModelResponseListView, ModelResponseDetailView, PeriodicTaskView,
                               MessageListView, EmployeeListView, EmployeeAccountListView, EmployeeDetailView,
                               EmployeeAccountDetailView, PeriodicTaskDetailView, ChatDetailView, MessageDetailView,
                                MessagesByChatView, MessagesByDateView, ChatsBySourceListView, ModelResponseByDateView, 
                                LlamaTestView, ChatListView, ChatsByEmployeeNicknameView)

urlpatterns = [
    path("summary/", ModelResponseListView.as_view(), name="summary-list"),
    path("summary-delete/", ModelResponseDetailView.as_view(), name="summary-delete"),
    path("summary/by-date/<str:date>/", ModelResponseByDateView.as_view(), name="summary_by_date"),

    path("chats/", ChatListView.as_view(), name="chat-list"),
    path('chats/by-nickname/<str:nickname>/', ChatsByEmployeeNicknameView.as_view(), name='chats_by_nickname'),
    path('chats/by-source/<str:source>/', ChatsBySourceListView.as_view(), name='chats_by_source'),
    path("chats-detail/", ChatDetailView.as_view(), name="chats-detail"),
    path("chats-detail/by-source-id/<str:source_id>/", ChatDetailView.as_view(), name="chats-detail-source"),

    path("employee/", EmployeeListView.as_view(), name="employee-list"),
    path("employee-detail/", EmployeeDetailView.as_view(), name="employee-detail"),
    path("employee-account/", EmployeeAccountListView.as_view(), name="employee-account-list"),
    path("employee-account-detail/<str:nickname>/", EmployeeAccountDetailView.as_view(), name="employee-account-detail"),

    path("periodic-task/", PeriodicTaskView.as_view(), name="periodic-task-list"),
    path("periodic-task-detail/<str:name>/", PeriodicTaskDetailView.as_view(), name="periodic-task-detail"),

    path("message/", MessageListView.as_view(), name="message-list"),
    path("message-delete/", MessageDetailView.as_view(), name="message-delete"),
    path("message/by-date/<str:date>/", MessagesByDateView.as_view(), name="message_by_date"),
    path("message/by-chat/<int:chat_id>/", MessagesByChatView.as_view(), name="message_by_chat"),

    path("test-view/", LlamaTestView.as_view(), name="test-view")
]
