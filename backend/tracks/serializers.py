from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Track, Comment, Like, Report

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    tracks_count = serializers.SerializerMethodField()
    total_likes_received = serializers.SerializerMethodField()
    total_comments_received = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'tracks_count', 'total_likes_received', 'total_comments_received', 'date_joined']
        read_only_fields = ['id', 'date_joined', 'role']
    
    def get_tracks_count(self, obj):
        return obj.tracks.count()
    
    def get_total_likes_received(self, obj):
        from django.db.models import Sum
        return obj.tracks.aggregate(total_likes=Sum('likes__id'))['total_likes'] or 0
    
    def get_total_comments_received(self, obj):
        from django.db.models import Sum
        return obj.tracks.aggregate(total_comments=Sum('comments__id'))['total_comments'] or 0


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']
        extra_kwargs = {
            'role': {'read_only': True}  # Los nuevos usuarios siempre son 'user'
        }
    
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializador para actualización de perfil de usuario"""
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'current_password', 'new_password']
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False}
        }
    
    def validate(self, data):
        # Si se quiere cambiar la contraseña, se requiere la contraseña actual
        if 'new_password' in data and 'current_password' not in data:
            raise serializers.ValidationError("Se requiere la contraseña actual para cambiar la contraseña")
        
        if 'current_password' in data and 'new_password' not in data:
            raise serializers.ValidationError("Se requiere una nueva contraseña")
        
        return data
    
    def validate_current_password(self, value):
        user = self.instance
        if not user.check_password(value):
            raise serializers.ValidationError("La contraseña actual es incorrecta")
        return value
    
    def update(self, instance, validated_data):
        # Actualizar contraseña si se proporciona
        if 'new_password' in validated_data:
            instance.set_password(validated_data['new_password'])
            validated_data.pop('new_password')
            validated_data.pop('current_password')
        
        return super().update(instance, validated_data)


    def create(self, validated_data):
        validated_data['role'] = 'user'  # Forzar rol de usuario normal
        user = User.objects.create_user(**validated_data)
        return user


class TrackSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Track
        fields = ['id', 'title', 'audio_file', 'description', 'user', 
                 'likes_count', 'comments_count', 'is_liked', 
                 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_active']
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'track', 'user', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'track', 'user', 'created_at']
        read_only_fields = ['id', 'created_at']


class ReportSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Report
        fields = ['id', 'track', 'user', 'reason', 'created_at', 'is_resolved']
        read_only_fields = ['id', 'created_at', 'is_resolved']


class ReportedTrackSerializer(serializers.ModelSerializer):
    """Serializador para tracks con reportes (panel admin)"""
    reports_count = serializers.SerializerMethodField()
    reports_detail = ReportSerializer(source='reports', many=True, read_only=True)
    user_username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = Track
        fields = ['id', 'title', 'user_username', 'description', 'created_at', 'is_active', 'reports_count', 'reports_detail']
    
    def get_reports_count(self, obj):
        return obj.reports.filter(is_resolved=False).count()