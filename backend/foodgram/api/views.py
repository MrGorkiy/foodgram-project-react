from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action, api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from recipe.models import (Favorite, Follow, Ingredient, Recipe, ShoppingCart,
                           Tag, User)
from .download_shopping_cart import download_shopping_cart
from .filters import IngredientFilter, RecipeFilter
from .permissions import ReadOnly
from .serializers import (
    CustomUserSerializer,
    FavoriteSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeCreatySerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer,
    TokenSerializer,
    UserCustomCreateSerializer,
    UserPasswordSerializer,
)


class FollowViewSet(viewsets.ModelViewSet):
    """Получение подписок пользователя"""

    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (
        IsAuthenticated,
        ReadOnly,
    )

    def get_queryset(self):
        review = Follow.objects.filter(user=self.request.user)
        return review

    def get_serializer_context(self):
        context = super(FollowViewSet, self).get_serializer_context()
        followers = Follow.objects.all()
        context.update({"follow": followers})
        return context


class RecipesViewSet(viewsets.ModelViewSet):
    """
    Создание, удаление, редактирование рецептов.
    Добавление, удаление подписок.
    Добавление, удаление, скачивание списка покупок.
    """

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ["create", "partial_update"]:
            return RecipeCreatySerializer
        elif self.action == "favorite":
            return FavoriteSerializer
        elif self.action == "shopping_cart":
            return ShoppingCartSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        context = super(RecipesViewSet, self).get_serializer_context()
        followers = Follow.objects.all()
        favorite = Favorite.objects.all()
        shopping_cart = ShoppingCart.objects.all()
        context.update(
            {
                "follow": followers,
                "favorite": favorite,
                "shopping_cart": shopping_cart,
            }
        )
        return context

    @action(
        detail=True,
        url_path="favorite",
        methods=["post", "delete"],
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        """Добавляет и удаляет рецепты в избранное."""
        if request.method == "POST":
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                recipe = Recipe.objects.get(pk=pk)
                if Favorite.objects.filter(recipe=recipe, user=request.user):
                    return Response(
                        {"errors": "Рецепт уже добавлен в избранное"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                serializer.save(user=self.request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        elif request.method == "DELETE":
            favorite = Favorite.objects.filter(recipe=pk, user=request.user)
            if favorite:
                favorite.delete()
                return Response(
                    {"message": f"Рецепт {pk} удален из избранного"},
                    status=status.HTTP_204_NO_CONTENT,
                )
            return Response(
                {"errors": "Рецепт не добавлен в избранное"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=True,
        url_path="shopping_cart",
        methods=["post", "delete"],
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Добавляет и удаляет рецепты в список покупок."""
        if request.method == "POST":
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                recipe = Recipe.objects.get(pk=pk)
                if ShoppingCart.objects.filter(recipe=recipe,
                                               user=request.user):
                    return Response(
                        {"errors": "Рецепт уже добавлен в список покупок"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                serializer.save(user=self.request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        elif request.method == "DELETE":
            recipe = Recipe.objects.get(pk=pk)
            shopping_cart = ShoppingCart.objects.filter(
                recipe=recipe, user=request.user
            )
            if shopping_cart:
                shopping_cart.delete()
                return Response(
                    {"message": f"Рецепт {pk} удален из списка покупок"},
                    status=status.HTTP_204_NO_CONTENT,
                )
            return Response(
                {"errors": "Рецепт не добавлен в список покупок"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Качаем список покупок."""
        return download_shopping_cart(self.request.user)


class IngredientViewSet(viewsets.ModelViewSet):
    """Чтение ингридиентов и фильтрация."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (ReadOnly,)
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    """Чтение тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None

    permission_classes = (ReadOnly,)


class CustomUserViewSet(UserViewSet):
    """
    Создание, получение списка пользователей.
    Создание и удаление подписки.
    """

    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitOffsetPagination
    serializer_class = CustomUserSerializer

    def get_serializer_context(self):
        context = super(UserViewSet, self).get_serializer_context()
        followers = Follow.objects.all()
        context.update({"follow": followers})
        return context

    def get_serializer_class(self):
        if self.action == "subscribe":
            return FollowSerializer
        if self.request.method.lower() == "post":
            return UserCustomCreateSerializer
        return CustomUserSerializer

    def perform_create(self, serializer):
        serializer.save(password=self.request.data["password"])

    @action(
        detail=True,
        url_path="subscribe",
        methods=["post", "delete"],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id=None):
        """Добавляет и удаляет пользователей в подписчики."""
        if request.method == "POST":
            author = get_object_or_404(User, pk=id)
            if request.user.id == int(id):
                return Response(
                    {"errors": "На самого себя не подписаться!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if request.user.follower.filter(user=author).exists():
                return Response(
                    {"errors": "Уже подписан!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            subs = request.user.follower.create(author=author)
            serializer = self.get_serializer(subs)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == "DELETE":
            user = request.user
            author = get_object_or_404(User, pk=id)
            follow = Follow.objects.filter(user=user, author=author)
            if follow:
                follow.delete()
                return Response(
                    {"message": "Вы отписались!"},
                    status=status.HTTP_204_NO_CONTENT,
                )
            return Response(
                {"errors": "Подписка отсутствует!"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class AuthToken(ObtainAuthToken):
    """Авторизация пользователя."""

    serializer_class = TokenSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"auth_token": token.key},
                        status=status.HTTP_201_CREATED)


@api_view(["post"])
def set_password(request):
    """Изменение пароля."""
    serializer = UserPasswordSerializer(data=request.data,
                                        context={"request": request})
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Пароль изменен!"},
                        status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
