from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.db.models import F
from .models import Movie, Genre
# Create your views here.

def index(request):
    if 'release_date' in request.POST:
        movies = Movie.objects.order_by('-release_date')
    elif 'popularity' in request.POST:
        movies = Movie.objects.order_by('-popularity')
    elif 'like' in request.POST:
        movies = Movie.objects.annotate(num_likes=Count('like_users')).order_by('-num_likes')
    else:
        movies = Movie.objects.order_by('-vote_average')

    paginator = Paginator(movies, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    genres = Genre.objects.all()

    if request.user.is_authenticated:
        if not request.user.like_genres.all().count():
            return redirect('accounts:add_genre')
        else:
            temp_recommend = Movie.objects.none()
            for genre in request.user.like_genres.all():
                temp_recommend = temp_recommend.union(genre.movies.all())
            movies_recommend = temp_recommend.order_by('-popularity')[:10]
    else:
        movies_recommend = Movie.objects.all().order_by('-popularity')[:10]

    context = {
        'movies': movies,
        'page_obj': page_obj,
        'movies_recommend' : movies_recommend,
    }
    return render(request, 'movies/index.html', context)

def movie_detail(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    context = {
        'movie' : movie,
    }
    return render(request, 'movies/movie_detail.html', context)

@login_required
def like(request, movie_pk):
    user = request.user
    movie = get_object_or_404(Movie, pk=movie_pk)

    if movie.like_users.filter(pk=user.pk).exists():
        movie.like_users.remove(user)
        liked = False
    else:
        movie.like_users.add(user)
        liked = True

    context = {
        'liked': liked,
        'count': movie.like_users.count()
    }
    return JsonResponse(context)