from django.urls import path
from .views import (
    GetBlogTitleSugggestion,
    blog_title_suggestion_view
)

urlpatterns = [
    path('blog-title-view', blog_title_suggestion_view, name='blog_title_view'),
    path('get-title-suggestions', GetBlogTitleSugggestion.as_view(), name='get_blog_title_suggestions'),
]
