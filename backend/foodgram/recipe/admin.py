from django.contrib import admin

from .models import (Favorite, Follow, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag, User)


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
    search_fields = ("name",)
    list_editable = ("measurement_unit",)
    list_filter = ("name",)
    empty_value_display = "-пусто-"


class RecipeIngredientAdmin(admin.StackedInline):
    model = IngredientRecipe
    autocomplete_fields = ("ingredient",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "get_ingredients",
        "get_tags",
        "author",
        "get_favorite_count",
    )
    search_fields = (
        "name",
        "author",
        "tags",
        "author__email",
        "ingredients__name",
    )
    list_filter = (
        "name",
        "author",
        "tags",
    )
    inlines = (RecipeIngredientAdmin,)
    readonly_fields = ["get_favorite_count"]
    empty_value_display = "-пусто-"

    def get_tags(self, obj):
        list_ = [_.name for _ in obj.tags.all()]
        return ", ".join(list_)

    get_tags.short_description = "Тэги"

    def get_ingredients(self, obj):
        return "\n ".join(
            [
                f'{item["ingredient__name"]} - {item["amount"]}'
                f' {item["ingredient__measurement_unit"]}.'
                for item in obj.recipe.values(
                    "ingredient__name",
                    "amount",
                    "ingredient__measurement_unit",
                )
            ]
        )

    get_ingredients.short_description = "Ингредиенты"

    def get_favorite_count(self, obj):
        return obj.recipe_favorite.count()

    get_favorite_count.short_description = "В избранном"


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
    list_filter = ("recipe",)
    empty_value_display = "-пусто-"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user",
        "recipe",
        "get_count",
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

    def get_count(self, obj):
        return obj.recipe.recipe_favorite.count()

    get_count.short_description = "В избранных"


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user",
        "get_recipe",
        "get_count",
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

    def get_recipe(self, obj):
        return [f"{obj.recipe.name}"]

    get_recipe.short_description = "Рецепт"

    def get_count(self, obj):
        return obj.recipe.recipe_favorite.count()

    get_count.short_description = "В избранных"
