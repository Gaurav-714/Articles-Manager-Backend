from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet, CommentViewSet, CategoryViewSet, TagViewSet

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='articles')
router.register(r'comments', CommentViewSet, basename='comments')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
]
