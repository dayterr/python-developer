from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     UpdateAPIView)
from rest_framework.mixins import (CreateModelMixin,
                                   DestroyModelMixin, ListModelMixin)
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

from .filters import TitleFilter
from .models import Category, Genre, Review, Title, User
from .permissions import IsAdminOrReadOnly, IsAutrhOrAdminOrModeratorOrReadOnly
from .serializer import (CategorySerializer, CommentSerializer,
                         GenreSerializer, ReviewSerializer,
                         TitleReadSerializer, TitleWriteSerializer,
                         UserAdminSerializer, TokenSerializer,
                         UserEmailSerializer, UserSerializer)


class CategoryViewSet(viewsets.GenericViewSet,
                      CreateModelMixin,
                      DestroyModelMixin, ListModelMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(viewsets.GenericViewSet,
                   CreateModelMixin,
                   DestroyModelMixin, ListModelMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.GenericViewSet, CreateAPIView, DestroyAPIView,
                   ListAPIView, RetrieveAPIView, UpdateAPIView):
    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_object(self):
        obj = get_object_or_404(Title, pk=self.kwargs.get('pk'))
        return obj

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (
        IsAutrhOrAdminOrModeratorOrReadOnly, )

    def get_queryset(self):
        title = get_object_or_404(
            Title, id=self.kwargs['title_id'])
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title, id=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        IsAutrhOrAdminOrModeratorOrReadOnly, )

    def get_queryset(self):
        review = get_object_or_404(
            Review, id=self.kwargs['review_id'],
            title=self.kwargs['title_id'])
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review, id=self.kwargs['review_id'],
            title=self.kwargs['title_id'])
        serializer.save(author=self.request.user, review=review)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    lookup_field = 'username'
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.request.user.is_admin:
            return UserAdminSerializer
        return UserSerializer

    @action(
        detail=False,
        methods=['GET', 'PATCH'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_confirmation_code(request):
    serializer = UserEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data['email']
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = User.objects.create_user(username=email, email=email)
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        'Код подтверждения',
        f'Ваш код подтверждения: {confirmation_code}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False
    )
    return Response(
        data={'message': f'Код выслан на email: {email}'}
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data['email']
    confirmation_code = serializer.data['confirmation_code']
    user = get_object_or_404(User, email=email)
    if not default_token_generator.check_token(
            user=user, token=confirmation_code):
        return Response(
            data={'confirmation_code': 'Несоответствие кода подтверждения'})
    token = AccessToken.for_user(user)
    return Response({'token': {token}})
