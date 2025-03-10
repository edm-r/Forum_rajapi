from rest_framework import generics, status
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.conf import settings
import requests

from .models import Forum, ForumMember, Message
from .serializers import (
    ForumSerializer, 
    ForumDetailSerializer, 
    ForumMemberSerializer,
    SimpleMemberSerializer,
    MessageSerializer
)
from .permissions import IsForumOwner, IsForumActiveMember, IsMessageAuthor
from .authentication import MicroserviceTokenAuthentication

class ForumListCreateView(generics.ListCreateAPIView):
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer
    authentication_classes = [MicroserviceTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        forum = serializer.save(created_by=self.request.user)
        
        # Ajouter automatiquement le créateur comme membre modérateur
        ForumMember.objects.create(
            user=self.request.user,
            forum=forum,
            role='moderator',
            status='active'
        )

class ForumRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Forum.objects.all()
    authentication_classes = [MicroserviceTokenAuthentication]
    permission_classes = [IsAuthenticated, IsForumOwner]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ForumDetailSerializer
        return ForumSerializer

class ForumMemberView(generics.CreateAPIView):
    serializer_class = ForumMemberSerializer
    authentication_classes = [MicroserviceTokenAuthentication]
    permission_classes = [IsAuthenticated, IsForumOwner]

    def get_forum(self):
        return get_object_or_404(Forum, pk=self.kwargs['forum_pk'])

    def perform_create(self, serializer):
        forum = self.get_forum()
        email = serializer.validated_data.pop('email')
        base_url = settings.URL_B
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            auth_header = self.request.headers.get('Authorization')
            headers = {'Authorization': auth_header}
            
            response = requests.get(
                base_url,
                params={'email': email},
                headers=headers
            )
            if response.status_code != 200:
                raise serializers.ValidationError({
                    "code": "USER_NOT_FOUND",
                    "detail": "L'utilisateur n'existe pas."
                })
            
            user_data = response.json()
            user = User.objects.create(
                username=user_data['username'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )
        
        if ForumMember.objects.filter(user=user, forum=forum).exists():
            raise serializers.ValidationError({
                "code": "USER_ALREADY_MEMBER",
                "detail": "L'utilisateur est déjà membre de ce forum."
            })
        
        serializer.save(forum=forum, user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class ForumMemberViewSet(generics.GenericAPIView):
    serializer_class = SimpleMemberSerializer
    authentication_classes = [MicroserviceTokenAuthentication]
    permission_classes = [IsAuthenticated, IsForumOwner]

    def get_forum(self):
        return get_object_or_404(Forum, pk=self.kwargs['forum_pk'])

    def get_member(self):
        forum = self.get_forum()
        return get_object_or_404(ForumMember, 
                               forum=forum, 
                               id=self.kwargs['member_pk'])

    def delete(self, request, *args, **kwargs):
        member = self.get_member()
        member.status = 'inactive'
        member.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    authentication_classes = [MicroserviceTokenAuthentication]
    permission_classes = [IsAuthenticated, IsForumActiveMember]
    
    def get_forum(self):
        return get_object_or_404(Forum, pk=self.kwargs['forum_pk'])
    
    def get_queryset(self):
        forum = self.get_forum()
        return Message.objects.filter(forum=forum)
    
    def perform_create(self, serializer):
        forum = self.get_forum()
        serializer.save(author=self.request.user, forum=forum)

class MessageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MessageSerializer
    authentication_classes = [MicroserviceTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_forum(self):
        return get_object_or_404(Forum, pk=self.kwargs['forum_pk'])
    
    def get_queryset(self):
        forum = self.get_forum()
        return Message.objects.filter(forum=forum)
    
    def perform_update(self, serializer):
        serializer.save(is_edited=True)
        
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsMessageAuthor()]
        return [IsAuthenticated(), IsForumActiveMember()]