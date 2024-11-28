from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError

from manager.permissions import IsAdmin, IsModerator
from .serializers import ArticleSerializer, CommentSerializer
from .pagination import CustomPagination
from .models import Article, Comment


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().order_by('-created_at')
    serializer_class = ArticleSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin | IsModerator]

    # Pagination, Filtering, and Search
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category', 'author']
    search_fields = ['title', 'content']

    def perform_create(self, serializer):
        if not self.request.user.has_approval:
            raise ValidationError("You are not approved to write articles. Submit a request for approval.")
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin | IsModerator]

    # Pagination, Filtering, and Search
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['article', 'author']  # Allows filtering by article and author
    search_fields = ['comment']  # Allows searching by comment's content

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
