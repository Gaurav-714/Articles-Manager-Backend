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
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    author_email = serializers.EmailField(source='author.email', read_only=True)
    author_name = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['uid', 'title', 'content','author', 'author_email', 'author_name', 'category', 'tags', 'created_at', 'updated_at']
    
    def get_author_name(self, obj):
        # Concatenates first and last name to return full name
        return f"{obj.author.first_name} {obj.author.last_name}"
    
    def get_category(self, obj):
        # Returns the name of the category if available
        return obj.category.name if obj.category else None
    
    def get_tags(self, obj):
        # Returns the name of all tags
        return [tag.name if tag.name else "Unnamed Tag" for tag in obj.tags.all()]

    
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    author_email = serializers.EmailField(source='author.email', read_only=True)
    author_name = serializers.SerializerMethodField()
    article_title = serializers.CharField(source='article.title', read_only=True)

    class Meta:
        model = Comment
        fields = ['uid', 'comment', 'article', 'article_title', 'author', 'author_email', 'author_name', 'created_at', 'updated_at']
    
    def get_author_name(self, obj):
        # Returns the author's full name
        return f"{obj.author.first_name} {obj.author.last_name}" if obj.author else "Unknown Author"
