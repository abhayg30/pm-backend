from django.urls import path, include
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileView,
    UserLogoutView,
    UpdateProfile,
)

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("update/profile/", UpdateProfile.as_view(), name="update-profile"),
    path("update/profile/", UpdateProfile.as_view(), name="update-profile"),
]
