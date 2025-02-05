
from django.urls import path

from manager_app.views import (ModelResponseListView, ModelResponseDetailView,
    # NoteListView, NoteDetailView, \
                               MessageListView, LlamaTestView)

urlpatterns = [
    path("summary/", ModelResponseListView.as_view(), name="summary-list"),
    path("test-view/", LlamaTestView.as_view(), name="test-view"),
    path("summary-detail/", ModelResponseDetailView.as_view(), name="summary-detail"),
    # path("note/", NoteListView.as_view(), name="note-list"),
    # path("note-detail/", NoteDetailView.as_view(), name="note-detail"),
    path("message/", MessageListView.as_view(), name="message-list"),
  # path('db_status/', views.db_status, name='db_status'),
  # path('build_db/', views.build_db, name='build_db'),
]