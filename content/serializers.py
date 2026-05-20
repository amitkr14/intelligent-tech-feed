from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    # We add this read-only field to include our calculated recommendation score in the JSON
    total_score = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Article
        fields = ['id', 'title', 'source_name', 'source_url', 'summary', 'published_date', 'total_score']