from django.conf import settings
from django.contrib.auth.tokens import default_token_generator as dtg
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters, generics, mixins, permissions, status,
                            viewsets)
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import TitleFilter
from api.permissions import (
    IsAdminOrSuperuser,
    IsAuthorOrModeratorOrAdmin,
    IsAdminOrReadOnly)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             SignUpSerializer, TitleReadOnlySerializer,
                             TitleSerializer, TokenSerializer, UserSerializer)
from reviews.models import Category, Genre, Review, Title
from users.models import User


class SignUpView(generics.CreateAPIView):
    """
    Представление для регистрации новых пользователей.

    Позволяет любому пользователю зарегистрироваться, отправляя
    код подтверждения на указанный email.

    Аргументы
    ---------
    serializer_class : Класс для валидации и десериализации входящих данных.
    permission_classes : Класс доступов к эндпоинту данного вью.

    Методы
    ------
    perform_create(serializer) : Отправка кодов подтверждений пользователям.
    create(request) : Обработка запроса на создание пользователя.
    """

    serializer_class = SignUpSerializer
    permission_classes = (permissions.AllowAny,)

    def perform_create(self, serializer):
        """Поиск или создание пользователя, генерация и отправка кода."""
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']

        # Попытка получить или создать пользователя
        user, _ = User.objects.get_or_create(
            username=username,
            email=email,
        )
        # Генерация нового кода подтверждения
        confirmation_code = dtg.make_token(user)
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
        """После успешного создания юзера, переопределяет код ответа на 200."""
        response = super().create(request, *args, **kwargs)
        response.status_code = status.HTTP_200_OK
        return response


class TokenView(generics.CreateAPIView):
    """
    Вью для создания JWT-токена из username и confirmation_code.

    Этот класс обрабатывает только POST-запросы которые
    приходят на эндпоинт /api/v1/auth/token/.
    Для обновления access-токена не применяем refresh-токен и доп. эндпоинт.
    Токен обновляется через повторную передачу username и confirmation_code.
    Если проверка confirmation_code не проходит,
    сериализатор выбрасывает исключение, и выполнение
    метода create не продолжается.

    Аргументы
    ---------
    serializer_class : Класс для валидации и десериализации входящих данных.
    permission_classes : Класс доступов к эндпоинту данного вью.

    Методы
    ------
    create(request) : Обработка запроса на создание пользователя.
    """

    serializer_class = TokenSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        """Возвращает JWT-токен на основе username и confirmation_code."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        user = get_object_or_404(User, username=username)
        # Создаем JWT-токен для пользователя
        access_token = AccessToken.for_user(user)

        return Response({'token': str(access_token)},
                        status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для управления CRUD операциями Пользователей.

    Подключает два метода для выделенного эндпоинта /me/.
    GET /api/v1/users/me/: Получение данных текущего юзера.
    PATCH /api/v1/users/me/: Обновление данных текущего юзера.

    Аргументы
    ---------
    queryset : Выборка всех пользователей.
    serializer_class : Сериализатор для преобразования данных юзера.
    pagination_class : Пагинация результатов запроса.
    permission_classes : Разрешения, применимые ко всему вьюсету.
    filter_backends : Фильтр, используемый для поиска по username.
    search_fields : Поля, по которым будет происходить поиск.
    lookup_field : Поле, используемое для поиска юзера вместо pk.
    http_method_names : Разрешенные методы HTTP-запросов.

    Методы
    ------
    me(request) : Обработка GET/PATCH-запросов для авториз. юзера.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrSuperuser,)
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(detail=False, methods=['get', 'patch'], url_path='me',
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        """Обрабатывает GET и PATCH запросы только в /me/."""
        if request.method == 'GET':
            # Создаем экземпляр сериализатора с данными из POST-запроса:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)

        else:
            # Создаем экземпляр сериализатора с данными из POST-запроса.
            # partial=True -- поскольку у нас PATCH-запрос, а не PUT.
            serializer = self.get_serializer(request.user,
                                             data=request.data,
                                             partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data)


class NameSlugModelViewSet(mixins.CreateModelMixin,
                           mixins.ListModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    """Абстрактный класс для вьюсетов категория/жанр."""

    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]


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

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('rating')
    filter_backends = (DjangoFilterBackend,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)
    ordering_fields = ('name',)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return TitleReadOnlySerializer
        return TitleSerializer


class ReviewViewSet(ModelViewSet):
    """Вьюсет для ревью."""

    serializer_class = ReviewSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrModeratorOrAdmin,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(ModelViewSet):
    """Вьюсет для комментариев."""

    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin
    )
    http_method_names = ['get', 'post', 'patch', 'delete']

    def review_query(self):
        return get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        review = self.review_query()
        return review.comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.review_query())
