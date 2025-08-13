from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from .models import User, Subscribe
from recipes.models import Recipe


class FourFieldRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Subscribe.objects.filter(user=user, following=obj).exists()


class UserInSubscriptionsSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Subscribe.objects.filter(user=user, following=obj).exists()

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        request = self.context.get('request')
        return FourFieldRecipeSerializer(recipes, many=True,
                                         context={'request': request}).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscribeSerializer(serializers.Serializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        read_only=True)
    following = serializers.SlugRelatedField(slug_field='username',
                                             queryset=User.objects.all())

    class Meta:
        fields = ('id', 'user', 'following')
        model = Subscribe
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'following'),
                message='Подписаться на пользователя можно только один раз'
            ),
        )

    def create(self, validated_data):
        fol = validated_data.pop('following')
        user = self.context.get('request').user
        subscription = Subscribe.objects.create(user=user, following=fol)
        return subscription

    def validate_following(self, value):
        if self.context['request'].user == value:
            raise serializers.ValidationError(
                'Подписка на самого себя невозможна')
        return value


class UserCreateCustomSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email', 'username', 'password',
        )
