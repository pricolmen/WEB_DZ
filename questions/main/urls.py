from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot_questions, name='hot_questions'),
    path('tag/<str:tag_name>/', views.questions_by_tag, name='questions_by_tag'),
    path('question/<int:question_id>/', views.question_detail, name='question'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path('ask/', views.ask_question, name='ask'),
    path('question/<int:question_id>/answer/', views.add_answer, name='add_answer'),
]