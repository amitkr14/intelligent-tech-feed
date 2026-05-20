from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from .models import Article
from .serializers import ArticleSerializer
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required


def home_page(request):
    # This simply looks in your templates folder and sends index.html to the browser
    return render(request, 'index.html')

class RecommendationAPIView(APIView):
    # Ensure only logged-in users can get recommendations
    permission_classes = [IsAuthenticated] 
    
    def get(self, request):
        # For testing purposes, we will hardcode 'amit_reader' since we don't have JWT auth setup yet.
        # In production, this would be: user = request.user
        from django.contrib.auth.models import User
        user = request.user
        
        # 1. Create a unique cache key for THIS specific user
        cache_key = f"recommendations_user_{user.id}"
        
        # 2. Try to get the data from Redis
        cached_data = cache.get(cache_key)
        
        if cached_data:
            print("CACHE HIT! Serving from Redis...")
            return Response(cached_data)
            
        print("CACHE MISS! Querying Database...")
        # 3. If not in cache, run our heavy algorithm
        recommended_articles = Article.objects.get_recommendations_for(user)[:10] # Top 10
        serializer = ArticleSerializer(recommended_articles, many=True)
        
        # 4. Save the JSON result to Redis for 15 minutes (900 seconds)
        cache.set(cache_key, serializer.data, timeout=900)
        
        return Response(serializer.data)
    


# 1. Protect the home page so only logged-in users can see it
@login_required(login_url='/login/')
def home_page(request):
    return render(request, 'index.html')

# 2. Create the Registration View
def register_page(request):
    # If the user is already logged in, redirect them home
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Automatically log the user in after they register
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
        
    return render(request, 'register.html', {'form': form})    