from rest_framework import serializers
from .models import Forum

class ForumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forum
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')