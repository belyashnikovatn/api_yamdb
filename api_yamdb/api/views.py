from rest_framework import viewsets
from rest_framework import filters, mixins, viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from reviews.models import Title, Genre, Category
from users.models import User
from api.serializers import (
    SignUpSerializer,
    TokenSerializer,
    UserSerializer,
    GenreSerailizer,
    CategorySerailizer,
    TitleSerailizer,
    TitleReadOnlySerailizer
)
from django_filters.rest_framework import DjangoFilterBackend
import random
import string
from django.core.mail import send_mail
from django.conf import settings


class SignUpView(generics.CreateAPIView):
    """
    Вью для регистрации пользователя.
    Этот класс обрабатывает только POST-запросы которые
    приходят на эндпоинт /api/v1/auth/signup/.

    Данный вью-класс использует сериализатор SignUpSerializer для
    валидации значений, переданных пользователем.

    Создает нового пользователя и отправляет код подтверждения.

    Модель, в которой будет создан новый
    пользователь определяется в сериализаторе.
    """
    serializer_class = SignUpSerializer

    def perform_create(self, serializer):
        """
        Создаем нового пользователя и сразу отправляем ему
        код подтверждения на email.

        :param serializer: Сериализатор с данными пользователя.
        """
        user = serializer.save()
        confirmation_code = ''.join(
            random.choices(string.ascii_letters + string.digits, k=20))
        user.confirmation_code = confirmation_code
        user.save()
        send_mail(
            'Ваш код подтверждения',
            f'Ваш код подтверждения {confirmation_code}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


class TokenView(generics.GenericAPIView):
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

    def create(self, request, *args, **kwargs):
        """
        Создает JWT-токен на основе username и confirmation_code.

        :param request: Входной запрос.
        :return: Ответ с JWT токеном или ошибкой валидации.
        """
        # Создаем экземпляр сериализатора с данными из POST-запроса:
        serializer = self.get_serializer(data=request.data)
        # Проверяем, что данные POST-запроса валидны.
        # Если нет, выбрасывается ValidationError:
        serializer.is_valid(raise_exception=True)
        # Извлекаем успешно провалидированные
        # значения из validated_data в сериализаторе TokenSerializer:
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']

        # Логика проверки и создания токена
        try:
            # В момент регестрации (SignUpView) эти поля пропишутся в Users
            user = User.objects.get(username=username,
                                    confirmation_code=confirmation_code)
        except User.DoesNotExist:
            return Response({'detail': 'Неверное имя или код подтверждения'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Создание объекта AccessToken для пользователя
        access_token = AccessToken.for_user(user)

        return Response({'access': str(access_token),
                         }, status=status.HTTP_200_OK)


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
    # permission_classes -- пока что оставлю заглушку.
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter,)
    search_fields = ('username',)

    @action(detail=False, methods=['get', 'patch'], url_path='me')
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
    """Вьюсет для жанра."""
    serializer_class = GenreSerailizer
    queryset = Genre.objects.all()


class CategoryViewSet(NameSlugModelViewSet):
    """Вьюсет для категории."""
    serializer_class = CategorySerailizer
    queryset = Category.objects.all()


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""
    serializer_class = TitleSerailizer
    queryset = Title.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'year', 'genre__slug', 'category__slug')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleReadOnlySerailizer
        return TitleSerailizer
