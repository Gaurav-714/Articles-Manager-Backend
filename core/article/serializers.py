from rest_framework import serializers
from .models import Article, Comment, Category, Tag

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']  # Include the fields you need


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['uid', 'title', 'content', 'category', 'tags', 'created_at', 'updated_at']
    
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['uid', 'comment', 'article', 'created_at']