from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import (Favourite, Ingredient,
                     IngredientInRecipe, Recipe, ShoppingList, Tag)
from users.models import User
from users.serializer import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=ShoppingList.objects.all(),
                fields=('name', 'measurement_unit'),
                message=('Рецепт можно добавить '
                         'в список покупок только один раз')
            ),
        )


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='ingredient',
                                            queryset=Ingredient.objects.all())
    name = serializers.SlugRelatedField(read_only=True, source='ingredient',
                                        slug_field='name')
    measurement_unit = serializers.SlugRelatedField(
        read_only=True, source='ingredient',
        slug_field='measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')

    def get_ingredients(self, obj):
        ing_list = obj.ings_in_recipe.all()
        return IngredientInRecipeSerializer(ing_list, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        author = request.user
        return Favourite.objects.filter(author=author, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        author = request.user
        return ShoppingList.objects.filter(author=author, recipe=obj).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(many=True,
                                               source='ings_in_recipe')
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True,
    )

    class Meta:
        model = Recipe
        fields = ('author', 'id', 'ingredients', 'tags',
                  'image', 'name', 'text', 'cooking_time')

    def validate(self, data):
        ingredients = data.get('ings_in_recipe')
        ingredients_set = set([value.get('ingredient')
                               for value in ingredients])
        if len(ingredients) > len(ingredients_set):
            raise serializers.ValidationError('Ингредиенты в рецепте '
                                              'не должны повторяться')
        tags = data.get('tags')
        tags_set = set([value for value in tags])
        if len(tags) > len(tags_set):
            raise serializers.ValidationError('Тэги должны быть уникальны')
        cooking_time = data.get('cooking_time')
        if cooking_time < 0:
            raise serializers.ValidationError('Время приготовления не '
                                              'может быть отрицательным')
        for ingredient in ingredients:
            if ingredient.get('amount') < 0:
                raise serializers.ValidationError('Количество ингредиента не '
                                                  'может быть отрицательным')
        return data

    def get_nested(self, validated_data):
        ingredients = validated_data.pop('ings_in_recipe')
        tags = validated_data.pop('tags')
        return ingredients, tags

    def save_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            ingredients_in_recipe = IngredientInRecipe.objects.create(
                recipe=recipe, ingredient=ingredient['ingredient'],
                amount=ingredient.get('amount'))
            ingredients_in_recipe.save()

    def create(self, validated_data):
        ingredients, tags = self.get_nested(validated_data)
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.save_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        ingredients, tags = self.get_nested(validated_data)
        for tag_id in tags:
            instance.tags.add(tag_id)
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        self.save_ingredients(ingredients, instance)
        if validated_data.get('image') is not None:
            instance.image = validated_data.get('image')
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(
            instance, context=context).data


class FourFieldRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingListSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingList
        fields = ('author', 'recipe')
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=ShoppingList.objects.all(),
                fields=('author', 'recipe'),
                message=('Рецепт можно добавить '
                         'в список покупок только один раз')
            ),
        )

    def to_representation(self, instance):
        request = self.context.get('request')
        recipe = FourFieldRecipeSerializer(instance.recipe,
                                           context={'request': request}).data
        return recipe


class FavouriteSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favourite
        fields = ('author', 'recipe')
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Favourite.objects.all(),
                fields=('author', 'recipe'),
                message='Рецепт можно добавить в Избранное только один раз'
            ),
        )

    def to_representation(self, instance):
        request = self.context.get('request')
        recipe = FourFieldRecipeSerializer(instance.recipe,
                                           context={'request': request}).data
        return recipe
