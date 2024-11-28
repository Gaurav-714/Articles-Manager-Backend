from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['uid', 'title', 'content', 'category', 'tags', 'author', 'created_at', 'updated_at']