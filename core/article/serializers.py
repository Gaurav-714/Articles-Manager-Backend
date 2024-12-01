from rest_framework import serializers
from .models import Article, Comment, Category, Tag

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    author_email = serializers.EmailField(source='author.email', read_only=True)
    author_name = serializers.SerializerMethodField()

    category = serializers.SlugRelatedField(queryset=Category.objects.all(), slug_field='name')
    tags = serializers.SlugRelatedField(queryset=Tag.objects.all(), slug_field='name', many=True)

    class Meta:
        model = Article
        fields = ['uid', 'title', 'content', 'author', 'author_email', 'author_name', 'category', 'tags', 'created_at', 'updated_at']

    def get_author_name(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}"

    # Override validate_category to handle category creation
    def validate_category(self, value):
        # Ensure category is created if it doesn't exist
        category_obj, created = Category.objects.get_or_create(name=value)
        return category_obj  # No need to unpack, directly return the object

    # Override validate_tags to handle tag creation
    def validate_tags(self, value):
        # Ensure each tag is created if it doesn't exist
        tag_objects = []
        for tag_name in value:
            tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
            tag_objects.append(tag_obj)
        return tag_objects

    def create(self, validated_data):
        category = validated_data.pop('category')
        tags = validated_data.pop('tags')

        # Create the article and associate the category
        article = Article.objects.create(category=category, **validated_data)

        # Associate tags with the article
        article.tags.set(tags)  # Add the tags to the article
        article.save()

        return article


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
