from django.urls import include, path
from rest_framework import routers

# from .views import SignUpView, TokenView, UsersViewSet

API_VERSION_1 = 'v1/'

router_v1 = routers.DefaultRouter()
# router_v1.register('posts', UsersViewSet)

urlpatterns = [
    # path(f'{API_VERSION_1}auth/signup/', SignUpView.as_view(), name='signup'),
    # path(f'{API_VERSION_1}auth/token/', TokenView.as_view(), name='get_token'),
    # path(f'{API_VERSION_1}', include(router_v1.urls)),
]