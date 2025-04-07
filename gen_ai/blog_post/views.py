from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    BlogTitleSugggestionSerializer
)
from .services import create_title_suggestions


class GetBlogTitleSugggestion(APIView):
    def post(self, request):
        try:
            serializer = BlogTitleSugggestionSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    data={"status": False, "message":serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            suggestions = create_title_suggestions(
                blog=request.data.get('blog_content'),
                num_of_suggestion=request.data.get('number_of_suggestions')
            )

            data = {"data":suggestions, "message": "successfull", "status":True}
            return Response(data=data, status=status.HTTP_200_OK)
        
        except Exception as error:

            return Response(
                data={"status": False, "message":str(error)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
def blog_title_suggestion_view(request):
    return render(request, 'blog.html')



