from django_filters import rest_framework as filters
from .models import Article, Category, Tag

class ArticleFilter(filters.FilterSet):
    category = filters.CharFilter(field_name="category__name", lookup_expr="icontains")
    tag = filters.CharFilter(field_name="tags__name", lookup_expr="icontains")

    author_email = filters.CharFilter(field_name="author__email", lookup_expr="icontains")
    author_first_name = filters.CharFilter(field_name="author__first_name", lookup_expr="icontains")
    author_last_name = filters.CharFilter(field_name="author__last_name", lookup_expr="icontains")

    class Meta:
        model = Article
        fields = ['category', 'tags', 'author']


class CategoryFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    description = filters.CharFilter(field_name="description", lookup_expr="icontains")

    class Meta:
        model = Category
        fields = ['name', 'description']


class TagFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Tag
        fields = ['name']