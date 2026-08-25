from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from .serializers import ChangePasswordSerializer, UserRegistrationSerializer, UserSerializer

User = get_user_model()


class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class RegisterView(generics.CreateAPIView):
    """
    Staff-only endpoint for creating a new leader account. This app is
    for internal organization use, so accounts aren't self-service --
    a staff/coordinator creates each leader's account for them.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        # Respond with the same {token, user} shape as /login/, using the
        # full UserSerializer (not the registration-input serializer) --
        # otherwise the frontend's in-memory user object is missing fields
        # like groups_led/school_name until the next page load re-fetches it.
        return Response(
            {"token": token.key, "user": UserSerializer(user).data},
            status=201,
        )


class LoginView(ObtainAuthToken):
    """Returns an auth token plus basic profile info on login."""

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user": UserSerializer(user).data,
        })


class MeView(generics.RetrieveUpdateAPIView):
    """The logged-in leader's own profile."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.GenericAPIView):
    """
    Lets a logged-in leader change their own password -- e.g. after
    staff creates their account with a temporary one. Also rotates
    their auth token, so any old copy of it (e.g. a temp password
    shared insecurely) stops working immediately.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save()

        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)

        return Response({"token": token.key, "detail": "Password changed successfully."})


class LeaderListView(generics.ListAPIView):
    """
    Any authenticated leader can list/search leader accounts -- needed
    so a leader can find and add another leader to their group's
    roster (common for leadership groups). Staff additionally get to
    use this to assign group ownership.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = User.objects.all().order_by("first_name", "last_name")

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(username__icontains=search)
            )

        leader_role = self.request.query_params.get("leader_role")
        if leader_role:
            qs = qs.filter(leader_role=leader_role)

        return qs


class LeaderDetailView(generics.RetrieveAPIView):
    """Any authenticated leader can view another leader's profile."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
