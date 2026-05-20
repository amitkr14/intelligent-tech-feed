import requests
from celery import shared_task
from django.db import IntegrityError
from .models import Article
from datetime import datetime

@shared_task
def fetch_devto_articles():
    print("Fetching latest articles from Dev.to...")
    
    # The Dev.to API endpoint (fetching the 10 most recent articles)
    url = "https://dev.to/api/articles?per_page=10"
    response = requests.get(url)
    
    if response.status_code != 200:
        return "Failed to fetch data from API"
        
    articles_data = response.json()
    saved_count = 0
    
    for item in articles_data:
        # 1. Check if the article already exists to save database operations
        if not Article.objects.filter(source_url=item['url']).exists():
            try:
                # 2. Save the new article to our PostgreSQL database
                Article.objects.create(
                    title=item['title'],
                    source_name="Dev.to",
                    source_url=item['url'],
                    summary=item['description'],
                    published_date=item['published_at'] # API returns ISO format which Django parses automatically
                )
                saved_count += 1
            except IntegrityError:
                # 3. If two workers try to save the same article at the exact same millisecond,
                # the database's unique constraint (our url_hash) will trigger an IntegrityError.
                # We catch it gracefully and move on.
                pass
                
    result_msg = f"Successfully fetched and saved {saved_count} new articles!"
    print(result_msg)
    return result_msg