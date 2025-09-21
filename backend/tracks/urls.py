from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, TrackViewSet, CommentViewSet, 
    LikeViewSet, ReportViewSet
)

# Crear router y registrar ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'tracks', TrackViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'likes', LikeViewSet)
router.register(r'reports', ReportViewSet)

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
    # Endpoints adicionales para funcionalidades específicas
    path('auth/register/', UserViewSet.as_view({'post': 'register'}), name='user-register'),
]