from rest_framework import viewsets
from rest_framework import filters, mixins, viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework import serializers

from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator as dtg

from reviews.models import Title, Genre, Category, Review

from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator as dtg

from reviews.models import Title, Genre, Category

from users.models import User
from api.serializers import (
    SignUpSerializer,
    TokenSerializer,
    UserSerializer,
    GenreSerializer,
    CategorySerializer,
    TitleSerializer,
    TitleReadOnlySerializer,
    ReviewSerializer,
    CommentSerializer
)
from api.permissions import (IsAdminOrReadOnly,
                             IsAdminOrSuperuser,
                             IsAuthorOrModeratorOrAdmin)
from django_filters.rest_framework import DjangoFilterBackend
import random
import string
from django.core.mail import send_mail
from django.conf import settings

# TEST
class SignUpView(generics.CreateAPIView):
    serializer_class = SignUpSerializer
    permission_classes = (permissions.AllowAny,)

    def perform_create(self, serializer):
        """
        Создаем нового пользователя и сразу отправляем ему
        код подтверждения на email.
        """
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']

        # Попытка получить или создать пользователя
        user, _ = User.objects.get_or_create(
            username=username,
            email=email,
        )
        # Генерация нового кода подтверждения
        confirmation_code = ''.join(
            random.choices(string.ascii_letters + string.digits, k=20)
        )
        user.confirmation_code = confirmation_code
        user.save()
        send_mail(
            'Ваш код подтверждения',
            f'Ваш код подтверждения {confirmation_code}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.status_code = status.HTTP_200_OK
        return response


class TokenView(generics.CreateAPIView):
    """
    Вью для получения JWT-токена.

    Этот класс обрабатывает только POST-запросы которые
    приходят на эндпоинт /api/v1/auth/token/.

    Данный вью-класс использует сериализатор TokenSerializer для
    валидации значений, переданных пользователем.

    Принимает параметры username и confirmation_code от юзера,
    и возвращает JWT access-токен.

    Для обновления access-токена не применяем refresh-токен и доп. эндпоинт.
    Токен обновляется через повторную передачу username и кода подтверждения.
    """
    serializer_class = TokenSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        """
        Создает JWT-токен на основе username и confirmation_code.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        user = get_object_or_404(User, username=username)
        # Проверяем код подтверждения
        if not dtg.check_token(user, request.data.get('confirmation_code')):
            raise ValidationError('Неверный код подтверждения')

        # Создаем JWT-токен для пользователя
        access_token = AccessToken.for_user(user)
        
        return Response({'token': str(access_token)}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для управления CRUD операциями Пользователей.

    GET /api/v1/users/: Получение списка юзеров
    с возможностью поиска по username.
    POST /api/v1/users/: Создание нового юзера.
    GET /api/v1/users/{username}/: Получение данных юзера по username.
    PATCH /api/v1/users/{username}/: Обновление данных юзера по username.
    DELETE /api/v1/users/{username}/: Удаление юзера.

    Кастомные методы:
    GET /api/v1/users/me/: Получение данных текущего юзера.
    PATCH /api/v1/users/me/: Обновление данных текущего юзера.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrSuperuser,)
    filter_backends = (SearchFilter,)
    search_fields = ('username',)

    @action(detail=False, methods=['get', 'patch'], url_path='me',
            permission_classes=(permissions.IsAuthenticated,))

    def me(self, request):
        """
        Обрабатывает GET и PATCH запросы для
        текущего аутентифицированного пользователя.
        """
        if request.method == 'GET':
            # Создаем экземпляр сериализатора с данными из POST-запроса:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)

        elif request.method == 'PATCH':
            # Создаем экземпляр сериализатора с данными из POST-запроса.
            # partial=True -- поскольку у нас PATCH-запрос, ставим флаг
            # что мы обновляем не все поля, как в PUT-запросе, а выборочные.
            serializer = self.get_serializer(request.user,
                                             data=request.data,
                                             partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)


class NameSlugModelViewSet(mixins.CreateModelMixin,
                           mixins.ListModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    """Абстрактный класс для вьюсетов категория/жанр."""
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(NameSlugModelViewSet):
    """Вьюсет для жанра.
    Доступные действия: просмотр списка, добавление, удаление,
    поиск по наименованию (регистр учитывается)."""
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()


class CategoryViewSet(NameSlugModelViewSet):
    """Вьюсет для категории.
    Доступные действия: просмотр списка, добавление, удаление,
    поиск по наименованию (регистр учитывается)."""
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений.
    Доступные действия: весь набор.
    Поиск по полям: название, год, slug жанры(ы), slug категория."""
    serializer_class = TitleSerializer
    queryset = Title.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'year', 'genre__slug', 'category__slug')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleReadOnlySerializer
        return TitleSerializer


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrModeratorOrAdmin,)

    def get_serializer_context(self):
        context = super(ReviewViewSet, self).get_serializer_context()
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        context.update({'title': title})
        return context

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModeratorOrAdmin,)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )
        user = get_object_or_404(User, username=self.request.user)
        serializer.save(author=user, review=review)
