from django.urls import include, path
from django.urls import re_path
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework import routers
from django.contrib.auth import get_user_model

from .views import (
    RecipesViewSet,
    TagViewSet,
    CustomUserViewSet,
    IngredientViewSet,
    FollowViewSet,
    set_password,
    # GetTokenView,
    AuthToken,
)

app_name = 'api'

router_v1 = routers.DefaultRouter()
# router_v1.register(r"users", UserViewSet, basename="users")
router_v1.register(r"recipes", RecipesViewSet, basename="recipes")
router_v1.register(r"tags", TagViewSet, basename="tags")
router_v1.register('users/subscriptions', FollowViewSet)
router_v1.register("users", CustomUserViewSet)
router_v1.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('users/set_password/', set_password, name='set_password'),
    path(
        'auth/token/login/',
        AuthToken.as_view(),
        name='login'),
    path("", include(router_v1.urls)),
    path('', include('djoser.urls')),
    # re_path(r"^auth/token/login/?$", TokenCreateView.as_view(), name="login"),
    re_path(r"^auth/token/logout/?$", TokenDestroyView.as_view(), name="logout"),
    path('auth/', include('djoser.urls.authtoken')),
]

# User = get_user_model()
