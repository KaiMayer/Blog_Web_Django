from django.urls import path
from .views import PostListView
from . import views

urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),
    path('post/<int:pk>/<slug:slug>/', views.post_detail, name='post-detail'),
    path('post/<int:pk>/<slug:slug>/comment_update/<int:comment_id>', views.edit_comment, name='edit_comment'),
    path('post/<int:pk>/<slug:slug>/comment_delete/<int:comment_id>', views.delete_comment, name='delete_comment'),
    path('about/', views.about, name='blog-about'),
    path('post/<int:pk>/<slug:slug>/post_comment/', views.post_comment,  name='post_comment'),
    path('search/', views.post_search, name='search'),
    path('directions/', views.directions, name='directions'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('ranking/', views.post_ranking, name='ranking'),

]
