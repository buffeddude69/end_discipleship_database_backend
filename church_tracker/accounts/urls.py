from django.urls import path

from .views import LeaderDetailView, LeaderListView, LoginView, MeView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", MeView.as_view(), name="me"),
    path("leaders/", LeaderListView.as_view(), name="leader-list"),
    path("leaders/<int:pk>/", LeaderDetailView.as_view(), name="leader-detail"),
]
