from rest_framework import permissions


class IsLeaderOrReadOnlyForStaff(permissions.BasePermission):
    """
    Leaders can fully manage groups they lead. Staff/admin users can view
    (and, if is_staff, edit) everything -- useful for a church-wide
    coordinator role that needs to see all groups.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.leader_id == request.user.id
