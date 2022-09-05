from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.db.models import Q, F, CheckConstraint, UniqueConstraint
from django.db.models.signals import post_save
from django.core import validators
from django.dispatch import receiver

from .validators import validate_hex


# class UserAccountManager(BaseUserManager):
#     def create_user(self, email, username, first_name, last_name, password=None):
#         if not email:
#             raise ValueError('Users must have an email address')
#
#         email = self.normalize_email(email)
#         user = self.model(email=email, username=username, first_name=first_name, last_name=last_name)
#
#         user.set_password(password)
#         user.save()
#
#         return user


class User(AbstractUser):
    # username = models.CharField(
    #     max_length=150, null=False, blank=False, unique=True
    # )
    email = models.EmailField(
        max_length=254, unique=True, null=False, blank=False
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    # bio = models.TextField(blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    # objects = UserAccountManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.email


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        related_name="following",
        verbose_name="Автор",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        related_name="follower",
        verbose_name="Подписчик",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Подписку"
        verbose_name_plural = "Подписки"
        constraints = [
            CheckConstraint(check=~Q(author=F('user')),
                            name='author_not_user'),
            UniqueConstraint(fields=['user', 'author'],
                             name='unique_author_unique')
        ]


class Tag(models.Model):
    name = models.CharField("Наименование", max_length=256)
    color = models.CharField(max_length=16, validators=[validate_hex])
    slug = models.CharField("Ссылка", max_length=50, unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категория"

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    name = models.CharField("Название", max_length=256)
    measurement_unit = models.CharField("Единица измерения", max_length=10)

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField("Название", max_length=256)
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        related_name="recipe_user",
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        'Изображение рецепта',
        upload_to="recipe/",
        blank=True,
        null=True
    )
    text = models.TextField("Описание")
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name="ingredients",
        verbose_name="Ингредиенты",
        through='IngredientRecipe'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Категория",
        blank=True,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[validators.MinValueValidator(
            1, message='Мин. время приготовления 1 минута'), ])

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ('-id', )

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name="Ингридиент",
        related_name="amount",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        related_name="recipe",
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=(
            validators.MinValueValidator(
                1, message='Мин. количество ингридиентов 1'),),
        verbose_name='Количество', )

    class Meta:
        verbose_name = "Ингридиенты рецепта"
        verbose_name_plural = "Ингридиенты рецептов"
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique ingredient')]

    def __str__(self):
        return f'{self.amount}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        related_name="recipe_favorite",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"


    def __str__(self):
        return f'Рецепт {self.recipe} в избранного {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name='shopping_cart',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        related_name="shopping_cart",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f'Рецепт {self.recipe} в корзине {self.user}'


    # @receiver(post_save, sender=User)
    # def create_shopping_cart(
    #         sender, instance, created, **kwargs):
    #     if created:
    #         return ShoppingCart.objects.create(user=instance)

