from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('question/<int:question_id>/', views.question_detail, name='question'),
    path('ask/', views.ask_question, name='ask'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('tag/<str:tag_name>/', views.questions_by_tag, name='questions_by_tag'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
]