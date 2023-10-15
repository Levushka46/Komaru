from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet, basename="user")

urlpatterns = [
    path("users/login/", views.LoginJWTView.as_view(), name="token_obtain_pair"),
    path("users/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/friends/", views.FriendListViewSet.as_view({"get": "list"}), name="user_friend_list"),
    path(
        "users/profile/<str:username>/",
        views.UserProfileViewSet.as_view({"get": "retrieve", "patch": "partial_update", "put": "update"}),
        name="user_profile",
    ),
    path("users/friend/<str:username>/", views.FriendView.as_view(), name="user_friend"),
    path("users/unfriend/<str:username>/", views.UnFriendView.as_view(), name="user_unfriend"),
    path("", include(router.urls)),
]
