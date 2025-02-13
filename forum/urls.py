from django.urls import path
from .views import (
    ForumListCreateView, 
    ForumRetrieveUpdateDestroyView,
    ForumMemberView,
    ForumMemberViewSet,
    MessageListCreateView,
    MessageRetrieveUpdateDestroyView
)

app_name = 'forum'

urlpatterns = [
    path('forums/', ForumListCreateView.as_view(), name='forum-list-create'),
    path('forums/<int:pk>/', ForumRetrieveUpdateDestroyView.as_view(), 
         name='forum-retrieve-update-destroy'),
    path('forums/<int:forum_pk>/members/', ForumMemberView.as_view(), 
         name='forum-member-add'),
    path('forums/<int:forum_pk>/members/<int:member_pk>/', 
         ForumMemberViewSet.as_view(), name='forum-member-detail'),
    path('forums/<int:forum_pk>/messages/', MessageListCreateView.as_view(), name='forum-messages'),
    path('forums/<int:forum_pk>/messages/<int:pk>/', MessageRetrieveUpdateDestroyView.as_view(), name='forum-message-detail'),
]