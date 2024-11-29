from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action

from .permissions import IsAdmin, IsModerator
from .serializers import ArticleSerializer, CommentSerializer, CategorySerializer, TagSerializer
from .filters import ArticleFilter, CategoryFilter, TagFilter
from .models import Article, Comment, Category, Tag
from .pagination import CustomPagination


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin | IsModerator]

    # Pagination, Filtering, and Search
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = CategoryFilter
    search_fields = ['name', 'description']

    def perform_create(self, serializer):
        if not self.request.user.has_approval:
            raise ValidationError("You are not approved to create Categories. Submit a request for approval.")
        serializer.save(author=self.request.user)

    # Override create method to handle validation and custom exceptions
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs) # Calls the parent class's create method
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin | IsModerator]

    # Pagination, Filtering, and Search
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = TagFilter
    search_fields = ['name']

    def perform_create(self, serializer):
        if not self.request.user.has_approval:
            raise ValidationError("You are not approved to create Tags. Submit a request for approval.")
        serializer.save(author=self.request.user)

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().order_by('-created_at')
    serializer_class = ArticleSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsModerator]

    # Pagination, Filtering, and Search
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ArticleFilter
    search_fields = ['title', 'content', 'category__name', 'tags__name']

    def perform_create(self, serializer):
        if not self.request.user.has_approval:
            raise ValidationError("You are not approved to write articles. Submit a request for approval.")
        try:
            serializer.save(author=self.request.user)
        except ValidationError as e:
            raise ValidationError({"message": str(e)})
        except Exception as ex:
            print(ex)
            raise ValidationError({"message": "An unexpected error occurred while creating the article."})
    
    # Override create method to handle validation and custom exceptions
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs) # Calls the parent class's create method
        except ValidationError as ex:
            return Response({
                "success": False,
                "message": str(ex)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            print(ex)
            return Response({
                "success": False,
                "message": "An unexpected error occurred."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    # Pagination, Filtering, and Search
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['article', 'author__email', 'author__first_name']  # Filtering on article and author details
    search_fields = ['content']  # Allows searching by comment's content

    def perform_create(self, serializer):
        try:
            serializer.save(author=self.request.user)
        except ValidationError as e:
            raise ValidationError({"message": str(e)})
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
            print(ex)
            return Response({
                "success": False,
                "message": "An unexpected error occurred."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Custom method to retrieve comments for a specific article
    @action(detail=True, methods=['get'])
    def article_comments(self, request, pk=None):
        article = get_object_or_404(Article, pk=pk)
        comments = self.queryset.filter(article=article)
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)
