from rest_framework import generics, status
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import requests

from .models import Forum, ForumMember
from .serializers import (
    ForumSerializer, 
    ForumDetailSerializer, 
    ForumMemberSerializer,
    SimpleMemberSerializer
)
from .permissions import IsForumOwner
from .authentication import MicroserviceTokenAuthentication

class ForumListCreateView(generics.ListCreateAPIView):
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer
    authentication_classes = [MicroserviceTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

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
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            auth_header = self.request.headers.get('Authorization')
            headers = {'Authorization': auth_header}
            
            response = requests.get(
                'https://rajapi-cop-auth-api-33be22136f5e.herokuapp.com/auth/profile/',
                params={'email': email},
                headers=headers
            )
            user_data = response.json()
            
            user = User.objects.create(
                username=user_data['username'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )
        
        if ForumMember.objects.filter(user=user, forum=forum).exists():
            raise serializers.ValidationError("L'utilisateur est déjà membre de ce forum")
        
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