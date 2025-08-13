import io

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab import rl_config
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import IngredientFilter, RecipeFilter
from .models import (Favourite, Ingredient,
                     Recipe, ShoppingList, Tag)
from .pagination import CustomPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializer import (FavouriteSerializer, IngredientSerializer,
                         RecipeReadSerializer,
                         RecipeWriteSerializer,
                         ShoppingListSerializer, TagSerializer)

rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/fonts')


class RecipeViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filter_class = IngredientFilter
    pagination_class = None
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class BaseCustomView(APIView):
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    error_message = None
    serializer_to_use = None
    model_contains = None

    def get(self, request, recipe_id):
        author = request.user
        data = {
            'author': author.id,
            'recipe': recipe_id
        }
        serializer = self.serializer_to_use(data=data,
                                            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        author = request.user
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        rec_exists = self.model_contains.objects.filter(author=author,
                                                        recipe=recipe).delete()
        if rec_exists[0] == 0:
            return Response(self.error_message,
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingListViewSet(BaseCustomView):
    error_message = 'Данного рецепта нет в Вашем списке покупок'
    serializer_to_use = ShoppingListSerializer
    model_contains = ShoppingList


class FavouriteViewSet(BaseCustomView):
    error_message = 'Данного рецепта нет в Избранном'
    serializer_to_use = FavouriteSerializer
    model_contains = Favourite


class DownloadShoppingList(APIView):
    permission_classes = (IsAuthorOrAdminOrReadOnly,)

    def get(self, request):
        recipes = Recipe.objects.filter(shop_recipes__author=request.user.pk)
        ingredients = recipes.values_list(
            'ingredients__name',
            'ingredients__measurement_unit'
        ).annotate(ingredients_amount=Sum('ings_in_recipe__amount'))
        response = HttpResponse(content_type='application/pdf; charset=UTF-8')
        response['Content-Disposition'] = 'attachment; filename="spisok.pdf"'
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        textobject = p.beginText()
        textobject.setTextOrigin(inch, 10.5 * inch)
        pdfmetrics.registerFont(TTFont('Roboto', 'Roboto-Regular.ttf'))
        textobject.setFont('Roboto', 14)
        for ingr in ingredients:
            stroka = f'{ingr[0]}: {ingr[2]} {ingr[1]}'
            textobject.textLine(stroka)
        p.drawText(textobject)
        p.showPage()
        p.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
