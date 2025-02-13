from rest_framework import permissions
from .models import ForumMember
class IsForumOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user

    def has_permission(self, request, view):
        if 'forum_pk' in view.kwargs:
            forum = view.get_forum()
            return forum.created_by == request.user
        return True

class IsForumActiveMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if 'forum_pk' in view.kwargs:
            forum = view.get_forum()
            
            # Vérifier si l'utilisateur est le créateur du forum
            if forum.created_by == request.user:
                return True
                
            # Vérifier si l'utilisateur est un membre actif
            return ForumMember.objects.filter(
                user=request.user,
                forum=forum,
                status='active'
            ).exists()
        return False

class IsForumActiveMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if 'forum_pk' in view.kwargs:
            forum = view.get_forum()
            return ForumMember.objects.filter(
                user=request.user,
                forum=forum,
                status='active'
            ).exists()
        return False

class IsMessageAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user