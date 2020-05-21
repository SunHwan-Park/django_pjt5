# SSAFY_django_pjt5 [서울 / 3기 / 박선환]

- [프로젝트 흐름 정리](#프로젝트흐름정리)
- [새롭게 알게 된 점](#새롭게알게된점)
- [어려웠던 점](#어려웠던점)

# 프로젝트흐름정리

## 1. Start Project(CS50 IDE)

- `.gitignore` 생성

  ```bash
  $ touch .gitignore
  # www.gitignore.io => python, django, venv
  ```

- 가상환경 setting

  ```bash
  $ mkdir django_pjt5
  $ cd django_pjt5
  $ python -m venv venv
  $ source venv/bin/activate

  # 필요한 library 설치
  (venv) $ pip install --upgrade pip
  (venv) $ pip install django==2.1.15
  (venv) $ pip install django-bootstrap4
  (venv) $ pip install django-bootstrap-pagination
  ```

- startproject & startapp

  ```bash
  # 현재 위치(django_pjt5 폴더) 안에 바로 프로젝트 폴더 & manage.py 생성
  (venv) $ django-admin startproject django_pjt5 .
  # startapp
  (venv) $ python manage.py startapp accounts
  (venv) $ python manage.py startapp movies
  ```

- `django_pjt5/settings.py` 설정

  ```python
  ...
  DEBUG = False

  ALLOWED_HOSTS = ['*']

  INSTALLED_APPS = [
      # pip
      'bootstrap4',
      'bootstrap_pagination',
  	...
      # my app
      'accounts',
      'movies',
  ]

  TEMPLAGES = [{
      ...
      'DIRS': [os.path.join(BASE_DIR, 'templates')] # base.html 사용하기 위해
      ...
  }]

  LANGUAGE_CODE = 'ko-kr'
  TIME_ZONE = 'Asia/Seoul'

  AUTH_USER_MODEL = 'accounts.User' # Custom User 사용하기 위해
  ```



## 2. Model, Data & Form

- `movies/models.py`

  ```python
  from django.db import models
  from django.conf import settings

  class Genre(models.Model):
      name = models.CharField(max_length=100)

  class Movie(models.Model):
      title = models.CharField(max_length=100)
      original_title = models.CharField(max_length=100)
      release_date = models.DateField()
      popularity = models.FloatField()
      vote_count = models.IntegerField()
      vote_average = models.FloatField()
      adult = models.BooleanField()
      overview = models.TextField()
      original_language = models.CharField(max_length=100)
      poster_path = models.CharField(max_length=1000)
      backdrop_path = models.CharField(max_length=1000)
      # Genre와 Movie의 M:N 관계
      genres = models.ManyToManyField(Genre, related_name='movies')
      # User와 Movie의 M:N 관계(좋아요)
      like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_movies')
  ```

- `movies/admin.py`

  ```python
  from django.contrib import admin
  from .models import Movie, Genre

  admin.site.register(Movie)
  admin.site.register(Genre)
  ```

- `accounts/models.py`

  ```python
  from django.db import models
  from django.contrib.auth.models import AbstractUser
  from django.conf import settings
  from movies.models import Genre

  class User(AbstractUser):
      # Genre와 User의 M:N 관계(장르 선호 => 영화 추천 서비스)
      like_genres = models.ManyToManyField(Genre, related_name='like_users')
  ```

- `accounts/admin.py`

  ```python
  from django.contrib import admin
  from django.contrib.auth import get_user_model

  admin.site.register(get_user_model())
  ```

- Migration & Superuser

  ```bash
  (venv) $ python manage.py makemigrations
  (venv) $ python manage.py migrate
  (venv) $ python manage.py createsuperuser
  ```

- Json Data load

  ```bash
  # moviedata.json은 프로젝트 폴더 & manage.py와 같은 레벨에 있어야 한다.
  (venv) $ python manage.py loaddata moviedata.json
  ```

- `accounts/forms.py`

  ```python
  from django.contrib.auth.forms import UserCreationForm
  from django.contrib.auth import get_user_model

  class CustomUserCreationForm(UserCreationForm):
      class Meta(UserCreationForm.Meta):
          model = get_user_model()
  ```



## 3. URL

- `django_pjt5/urls.py`

  ```python
  from django.contrib import admin
  from django.urls import path, include
  from movies import views as movies_views

  urlpatterns = [
      path('admin/', admin.site.urls),
      path('accounts/', include('accounts.urls')),
      path('movies/', include('movies.urls')),
      path('', movies_views.index), # 도메인 페이지를 바로 /movies/로
  ]
  ```

- `accounts/urls.py`

  ```python
  from django.urls import path
  from . import views

  app_name = 'accounts'
  urlpatterns = [
      path('login/', views.login, name='login'),
      path('logout/', views.logout, name='logout'),
      path('signup/', views.signup, name='signup'),
      path('add_genre/', views.add_genre, name='add_genre'),
      path('delete_genre/', views.delete_genre, name='delete_genre'),
  ]
  ```

- `movies/urls.py`

  ```python
  from django.urls import path
  from . import views

  app_name = 'movies'
  urlpatterns = [
      path('', views.index, name='index'),
      path('<int:movie_pk>/', views.movie_detail, name='movie_detail'),
      path('<int:movie_pk>/like/', views.like, name='like'),
      ]
  ```



## 4. View & Template

### base.html

- bootstrap4 사용 위한 setting

  - {% load bootstrap4 %}
  - {% bootstrap_css %}
  - {% bootstrap_javascript jquery='full' %}

- `<head>`

  - fontawesome script
  - axios cdn script

- block

  ```html
  <body>
      <!-- navbar 구현 -->
  	{% block content %}
  	{% endblock %}
      <!-- footer 구현 -->
  </body>

  ```

- 사용자 인증여부에 따라 분기한 UI 구성

  ```html
  {% if user.is_authenticated %}
  {% else %}
  {% endif %}
  ```



### accounts app

- `accounts/views.py` - `import`

  ```python
  from django.shortcuts import render, redirect
  from django.contrib.auth.forms import AuthenticationForm
  from django.contrib.auth.decorators import login_required
  from django.contrib.auth import login as auth_login, logout as auth_logout, get_user_model

  from .models import User
  from .forms import CustomUserCreationForm
  from movies.models import Genre
  ```

- 회원가입

  ```python
  # accounts/views.py
  def signup(request):
      if request.user.is_authenticated: # 이미 로그인한 유저의 경우
          return redirect('movies:index')

      if request.method == 'POST': # 완성된 가입 form 제출
          form = CustomUserCreationForm(request.POST)
          if form.is_valid(): # 유효성 검증
              user = form.save()
              auth_login(request, user) # 가입과 동시에 로그인
              return redirect('movies:index')
      else:
          form = CustomUserCreationForm()
      context = {
          'form' : form
      }
      return render(request, 'accounts/form.html', context)
  ```

  ```html
  <!-- accounts/templates/accounts/form.html signup/login 공유!-->
  {% extends 'base.html' %}
  {% load bootstrap4 %}

  {% block content %}
  {% if request.resolver_match.url_name == "signup" %}
  <h1 class="text-center">Signup</h1>
  {% elif request.resolver_match.url_name == "login" %}
  <h1 class="text-center">Login</h1>
  {% endif %}
  <hr>
  <form method = "POST">
  {% csrf_token %}
  {% bootstrap_form form %}
  {% bootstrap_button "저장" button_type="submit" button_class="btn-primary" %}
  </form>
  {% endblock %}
  ```

- 로그인

  ```python
  # accounts/views.py
  def login(request):
      if request.user.is_authenticated: # 이미 로그인한 유저의 경우
          return redirect('movies:index')

      if request.method == 'POST': # 완성된 로그인 form 제출
          form = AuthenticationForm(request, request.POST)
          if form.is_valid(): # 유효성 검증
              user = form.get_user()
              auth_login(request, user) # 로그인
              return redirect('movies:index')
      else:
          form = AuthenticationForm()
      context = {
          'form': form,
      }
      return render(request, 'accounts/form.html', context)
  ```

- 로그아웃

  ```python
  # accounts/views.py
  @login_required
  def logout(request):
      auth_logout(request)
      return redirect('movies:index')
  ```

- 장르 선호 추가 / 삭제(영화 추천 서비스용)

  ```python
  # accounts/views.py
  @login_required
  def add_genre(request):
      if request.method == 'POST': # 완성된 장르 선호 form 제출
          for i in range(1,len(request.POST)):
              value = request.POST.get(f'favorite_genre{i}','')
              if request.user.like_genres.all().filter(id__contains=value):
                  # 이미 해당 장르를 선호하고 있을 때
                  continue
              else:
                  # 새롭게 선호 장르 추가
                 request.user.like_genres.add(request.POST.get(f'favorite_genre{i}',''))
          return redirect('movies:index')
      else: # 장르 선호 page로
          genres = Genre.objects.all()
          context = {
              'genres' : genres,
          }
          return render(request, 'accounts/add_genre.html', context)

  @login_required
  def delete_genre(request):
      if request.method == 'POST': # 완성된 장르 선호 form 제출
          for i in range(1,len(request.POST)):
              value = request.POST.get(f'favorite_genre{i}','')
              if request.user.like_genres.all().filter(id__contains=value):
                  # 선택한 장르 제거
                  request.user.like_genres.remove(request.POST.get(f'favorite_genre{i}',''))
              else:
                  continue
          return redirect('movies:index')
      else: # 장르 삭제 page로
          genres = request.user.like_genres.all()
          context = {
              'genres' : genres,
          }
          return render(request, 'accounts/genre.html', context)
  ```

  ```html
  <!-- accounts/templates/accounts/genre.html => add/delete 공유! -->
  {% extends 'base.html' %}
  {% load bootstrap4 %}

  {% block content %}
  <div class="d-flex flex-column align-items-center my-5">
    {% if request.resolver_match.url_name == "add_genre" %} <!-- url별 조건 분기 -->
    <h1 class="text-center">선호하는 장르를 골라주세요!</h1>
    {% elif request.resolver_match.url_name == "delete_genre" %}
    <h1 class="text-center">지우고 싶은 장르를 골라주세요!</h1>
    {% endif %}
    {% if request.user.like_genres.first %} <!-- 장르 선호가 있다면 -->
    <h3>현재 {{ request.user.username }}님이 선호하는 장르</h3>
    <strong>
      /
      {% for genre in request.user.like_genres.all %} <!-- 사용자 선호 장르 순회 -->
        {{ genre.name }} /
      {% endfor %}
    </strong>
    {% endif %}
    <div class="d-flex flex-column align-items-center w-25 my-3">
      {% bootstrap_button "장르 선택, 묻고 더블로가!" id='addSelector' button_type="submit" button_class="btn-info" %} <!-- 클릭하면 select tag를 하나씩 추가 -->
    </div>
    <div>
      <form action="" method="POST" class="d-flex flex-column align-items-center">
        {% csrf_token %}
        <div id='sendForm'>
          <select class="select ml-1" name="favorite_genre1">
            {% for genre in genres %}
              <option value={{ genre.pk }}>{{ genre.name }}</option>
            {% endfor %}
          </select>
        </div>
        <hr>
        <div>
          {% bootstrap_button "저장" button_type="submit" button_class="btn-primary" %}
        </div>
      </form>
    </div>
  </div>

  <script>
      let counter = 2
      const addSelector = document.querySelector('#addSelector')
      const sendForm = document.querySelector('#sendForm')
      addSelector.addEventListener('click', function(e) {
          let selectorForm = document.createElement('select')
          selectorForm.setAttribute('name', `favorite_genre${counter}`) // 번호 매겨주기
          selectorForm.classList.add('m-1')
          counter += 1
          let optionForm = null
          {% for genre in genres %} // 장르 순회하면서 옵션 추가
            optionForm = document.createElement('option')
            optionForm.setAttribute('value', '{{ genre.pk }}')
            optionForm.innerText = '{{ genre.name }}'
            selectorForm.appendChild(optionForm)
          {% endfor %}
          sendForm.appendChild(selectorForm)
      })
  </script>
  {% endblock %}
  ```



### movies.app

- `movies.views.py` - `import`

  ```python
  from django.shortcuts import render, redirect, get_object_or_404
  from django.core.paginator import Paginator
  from django.http import JsonResponse
  from django.db.models import Count
  from django.contrib.auth.decorators import login_required
  from .models import Movie, Genre
  ```

- 메인 페이지(추천 영화, 영화 리스트)

  ```python
  # movies/views.py
  def index(request):
      if 'release_date' in request.POST:
          movies = Movie.objects.order_by('-release_date')  # 최신순 정렬
      elif 'popularity' in request.POST:
          movies = Movie.objects.order_by('-popularity')  # 인기순 정렬
      elif 'like' in request.POST:
          movies = Movie.objects.annotate(num_likes=Count('like_users')).order_by('-num_likes')  # 좋아요순 정렬
      else:
          movies = Movie.objects.order_by('-vote_average') # 평점순 정렬

      paginator = Paginator(movies, 9) # 한 페이지당 9개의 영화 노출
      page_number = request.GET.get('page')
      page_obj = paginator.get_page(page_number)

      if request.user.is_authenticated: # 로그인 한 경우에만
          if not request.user.like_genres.all().count(): # 아직 장르 선택을 하지 않았다면
              return redirect('accounts:add_genre') # 장르 선택 페이지로 이동
          else:
              temp_recommend = Movie.objects.none() # 빈 QuerySet(Movie 모델 스키마)
              for genre in request.user.like_genres.all(): # 사용자 선호 장르마다 영화 추가
                  temp_recommend = temp_recommend.union(genre.movies.all())
              movies_recommend = temp_recommend.order_by('-popularity')[:10] # 인기도순
      else: # 로그인 하지 않은 경우 전체 영화 인기도 순으로 추천
          movies_recommend = Movie.objects.all().order_by('-popularity')[:10]

      context = {
          'movies': movies,
          'page_obj': page_obj,
          'movies_recommend' : movies_recommend,
      }
      return render(request, 'movies/index.html', context)
  ```

  ```html
  <!-- movies/templates/movies/index.html -->
  <!--
  1. 추천 영화 리스트(carousel로 구현)
  2. 영화 리스트
    - 정렬 버튼(평점순/인기순/좋아요순/최신순)
    - 페이지당 9개의 영화를 한 줄에 3개 씩 배치하여 노출(card로 구현)
    - card
  	- 포스터 사진
  	- 제목
  	- 평점
  	- 인기도
  	- 개봉일
  	- 장르
  	- 좋아요 버튼 & 좋아요수
  	  - JS로 좋아요 구현
    - pagination
  -->

  {% extends 'base.html' %}
  {% load bootstrap_pagination %}

  {% block content %}
  <!-- ...(생략) -->
  <script>
      // 좋아요 기능 구현을 위한 JS
      const likeButtonList = document.querySelectorAll('.like-buttons')
      likeButtonList.forEach(likeButton => {
        likeButton.addEventListener('click', e => {
          const movieID = e.target.dataset.id
          {% if user.is_authenticated %}
          axios.get(`/movies/${movieID}/like/`)
            .then(res => {
              if (res.data.liked) {
                e.target.style.color = 'crimson'
              } else {
                e.target.style.color = 'black'
              }
              document.querySelector(`#like-count-${movieID}`).innerText = res.data.count
            })
          {% else %}
            alert('비로그인 사용자는 좋아요를 누를 수 없습니다.')
          {% endif %}
        })
      })
  </script>
  {% endblock %}
  ```

- 영화 디테일 정보 페이지

  ```python
  # movies/views.py
  def movie_detail(request, movie_pk):
      movie = get_object_or_404(Movie, pk=movie_pk)
      context = {
          'movie' : movie,
      }
      return render(request, 'movies/movie_detail.html', context)
  ```

  ```html
  <!-- movies/templates/movies/movie_detail.html -->
  <!--
  1. 영화 상세정보
    - 포스터 사진
    - 제목
    - 원제
    - 개봉일
    - 투표 인원
    - 평점
    - 인기도
    - 장르
    - 좋아요 버튼 & 좋아요수(좋아요 하는 유저 1명 이름 노출)
  	- JS로 좋아요 구현
  -->

  {% extends 'base.html' %}
  {% load bootstrap4 %}
  {% block content %}
  <!-- ...(생략) -->
  <!-- 좋아요 버튼 & 좋아요수(좋아요 하는 유저 1명 이름 노출) 구현 -->
  {% if user in movie.like_users.all %}
    <i class="fas fa-heart fa-lg like-buttons" style="color:crimson" data-id="{{ movie.pk }}"></i>
    <span>{{ user.username }}님을 비롯한 </span>
  {% else %}
    <i class="fas fa-heart fa-lg like-buttons" style="color:black" data-id="{{ movie.pk }}"></i>
    {% if movie.like_users.first %}
  	<span>{{ movie.like_users.first }}님을 비롯한 </span>
    {% endif %}
  {% endif %}
  <span id="like-count-{{ movie.pk }}">{{ movie.like_users.all|length }}</span>명이 이 영화를 좋아합니다.
  <!-- ...(생략) -->
  ```

- 영화 좋아요

  ```python
  # movies/views.py
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
  ```



## 5. Deploy app

### heroku 배포

1. heroku 로그인

   ```bash
   (venv) $ heroku login -i
   ```

2. 필요한 패키지 설치

   ```bash
   (venv) $ pip install dj-database-url gunicorn whitenoise
   ```

3. `Procfile`

   ```bash
   web: gunicorn django_pjt5.wsgi --log-file -
   ```

4. `requirements.txt`

   ```bash
   (venv) $ pip freeze > requirements.txt
   ```

   - `requirements.txt`에 `psycopg2` 패키지 추가

5. `runtime.txt`

   ```
   python-3.7.6
   ```

6. `django_pjt5/settings.py`

   - DB 관련

     ```python
     # Heroku: Update database configuration from $DATABASE_URL.
     import dj_database_url
     db_from_env = dj_database_url.config(conn_max_age=500)
     DATABASES['default'].update(db_from_env)
     ```

   - static 파일 관련

     ```python
     # Static files (CSS, JavaScript, Images)
     # https://docs.djangoproject.com/en/2.0/howto/static-files/

     # The absolute path to the directory where collectstatic will collect static files for deployment.
     STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

     # The URL to use when referring to static files (where they will be served from)
     STATIC_URL = '/static/'
     ```

   - MIDDLEWARE

     ```python
     MIDDLEWARE = [
         'django.middleware.security.SecurityMiddleware',
         'whitenoise.middleware.WhiteNoiseMiddleware', # 추가하기
         'django.contrib.sessions.middleware.SessionMiddleware',
         'django.middleware.common.CommonMiddleware',
         'django.middleware.csrf.CsrfViewMiddleware',
         'django.contrib.auth.middleware.AuthenticationMiddleware',
         'django.contrib.messages.middleware.MessageMiddleware',
         'django.middleware.clickjacking.XFrameOptionsMiddleware',
     ]
     ```

   - STATICFILES_STORAGE

     ```python
     # Simplified static file serving.
     # https://warehouse.python.org/project/whitenoise/
     STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
     ```

7. git versioning

   ```bash
   (venv) $ git init
   (venv) $ git add .
   (venv) $ git commit -m "first commit"
   ```

8. heroku 앱 생성 및 git push

   ```bash
   (venv) $ heroku create twoparkstears # 앱이름 정해서 생성
   (venv) $ git push heroku master # git push
   ```

9. heroku migration/createsuperuser

   - heroku로 처음 앱을 올리면서 DB 정보가 사라지기 때문에 새롭게 migration을 진행해줘야 한다.

   ```bash
   (venv) $ heroku run python manage.py migrate
   (venv) $ heroku run python manage.py createsuperuser
   ```

   - 이 파트를 heroku site에서 진행할 수 있다.
     - Open app 버튼 옆에 More - Run console



# 새롭게알게된점

### loaddata

- `python manage.py loaddata [data]`
- data는 프로젝트 폴더 & manage.py와 같은 레벨에 있어야 한다.



### AJAX 요청 사용한 좋아요 기능 구현

- ```python
  # movies/views.py
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
  ```

- ```html
  <!-- movies/templates/movies/index.html -->
  {% if user in movie.like_users.all %}
    <i class="fas fa-heart fa-lg like-buttons" style="color:crimson" data-id="{{ movie.pk }}"></i>
  {% else %}
    <i class="fas fa-heart fa-lg like-buttons" style="color:black" data-id="{{ movie.pk }}"></i>
  {% endif %}
  <span id="like-count-{{ movie.pk }}">{{ movie.like_users.all|length }}</span>명이 이 영화를 좋아합니다.

  <script>
      // 좋아요 기능 구현을 위한 JS
      const likeButtonList = document.querySelectorAll('.like-buttons')
      likeButtonList.forEach(likeButton => {
        likeButton.addEventListener('click', e => {
          const movieID = e.target.dataset.id
          {% if user.is_authenticated %}
          axios.get(`/movies/${movieID}/like/`)
            .then(res => {
              if (res.data.liked) {
                e.target.style.color = 'crimson'
              } else {
                e.target.style.color = 'black'
              }
              document.querySelector(`#like-count-${movieID}`).innerText = res.data.count
            })
          {% else %}
            alert('비로그인 사용자는 좋아요를 누를 수 없습니다.')
          {% endif %}
        })
      })
  </script>
  ```



### 영화 추천 서비스 구현

> 유저별 장르 선호도를 알아내고, 이를 바탕으로 해당 장르의 인기 있는 영화 반환

- 유저가 가입 후 처음 메인 페이지에 접근했을 때, 특정한 페이지(장르 선호 설문) 넘겨주는 것

- 해당 유저가 좋아하는 장르의 영화만 추출 => 인기도 기준으로 내림차순 정렬

  ```python
  # movies/views.py => index
  if request.user.is_authenticated: # 로그인 한 경우에만
      if not request.user.like_genres.all().count(): # 아직 장르 선택을 하지 않았다면
          return redirect('accounts:add_genre') # 장르 선택 페이지로 이동
      else:
          temp_recommend = Movie.objects.none() # 빈 QuerySet(Movie 모델 스키마)
          for genre in request.user.like_genres.all(): # 사용자 선호 장르마다 영화 추가
              temp_recommend = temp_recommend.union(genre.movies.all())
              movies_recommend = temp_recommend.order_by('-popularity')[:10] # 인기도순
  else: # 로그인 하지 않은 경우 전체 영화 인기도 순으로 추천
      movies_recommend = Movie.objects.all().order_by('-popularity')[:10]
  ```

- 선호 장르 선택(추가, 삭제)

  - 한 페이지에서 여러 개의 장르 선택 가능

    - form / select / option & Javascript 활용
      - select
        - 드롭다운 형태의 선택 input
        - name
      - option
        - select 안에 개별 선택지
        - value
      - subbit 했을 때 넘겨주는 url에서 `?name1=value1&name2=value2` 형태로 전달된다.

  - 처음 선택 이후에도, 장르 추가 & 장르 삭제 가능

    ```python
    # accounts/views.py
    @login_required
    def add_genre(request):
        if request.method == 'POST': # 완성된 장르 선호 form 제출
            for i in range(1,len(request.POST)):
                value = request.POST.get(f'favorite_genre{i}','')
                if request.user.like_genres.all().filter(id__contains=value):
                    # 이미 해당 장르를 선호하고 있을 때
                    continue
                else:
                    # 새롭게 선호 장르 추가
                   request.user.like_genres.add(request.POST.get(f'favorite_genre{i}',''))
            return redirect('movies:index')
        else: # 장르 선호 page로
            genres = Genre.objects.all()
            context = {
                'genres' : genres,
            }
            return render(request, 'accounts/add_genre.html', context)

    @login_required
    def delete_genre(request):
        if request.method == 'POST': # 완성된 장르 선호 form 제출
            for i in range(1,len(request.POST)):
                value = request.POST.get(f'favorite_genre{i}','')
                if request.user.like_genres.all().filter(id__contains=value):
                    # 선택한 장르 제거
                    request.user.like_genres.remove(request.POST.get(f'favorite_genre{i}',''))
                else:
                    continue
            return redirect('movies:index')
        else: # 장르 삭제 page로
            genres = request.user.like_genres.all()
            context = {
                'genres' : genres,
            }
            return render(request, 'accounts/genre.html', context)
    ```



### 컨텐츠 정렬

- 정렬 버튼(버튼 그룹) - 각 버튼 별 name 활용해 데이터 넘겨준다.

  ```html
  <div class="btn-group mb-3" role="group">
      <button id="btnGroupDrop1" type="button" class="btn border-info text-secondary dropdown-toggle mb-1" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
          정렬
      </button>
      <form action="{% url 'movies:index' %}" method="POST">
          <div class="dropdown-menu p-0" aria-labelledby="btnGroupDrop1" style="width:10px">
              {% csrf_token %}
              <button class="dropdown-item text-secondary text-center" type="submit" name="rank">평점순</button>
              <button class="dropdown-item text-secondary text-center" type="submit" name="popularity">인기순</button>
              <button class="dropdown-item text-secondary text-center" type="submit" name="like">좋아요순</button>
              <button class="dropdown-item text-secondary text-center" type="submit" name="release_date">최신순</button>
          </div>
      </form>
  </div>
  ```

- 넘어온 name 데이터에 따라 영화 목록 정렬

  ```python
  # movies/views.py
  def index(request):
      if 'release_date' in request.POST:
          movies = Movie.objects.order_by('-release_date')  # 최신순 정렬
      elif 'popularity' in request.POST:
          movies = Movie.objects.order_by('-popularity')  # 인기순 정렬
      elif 'like' in request.POST:
          movies = Movie.objects.annotate(num_likes=Count('like_users')).order_by('-num_likes')  # 좋아요순 정렬
      else:
          movies = Movie.objects.order_by('-vote_average') # 평점순 정렬
      #...(생략)
  ```



### `django-bootstrap-pagination` 활용

- 설치 : `$ pip install django-bootstrap-pagination`

- `settings.py` - `INSTALLED_APPS` : `'bootstrap_pagination'`

- `views.py`

  ```python
  from django.core.paginator import Paginator

  # movies/views.py
  def index(request):
      # ...(생략)
      paginator = Paginator(movies, 9) # 한 페이지당 9개의 영화 노출
      page_number = request.GET.get('page')
      page_obj = paginator.get_page(page_number)
  	# ...(생략)
      context = {
          'movies': movies,
          'page_obj': page_obj,
          'movies_recommend' : movies_recommend,
      }
      return render(request, 'movies/index.html', context)
  ```

- `html`

  ```html
  {% bootstrap_paginate page_obj range=10 show_prev_next="false" show_first_last="true" %}
  <div class="pagination">
    <span class="step-links">
        {% if page_obj.has_previous %}
            <a href="?page=1">&laquo; first</a>
            <a href="?page={{ page_obj.previous_page_number }}">previous</a>
        {% endif %}
    </span>
  </div>
  ```



# 어려웠던점

- 영화 추천 서비스를 위해 사용자 선호 장르 데이터를 얻어내는 과정을 구현할 때, 고려해야할 부분이 적지 않았다.
  - 어느 시점에 설문을 할 것인지
  - 최초 설정 이후에도 업데이트를 가능하게 할 것인지
  - 설문 페이지는 어떤 식으로 구현할 지
    - 장르 리스트를 어떤 형태로 노출 시킬 지
    - 선호하는 장르는 어떤 행위를 통해 고를 수 있나
    - 선호하는 장르는 몇 개까지 고를 수 있나
- allauth 사용법
  - 승인된 도메인 설정을 어떻게 해야 하는가....
- 역시나 배포는 낯설고 어렵다
  - error code h10
  - error code h14