from django.contrib import admin

from .models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "username",
        "email",
        "first_name",
        "last_name",
    )
    search_fields = (
        "username",
        "email",
    )
    list_filter = (
        "username",
        "email",
    )
    empty_value_display = "-пусто-"


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "user",
    )
    search_fields = (
        "author",
        "user",
    )
    list_filter = (
        "author",
        "user",
    )
    empty_value_display = "-пусто-"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "slug",
    )
    search_fields = (
        "name",
        "slug",
    )
    list_filter = (
        "name",
        "slug",
    )
    empty_value_display = "-пусто-"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "measurement_unit",
    )
    search_fields = (
        "name",
    )
    list_editable = (
        "measurement_unit",
    )
    list_filter = (
        "name",
    )
    empty_value_display = "-пусто-"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
    )
    search_fields = (
        "name",
        "author",
        "tags",
    )
    list_filter = (
        "name",
        "author",
        "tags",
    )
    empty_value_display = "-пусто-"


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "recipe",
        "ingredient",
        "amount",
    )
    search_fields = (
        "recipe",
        "ingredient",
    )
    list_editable = (
        "ingredient",
        "amount",
    )
    list_filter = (
        "recipe",
    )
    empty_value_display = "-пусто-"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user",
        "recipe",
    )
    search_fields = (
        "recipe",
        "user",
    )
    list_filter = (
        "recipe",
        "user",
    )
    empty_value_display = "-пусто-"


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user",
    )
    search_fields = (
        "recipe",
        "user",
    )
    list_filter = (
        "recipe",
        "user",
    )
    empty_value_display = "-пусто-"