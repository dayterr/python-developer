from django.urls import include, path

from .views import SubscribeViewSet, SubscribeListViewSet

urlpatterns = [
    path('users/<int:user_id>/subscribe/', SubscribeViewSet.as_view(),
         name='subscribe_to_users'),
    path('users/subscriptions/', SubscribeListViewSet.as_view({'get': 'list'}),
         name='subscriptions'),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
]
