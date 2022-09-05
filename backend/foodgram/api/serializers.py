from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.db.models import Count
import django.contrib.auth.password_validation as validators
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator
from django.shortcuts import get_object_or_404
from drf_base64.fields import Base64ImageField

from recipe.models import User, Follow, Tag, Ingredient, IngredientRecipe, Recipe, Favorite, ShoppingCart
from djoser.serializers import UserCreateSerializer
from djoser.serializers import UserSerializer

ERR_MSG = 'Не удается войти в систему с предоставленными учетными данными.'


# class GetTokenSerializer(serializers.Serializer):
#     """
#     Сериализатор для обработки запросов на получение токена.
#     """
#
#     email = serializers.EmailField(max_length=254)
#     password = serializers.CharField(max_length=128)
#
#     def validate(self, data):
#         """
#         Функция проверяет, что предоставленный пользователем email соотвествует
#         пользователю в базе данных и указанный пароль корректен для
#         пользователя с указанным e-mail.
#         """
#
#         try:
#             user = User.objects.get(email=data['email'])
#         except User.DoesNotExist:
#             raise serializers.ValidationError(
#                 'Предоставлен email незарегистрированного пользователя.'
#             )
#
#         print(user.check_password(data['password']))
#         print(data['password'])
#
#         user = self.context['request'].user
#         print("User:", user, "\nemail:", user.email, "\npassword:", data['password'])
#         if not authenticate(
#                 username=user.email,
#                 password=data['password']):
#             raise serializers.ValidationError(
#                 ERR_MSG, code='authorization')
#         return data['password']
#         # if user.check_password(data['password']):
#         #     return data
#         # raise serializers.ValidationError(
#         #     'Неверный пароль для пользователя с указанным email.'
#         # )
#
#
class TokenSerializer(serializers.Serializer):
    email = serializers.CharField(
        label='Email',
        write_only=True)
    password = serializers.CharField(
        label='Пароль',
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True)
    token = serializers.CharField(
        label='Токен',
        read_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        print(email, password)
        if email and password:
            user = authenticate(
                # request=self.context.get('request'),
                email=email,
                password=password)
            print(user)
            if not user:
                raise serializers.ValidationError(
                    ERR_MSG,
                    code='authorization')
        else:
            msg = 'Необходимо указать "адрес электронной почты" и "пароль".'
            raise serializers.ValidationError(
                msg,
                code='authorization')
        attrs['user'] = user
        return attrs


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', "is_subscribed",)

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        follow = self.context['follow']
        if str(user) != 'AnonymousUser':
            if follow.filter(user=user, author=obj):
                return True
            return False
        return None


class UserCustomCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )

    def validate_password(self, password):
        validators.validate_password(password)
        return password

    # def create(self, validated_data):
    #     user = self.context['request'].user
    #     # password = make_password(
    #     #     validated_data.get('new_password'))
    #     # user.password = password
    #     user.set_password(validated_data.get('password'))
    #     user.save()
    #     return validated_data


class ShoppingCartSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    cooking_time = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCart
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )

    def get_name(self, obj):
        return obj.recipe.name

    def get_image(self, obj):
        return obj.recipe.image.url

    def get_cooking_time(self, obj):
        return obj.recipe.cooking_time


class FavoriteSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    cooking_time = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Favorite
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )

    def get_name(self, obj):
        return obj.recipe.name

    def get_image(self, obj):
        return obj.recipe.image.url

    def get_cooking_time(self, obj):
        return obj.recipe.cooking_time


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id",
                  "name",
                  "color",
                  "slug",
                  )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit"
        )


class IngredientsqRecipeSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    id = serializers.ReadOnlyField(
        source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name')

    class Meta:
        model = IngredientRecipe
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class RecipeSerializer(serializers.ModelSerializer):
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    image = Base64ImageField()
    author = CustomUserSerializer()
    tags = TagSerializer(many=True)
    ingredients = IngredientsqRecipeSerializer(many=True, required=True, source='recipe')

    class Meta:
        model = Recipe
        fields = ("id",
                  "tags",
                  "author",
                  "ingredients",
                  "is_favorited",
                  "is_in_shopping_cart",
                  "name",
                  "image",
                  "text",
                  "cooking_time",)
        read_only_fields = ("author",)

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        shopping_cart = self.context['shopping_cart']
        if str(user) != 'AnonymousUser':
            if shopping_cart.filter(recipe=obj, user=user):
                return True
            return False
        return None

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        favorite = self.context['favorite']
        if str(user) != 'AnonymousUser':
            if favorite.filter(recipe=obj, user=user):
                return True
            return False
        return None


class IngredientRecipesSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='ingredient')

    class Meta:
        model = IngredientRecipe
        fields = (
            "id",
            "amount",
        )


class RecipeCreatySerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    tags = serializers.SlugRelatedField(
        queryset=Tag.objects.all(), slug_field="pk", many=True
    )
    ingredients = IngredientRecipesSerializer(many=True)
    image = Base64ImageField(
        max_length=None,
        use_url=True)

    class Meta:
        model = Recipe
        fields = ("id",
                  "tags",
                  "author",
                  "ingredients",
                  "name",
                  "image",
                  "text",
                  "cooking_time",)
        read_only_fields = ("author",)

    def validate(self, data):
        ingredients = data['ingredients']
        ingredient_list = []
        for items in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=items['ingredient'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиент должен быть уникальным!')
            ingredient_list.append(ingredient)
        tags = data['tags']
        if not tags:
            raise serializers.ValidationError(
                'Нужен хотя бы один тэг для рецепта!')
        for tag_name in tags:
            if not Tag.objects.filter(slug=tag_name).exists():
                raise serializers.ValidationError(
                    f'Тэга {tag_name} не существует!')
        return data

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) < 1:
            raise serializers.ValidationError(
                'Время приготовления >= 1!')
        return cooking_time

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Мин. 1 ингредиент в рецепте!')
        for ingredient in ingredients:
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента >= 1!')
        return ingredients

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient['ingredient'],
                amount=ingredient['amount'], )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        # recipe.tags.add(*tags)
        recipe.tags.set(tags)
        # for ingredient in ingredients:
        #     Ingredient_id, amount = ingredient['ingredient'], ingredient['amount']
        #     current_ingredient = Ingredient.objects.get(id=Ingredient_id)
        #     IngredientRecipe.objects.create(
        #         ingredient=current_ingredient, recipe=recipe, amount=amount)
        self.create_ingredients(ingredients, recipe)
        # recipe = Recipe.objects.get(pk=recipe.pk)
        # return RecipeSerializer(recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags'))
        return super().update(
            instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request'),
                'follow': Follow.objects.all(),
                'favorite': Favorite.objects.all(),
                'shopping_cart': ShoppingCart.objects.all()
            }).data


class RecipeFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class FollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    email = serializers.CharField(source='author.email')
    id = serializers.IntegerField(source='author.id')
    username = serializers.CharField(source='author')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')

    class Meta:
        model = Follow
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = (
            obj.author.recipe_user.all()[:int(limit)] if limit
            else obj.author.recipe_user.all())
        return RecipeFollowSerializer(
            recipes,
            many=True).data

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        follow = self.context['follow']
        if str(user) != 'AnonymousUser':
            if follow.filter(user=user, author=obj.author):
                return True
            return False
        return None

    def get_recipes_count(self, obj):
        return obj.author.recipe_user.all().count()


class UserPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        label='Новый пароль')
    current_password = serializers.CharField(
        label='Текущий пароль')

    def validate_current_password(self, current_password):
        user = self.context['request'].user
        print(authenticate(
            email=user.email,
            password=current_password))
        if not authenticate(
                username=user.email,
                password=current_password):
            raise serializers.ValidationError(
                ERR_MSG, code='authorization')
        return current_password

    def validate_new_password(self, new_password):
        validators.validate_password(new_password)
        return new_password

    def create(self, validated_data):
        user = self.context['request'].user
        # password = make_password(
        #     validated_data.get('new_password'))
        # user.password = password
        user.set_password(validated_data.get('new_password'))
        user.save()
        return validated_data
