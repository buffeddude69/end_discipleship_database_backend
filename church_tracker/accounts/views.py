from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from .serializers import UserRegistrationSerializer, UserSerializer

User = get_user_model()


class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class RegisterView(generics.CreateAPIView):
    """Public endpoint for a new group leader to create their account."""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(id=response.data["id"])
        token, _ = Token.objects.get_or_create(user=user)
        response.data["token"] = token.key
        return response


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


class LeaderListView(generics.ListAPIView):
    """
    Staff-only: list every leader account, so a coordinator can see
    who's who and assign/filter groups by leader.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaff]

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
