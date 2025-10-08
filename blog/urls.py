from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('post/new/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/update/', views.PostUpdateView.as_view(), name='post_update'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('posts/', views.PostListView.as_view(), name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.PostDetailView.as_view(), name='post_detail'),
    path('author/<str:username>/', views.AuthorPostListView.as_view(), name='author_posts'),
    path('category/<slug:slug>/', views.CategoryPostListView.as_view(), name='category_posts'),
    path('search/', views.search, name='search'),
    path('drafts/', views.DraftListView.as_view(), name='draft_list'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
]