
from django.urls import path

from manager_app.views import (ModelResponseListView, ModelResponseDetailView, PeriodicTaskView,
                               MessageListView, LlamaTestView, ChatListView, ChatsByEmployeeNicknameView)

urlpatterns = [
    path("summary/", ModelResponseListView.as_view(), name="summary-list"),
    path("chats/", ChatListView.as_view(), name="chat-list"),
    path('chats/by-nickname/<str:nickname>/', ChatsByEmployeeNicknameView.as_view(), name='chats_by_nickname'),
    path("test-view/", LlamaTestView.as_view(), name="test-view"),
    path("summary-detail/", ModelResponseDetailView.as_view(), name="summary-detail"),
    path("periodic-task/", PeriodicTaskView.as_view(), name="periodic-task-list"),
    # path("note-detail/", NoteDetailView.as_view(), name="note-detail"),
    path("message/", MessageListView.as_view(), name="message-list"),
  # path('db_status/', views.db_status, name='db_status'),
  # path('build_db/', views.build_db, name='build_db'),
]