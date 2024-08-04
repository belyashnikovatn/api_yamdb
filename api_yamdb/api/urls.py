from rest_framework import routers

from django.urls import include, path

from api.views import (CategoryViewSet,
                       GenreViewSet,
                       TitleViewSet,
                       SignUpView,
                       TokenView,
                       UserViewSet)


API_VERSION_1 = 'v1/'

router_v1 = routers.DefaultRouter()
router_v1.register('users', UserViewSet)
router_v1.register('genres', GenreViewSet)
router_v1.register('categories', CategoryViewSet)
router_v1.register('titles', TitleViewSet)

urlpatterns = [
    path(f'{API_VERSION_1}auth/signup/', SignUpView.as_view(), name='signup'),
    path(f'{API_VERSION_1}auth/token/', TokenView.as_view(), name='get_token'),
    path(f'{API_VERSION_1}', include(router_v1.urls)),
]
