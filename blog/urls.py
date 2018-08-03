from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from .views import PostViewSet, UserViewSet, api_root
from . import views

router = DefaultRouter()
router.register('posts', views.PostViewSet)
router.register('users', views.UserViewSet)

schema_view = get_schema_view(title='Pastebin API')

app_name='blog'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('Categories', views.CategoriesView.as_view(), name='categories'),
    path('Categories/<int:pk>/', views.CategoryView.as_view(), name='category'),
    path('Posts/<int:pk>/', views.PostView.as_view(), name='detail'),
    path('Search/', views.SearchView.as_view(), name='search'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('account', views.ProfileView.as_view(), name='profile_view'),
    path('new_post', views.CreatePostView.as_view(), name='new_post'),
    path('Posts/<int:pk>/edit', views.EditPostView.as_view(), name='edit'),
    path('Posts/<int:pk>/delete', views.DeletePostView.as_view(), name='delete'),
    path('api-auth', include('rest_framework.urls')),
    path('api', include(router.urls)),
    path('schema/', schema_view),
    path('api-root', views.api_root, name='apiroot'),
]
