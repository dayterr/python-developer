from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwt_views

from django.urls import include, path

from .views import CommentViewSet, FollowViewSet, GroupViewSet, PostViewSet

router_v1 = DefaultRouter()
router_v1.register('posts', PostViewSet, basename='posts')
router_v1.register(r'posts/(?P<post_id>\d+)/comments',
                   CommentViewSet, basename='comments')
router_v1.register('group',
                   GroupViewSet, basename='group')
router_v1.register('follow',
                   FollowViewSet, basename='follow')


urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/token/', jwt_views.TokenObtainPairView.as_view()),
    path('v1/token/refresh/', jwt_views.TokenRefreshView.as_view())
]
