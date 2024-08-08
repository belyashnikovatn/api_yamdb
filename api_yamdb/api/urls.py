from rest_framework import routers

from django.urls import include, path

from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       ReviewViewSet, SignUpView, TitleViewSet, TokenView,
                       UserViewSet)

API_VERSION_1 = 'v1/'

router_v1 = routers.DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register(
    r'titles/(?P<title_id>[\d]+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>[\d]+)/reviews/(?P<review_id>[\d]+)/comments',
    CommentViewSet,
    basename='comments'
)

auth_patterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('token/', TokenView.as_view(), name='get_token'),
]

api_patterns = [
    path('auth/', include(auth_patterns)),
    path('', include(router_v1.urls)),
]

urlpatterns = [
    path(f'{API_VERSION_1}', include(api_patterns)),
]
