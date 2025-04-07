from rest_framework import serializers

class BlogTitleSugggestionSerializer(serializers.Serializer):
    number_of_suggestions = serializers.IntegerField(max_value=5)
    blog_content = serializers.CharField()