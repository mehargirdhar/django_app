from django.urls import path
from .views import (
    GetBlogTitleSugggestion
)

urlpatterns = [
    path('get-title-suggestions', GetBlogTitleSugggestion.as_view(), name='get_blog_title_suggestions'),
]
