from django.db import models
import hashlib
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import Coalesce


class ArticleManager(models.Manager):
    def get_recommendations_for(self, user):
        # 1. Get a list of IDs for articles the user has already interacted with
        interacted_ids = user.interactions.values_list('article_id', flat=True)
        
        # 2. Query the database for unread articles, sum up their total interaction 
        # scores from other users, and order them by the highest score.
        return self.exclude(id__in=interacted_ids).annotate(
            total_score=Coalesce(Sum('interactions__weight'), 0)
        ).order_by('-total_score', '-published_date')

class Article(models.Model):
    title = models.CharField(max_length=500)
    source_name = models.CharField(max_length=100) # e.g., "TechCrunch", "Dev.to"
    source_url = models.URLField(max_length=1000, unique=True)
    summary = models.TextField(blank=True, null=True)
    published_date = models.DateTimeField()
    
    # We use a hash to quickly check for duplicates before inserting
    url_hash = models.CharField(max_length=64, unique=True, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ArticleManager()

    def save(self, *args, **kwargs):
        # Automatically generate a unique hash based on the URL before saving
        if not self.url_hash:
            self.url_hash = hashlib.sha256(self.source_url.strip().lower().encode('utf-8')).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.source_name}: {self.title}"
    

class UserInteraction(models.Model):
    # Mapping system interactions to weights for quantitative scoring
    INTERACTION_CHOICES = (
        ('VIEW', 1),
        ('LIKE', 3),
        ('BOOKMARK', 5),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=10, choices=[(c[0], c[0]) for c in INTERACTION_CHOICES])
    weight = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A user shouldn't have duplicate raw interaction rows for the exact same action type on an article
        unique_together = ('user', 'article', 'interaction_type')

    def save(self, *args, **kwargs):
        # Automatically assign scoring weight metric based on choice type mapping
        weights_dict = dict(self.INTERACTION_CHOICES)
        self.weight = weights_dict.get(self.interaction_type, 1)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.interaction_type} - {self.article.title[:30]}"    