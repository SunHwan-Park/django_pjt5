from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout as auth_logout, get_user_model

from movies.models import Genre

from .models import User
from .forms import CustomUserCreationForm
# Create your views here.

def signup(request):
    if request.user.is_authenticated:
        return redirect('movies:index')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('movies:index')
    else:
        form = CustomUserCreationForm()
    context = {
        'form' : form
    }
    return render(request, 'accounts/form.html', context)

def login(request):
    if request.user.is_authenticated:
        return redirect('movies:index')

    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('movies:index')
    else:
        form = AuthenticationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/form.html', context)

@login_required
def logout(request):
    auth_logout(request)
    return redirect('movies:index')

@login_required
def add_genre(request):
    if request.method == 'POST':
        for i in range(1,len(request.POST)):
            value = request.POST.get(f'favorite_genre{i}','')
            if request.user.like_genres.all().filter(id__contains=value):
                continue
            else:
                request.user.like_genres.add(request.POST.get(f'favorite_genre{i}',''))
        return redirect('movies:index')
    else:
        genres = Genre.objects.all()
        context = {
            'genres' : genres,
        }
        return render(request, 'accounts/add_genre.html', context)

@login_required
def delete_genre(request):
    if request.method == 'POST':
        for i in range(1,len(request.POST)):
            value = request.POST.get(f'favorite_genre{i}','')
            if request.user.like_genres.all().filter(id__contains=value):
                request.user.like_genres.remove(request.POST.get(f'favorite_genre{i}',''))
            else:
                continue
        return redirect('movies:index')
    else:
        genres = request.user.like_genres.all()
        context = {
            'genres' : genres,
        }
        return render(request, 'accounts/delete_genre.html', context)