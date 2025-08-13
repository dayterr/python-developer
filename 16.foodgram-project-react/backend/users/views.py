from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Subscribe, User
from .serializer import (SubscribeSerializer,
                         UserInSubscriptionsSerializer)
from recipes.pagination import CustomPagination


class SubscribeViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, user_id):
        user = request.user
        fol = User.objects.get(id=user_id)
        data = {
            'user': user.id,
            'following': fol
        }
        serializer = SubscribeSerializer(data=data,
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        user = request.user
        following = get_object_or_404(User, pk=user_id)
        sub_exists = Subscribe.objects.filter(user=user,
                                              following=following).delete()
        if sub_exists[0] == 0:
            return Response('Вы не подписаны на данного пользователя',
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeListViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserInSubscriptionsSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(following__user=user)
