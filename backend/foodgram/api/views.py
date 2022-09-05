import io

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.db.models import Count, Sum
from django.db.models.expressions import Exists, OuterRef, Value
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse
from djoser.views import UserViewSet
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, mixins, serializers, status, viewsets, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination,
)
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from recipe.models import User, Follow, Tag, Ingredient, IngredientRecipe, Recipe, Favorite, ShoppingCart
from .filters import IngredientFilter, RecipeFilter
from .pagination import CommentPagination
from .permissions import IsAdminOnly, IsAdminOrReadOnly, IsOwnerAdminModerator, ReadOnly
from .serializers import (
    CustomUserSerializer,
    RecipeSerializer,
    RecipeCreatySerializer,
    TagSerializer,
    IngredientSerializer,
    FavoriteSerializer,
    FollowSerializer,
    ShoppingCartSerializer,
    UserPasswordSerializer,
    UserCustomCreateSerializer,
    # GetTokenSerializer,
    TokenSerializer,
)

FILENAME = 'shoppingcart.pdf'


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        review = Follow.objects.filter(user=self.request.user)
        print("view", review)
        return review

    def get_serializer_context(self):
        context = super(FollowViewSet, self).get_serializer_context()
        followers = Follow.objects.all()
        context.update({"follow": followers})
        return context


class RecipesViewSet(viewsets.ModelViewSet):
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
        context.update({"follow": followers, "favorite": favorite, "shopping_cart": shopping_cart, })
        return context

    @action(
        detail=True,
        url_path="favorite",
        methods=["post", "delete"],
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        if request.method == "POST":
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                recipe = Recipe.objects.get(pk=pk)
                if Favorite.objects.filter(recipe=recipe, user=request.user):
                    return Response(
                        {"errors": "Рецепт уже добавлен в избранное"}, status=status.HTTP_400_BAD_REQUEST
                    )
                serializer.save(user=self.request.user, recipe=recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        elif request.method == "DELETE":
            favorite = Favorite.objects.filter(recipe=pk, user=request.user)
            if favorite:
                favorite.delete()
                return Response(
                    {"message": f"Рецепт {pk} удален из избранного"},
                    status=status.HTTP_204_NO_CONTENT,
                )
            return Response(
                {"errors": "Рецепт не добавлен в избранное"}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        url_path="shopping_cart",
        methods=["get", "post", "delete"],
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        if request.method == "GET":
            pass
        if request.method == "POST":
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                recipe = Recipe.objects.get(pk=pk)
                if ShoppingCart.objects.filter(recipe=recipe, user=request.user):
                    return Response(
                        {"errors": "Рецепт уже добавлен в список покупок"}, status=status.HTTP_400_BAD_REQUEST
                    )
                serializer.save(user=self.request.user, recipe=recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        elif request.method == "DELETE":
            recipe = Recipe.objects.get(pk=pk)
            shopping_cart = ShoppingCart.objects.filter(recipe=recipe, user=request.user)
            if shopping_cart:
                shopping_cart.delete()
                return Response(
                    {"message": f"Рецепт {pk} удален из списка покупок"},
                    status=status.HTTP_204_NO_CONTENT,
                )
            return Response(
                {"errors": "Рецепт не добавлен в список покупок"}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Качаем список с ингредиентами."""

        buffer = io.BytesIO()
        page = canvas.Canvas(buffer)
        pdfmetrics.registerFont(TTFont('DejaVuSerif', 'DejaVuSerif.ttf', 'UTF-8'))
        x_position, y_position = 50, 800
        shopping_cart = (
            ShoppingCart.objects.filter(user=self.request.user).
            values(
                'recipe__ingredients__name',
                'recipe__ingredients__measurement_unit'
            ).annotate(amount=Sum('recipe__recipe__amount')).order_by())
        page.setFont('DejaVuSerif', 14)
        if shopping_cart:
            indent = 20
            page.drawString(x_position, y_position, 'Cписок покупок:')
            for index, recipe in enumerate(shopping_cart, start=1):
                page.drawString(
                    x_position, y_position - indent,
                    f'{index}. {recipe["recipe__ingredients__name"]} - '
                    f'{recipe["amount"]} '
                    f'{recipe["recipe__ingredients__measurement_unit"]}.')
                y_position -= 15
                if y_position <= 50:
                    page.showPage()
                    y_position = 800
            page.save()
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=FILENAME)
        page.setFont('DejaVuSerif', 24)
        page.drawString(
            x_position,
            y_position,
            'Cписок покупок пуст!')
        page.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=FILENAME)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None

    permission_classes = (ReadOnly,)


class CustomUserViewSet(UserViewSet):
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
        print(self.action)
        if self.action == "subscribe":
            return FollowSerializer
        if self.request.method.lower() == 'post':
            return UserCustomCreateSerializer
        return CustomUserSerializer

    def perform_create(self, serializer):
        # print('self:', self.request.data['password'], self.request.data['email'], self.request.data['username'])
        # u = User.objects.get(username=self.request.data['username'])
        # print(u)
        password = make_password(self.request.data['password'])
        print("views_pass", password)
        print("test", self.request.data['password'])
        serializer.save(password=self.request.data['password'])

    @action(
        detail=True,
        url_path="subscribe",
        methods=["post", "delete"],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id=None):
        if request.method == "POST":
            author = get_object_or_404(User, pk=id)
            print(author)
            if request.user.id == int(id):
                return Response(
                    {'errors': 'На самого себя не подписаться!'},
                    status=status.HTTP_400_BAD_REQUEST)
            if request.user.follower.filter(user=author).exists():
                return Response(
                    {'errors': 'Уже подписан!'},
                    status=status.HTTP_400_BAD_REQUEST)
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
                    {"message": f"Вы отписались!"},
                    status=status.HTTP_204_NO_CONTENT,
                )
            return Response(
                {"errors": "Подписка отсутствует!"}, status=status.HTTP_400_BAD_REQUEST
            )


# class GetTokenView(ObtainAuthToken):
#     """
#     Класс для обработки POST запросов для получения токена авторизации по email
#     и паролю.
#     URL - /auth/token/login/.
#     """
#
#     name = 'Получение токена'
#     description = 'Получение токена'
#     permission_classes = (AllowAny,)
#
#     def post(self, request):
#         """
#         Функция для обработки POST запроса, создает токен аутентификации при
#         предоставлении корректных email и пароля.
#         """
#         serializer = GetTokenSerializer(data=request.data)
#         if serializer.is_valid():
#             user = get_object_or_404(
#                 User, email=serializer.validated_data['email']
#             )
#             token, created = Token.objects.get_or_create(user=user)
#             return Response(
#                 {
#                     'auth_token': token.key
#                 },
#                 status=status.HTTP_201_CREATED
#             )
#         return Response(
#             serializer.errors,
#             status=status.HTTP_400_BAD_REQUEST
#         )



class AuthToken(ObtainAuthToken):
    """Авторизация пользователя."""

    serializer_class = TokenSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {'auth_token': token.key},
            status=status.HTTP_201_CREATED)


@api_view(['post'])
def set_password(request):
    """Изменить пароль."""

    serializer = UserPasswordSerializer(
        data=request.data,
        context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'message': 'Пароль изменен!'},
            status=status.HTTP_201_CREATED)
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST)
