from django.urls import include, path, re_path
from djoser.views import TokenDestroyView
from rest_framework import routers

from .views import (
    AuthToken,
    CustomUserViewSet,
    FollowViewSet,
    IngredientViewSet,
    RecipesViewSet,
    TagViewSet,
    set_password,
)

app_name = "api"

router_v1 = routers.DefaultRouter()
router_v1.register("recipes", RecipesViewSet, basename="recipes")
router_v1.register("tags", TagViewSet, basename="tags")
router_v1.register("users/subscriptions", FollowViewSet)
router_v1.register("users", CustomUserViewSet)
router_v1.register("ingredients", IngredientViewSet)

urlpatterns = [
    path("users/set_password/", set_password, name="set_password"),
    path("auth/token/login/", AuthToken.as_view(), name="login"),
    path("", include(router_v1.urls)),
    path("", include("djoser.urls")),
    re_path(r"^auth/token/logout/?$", TokenDestroyView.as_view(),
            name="logout"),
    path("auth/", include("djoser.urls.authtoken")),
]
