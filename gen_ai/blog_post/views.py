from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    BlogTitleSugggestionSerializer
)


class GetBlogTitleSugggestion(APIView):
    def post(self, request):
        serializer = BlogTitleSugggestionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

       
        data = {"message": "This is the result of perform_action."}
        return Response(data, status=status.HTTP_200_OK)


