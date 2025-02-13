from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Forum, ForumMember, Message
import requests

class SimpleMemberSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    username = serializers.CharField(source='user.username')
    
    class Meta:
        model = ForumMember
        fields = ['id', 'email', 'username', 'role', 'status', 'joined_at']

class ForumMemberSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    username = serializers.CharField(read_only=True)
    
    class Meta:
        model = ForumMember
        fields = ['id', 'email', 'username', 'role', 'status', 'joined_at']
        read_only_fields = ['joined_at', 'status']

    def validate_email(self, value):
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Requête non disponible")

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise serializers.ValidationError("Token d'authentification manquant")

        headers = {'Authorization': auth_header}
        try:
            response = requests.get(
                f'https://rajapi-cop-auth-api-33be22136f5e.herokuapp.com/auth/profile/',
                params={'email': value},
                headers=headers
            )
            
            if response.status_code != 200:
                raise serializers.ValidationError("Impossible de vérifier l'utilisateur")
            
            user_data = response.json()
            if not user_data:
                raise serializers.ValidationError("Utilisateur non trouvé")
                
            return value
        except requests.RequestException as e:
            raise serializers.ValidationError(f"Erreur lors de la vérification de l'utilisateur: {str(e)}")

class ForumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forum
        fields = ['id', 'title', 'description', 'category', 'status', 'created_at', 'updated_at']
        read_only_fields = ('created_by', 'created_at', 'updated_at')

class ForumDetailSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    active_members_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Forum
        fields = ['id', 'title', 'description', 'category', 'status', 
                 'created_at', 'updated_at', 'members', 'active_members_count']

    def get_members(self, obj):
        members = obj.forummember_set.select_related('user').filter(status='active')
        return SimpleMemberSerializer(members, many=True).data

    def get_active_members_count(self, obj):
        return obj.forummember_set.filter(status='active').count()

class MessageSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'content', 'author_username', 'author', 'created_at', 'updated_at', 'is_edited']
        read_only_fields = ['author', 'created_at', 'updated_at', 'is_edited']