from django.contrib import admin

from .models import Ingredient, IngredientInRecipe, Recipe, Tag


class IngredientClass(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'in_favourite')
    list_filter = ('author', 'name', 'tags')

    def in_favourite(self, obj):
        return obj.fav_recipes.count()

    in_favourite.short_description = ('Количество добавлений '
                                      'рецепта в "Избранное"')


admin.site.register(Ingredient, IngredientClass)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(IngredientInRecipe)
