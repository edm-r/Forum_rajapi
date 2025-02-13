from django.urls import path
from .views import ForumListCreateView, ForumRetrieveUpdateDestroyView

urlpatterns = [
    path('forums/', ForumListCreateView.as_view(), name='forum-list-create'),
    path('forums/<int:pk>/', ForumRetrieveUpdateDestroyView.as_view(), name='forum-retrieve-update-destroy'),
]