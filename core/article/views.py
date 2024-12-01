from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action

from .serializers import ArticleSerializer, CommentSerializer, CategorySerializer, TagSerializer
from .permissions import *
from .filters import ArticleFilter, CategoryFilter, TagFilter, CommentFilter
from .models import Article, Comment, Category, Tag
from .pagination import CustomPagination


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [
        IsAuthenticated,
        (AdminPermissions | ModeratorPermissions | CategoryAndTagPermissions)
    ]
    # Pagination, Filtering, and Search
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = CategoryFilter
    search_fields = ['name']

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as ex:
            return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({
                "success": False,
                "message": "An unexpected error occurred.",
                "error": str(ex)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [
        IsAuthenticated,
        (AdminPermissions | ModeratorPermissions | CategoryAndTagPermissions)
    ]
    # Pagination, Filtering, and Search
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = TagFilter
    search_fields = ['name']

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as ex:
            return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({
                "success": False,
                "message": "An unexpected error occurred.",
                "error": str(ex)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().order_by('-created_at')
    serializer_class = ArticleSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [
        IsAuthenticated,
        (AdminPermissions | ModeratorPermissions | ArticleAndCommentPermissions)
    ]    
    # Pagination, Filtering, and Search
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ArticleFilter
    search_fields = ['title', 'content', 'category__name', 'tags__name']

    def perform_create(self, serializer):
        # The serializer now handles category and tag creation, no need to do it here.
        article = serializer.save(author=self.request.user)
        # Tags are already handled by the serializer (via tags.set), so no need to explicitly set them here.
        return article

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as ex:
            return Response({
                "success": False,
                "message": str(ex)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({
                "success": False,
                "message": "An unexpected error occurred.",
                "error": str(ex)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [
        IsAuthenticated,
        (AdminPermissions | ModeratorPermissions | ArticleAndCommentPermissions)
    ]  
    # Pagination, Filtering, and Search
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = CommentFilter  
    search_fields = ['comment']

    def perform_create(self, serializer):
        try:
            serializer.save(author=self.request.user)
        except ValidationError as ex:
            raise ValidationError({"message": str(ex)})
        except Exception as ex:
            print(ex)
            raise ValidationError({"message": "An unexpected error occurred while creating the comment."})

    # Override create method to handle validation and custom exceptions
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as ex:
            return Response({
                "success": False,
                "message": str(ex)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({
                "success": False,
                "message": "An unexpected error occurred.",
                "error": str(ex)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
    # Custom method to retrieve comments for a specific article
    @action(detail=True, methods=['get'])
    def article_comments(self, request, uid=None):
        article = get_object_or_404(Article, uid=uid)
        comments = self.queryset.filter(article=article)
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)
