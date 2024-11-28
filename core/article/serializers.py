from rest_framework import serializers
from .models import Article, Comment

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['uid', 'title', 'content', 'category', 'tags', 'author', 'created_at', 'updated_at']
    
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['uid', 'comment', 'article', 'author', 'created_at']