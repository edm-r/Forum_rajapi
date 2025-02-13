from rest_framework import permissions

class IsForumOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user

    def has_permission(self, request, view):
        if 'forum_pk' in view.kwargs:
            forum = view.get_forum()
            return forum.created_by == request.user
        return True