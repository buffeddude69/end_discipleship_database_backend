from rest_framework import permissions, viewsets

from .models import Group
from .permissions import IsLeaderOrReadOnlyForStaff
from .serializers import GroupSerializer


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated, IsLeaderOrReadOnlyForStaff]

    def get_queryset(self):
        user = self.request.user
        qs = Group.objects.select_related("leader").prefetch_related("memberships")
        if not user.is_staff:
            qs = qs.filter(leader=user)

        leader_id = self.request.query_params.get("leader")
        if leader_id:
            qs = qs.filter(leader_id=leader_id)

        return qs

    def perform_create(self, serializer):
        # Staff can create a group on behalf of any leader (by passing
        # "leader": <id> in the request). Everyone else always becomes
        # the leader of the group they create.
        user = self.request.user
        if user.is_staff and serializer.validated_data.get("leader"):
            serializer.save()
        else:
            serializer.save(leader=user)
