from rest_framework import permissions


class IsLeaderOrReadOnlyForStaff(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.leader_id == request.user.id
