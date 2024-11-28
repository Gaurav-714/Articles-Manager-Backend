from rest_framework import serializers
from .models import Article, Comment

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['uid', 'title', 'content', 'category', 'tags', 'created_at', 'updated_at']
    
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['uid', 'comment', 'article', 'created_at']