from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=100,
                            verbose_name='Название ингредиента')
    measurement_unit = models.CharField(max_length=10,
                                        verbose_name='Единицы измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (models.UniqueConstraint(
            fields=('name', 'measurement_unit'),
            name='OneNameOneUnit'),)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50,
                            verbose_name='Название тэга', unique=True)
    hex_code = models.CharField(max_length=10,
                                verbose_name='HEX-код', unique=True)
    slug = models.SlugField(unique=True, verbose_name='Адрес тэга')

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey('users.User', on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор, добавивший рецепт на сайт')
    name = models.CharField(max_length=300, verbose_name='Название блюда')
    image = models.ImageField(upload_to='recipes/',
                              verbose_name='Фото готового блюда')
    text = models.TextField(verbose_name='Текст рецепта')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientInRecipe',
                                         related_name='recipes',
                                         verbose_name='Ингредиент')
    tags = models.ManyToManyField(Tag, related_name='recipes',
                                  verbose_name='Тэг')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления рецепта на сайт'
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   verbose_name='Ингредиент')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='ings_in_recipe',
                               verbose_name='Рецепт')
    amount = models.PositiveSmallIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = (models.UniqueConstraint(fields=('ingredient', 'recipe'),
                       name='NoDuplicateIngredient'),)

    def __str__(self):
        return (f'{self.ingredient.name}: {self.amount} '
                f'{self.ingredient.measurement_unit}, '
                f'рецепт: {self.recipe.name}')


class Favourite(models.Model):
    author = models.ForeignKey('users.User', on_delete=models.CASCADE,
                               related_name='favs',
                               verbose_name='Автор "Избранного"')
    recipe = models.ForeignKey(Recipe, related_name='fav_recipes',
                               on_delete=models.CASCADE,
                               verbose_name='Рецепты')

    class Meta:
        verbose_name = 'Интересный рецепт'
        verbose_name_plural = 'Интересные рецепты'
        constraints = (models.UniqueConstraint(fields=('author', 'recipe'),
                       name='NoDuplicateRecipeInFavourite'),)


class ShoppingList(models.Model):
    author = models.ForeignKey('users.User', on_delete=models.CASCADE,
                               related_name='goods',
                               verbose_name='Автор списка покупок')
    recipe = models.ForeignKey(Recipe, related_name='shop_recipes',
                               on_delete=models.CASCADE,
                               verbose_name='Рецепты')

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = (models.UniqueConstraint(fields=('author', 'recipe'),
                       name='NoDuplicateRecipeInShoppingList'),)
