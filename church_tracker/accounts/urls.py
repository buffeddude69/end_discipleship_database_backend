from django.urls import path

from .views import ChangePasswordView, LeaderDetailView, LeaderListView, LoginView, MeView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", MeView.as_view(), name="me"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("leaders/", LeaderListView.as_view(), name="leader-list"),
    path("leaders/<int:pk>/", LeaderDetailView.as_view(), name="leader-detail"),
]
