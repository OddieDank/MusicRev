from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import Track, Comment, Like, Report

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'date_joined', 'is_active']
    list_filter = ['role', 'is_active', 'date_joined']
    search_fields = ['username', 'email']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role',)}),
    )


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'likes_count', 'comments_count', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'user__role']
    search_fields = ['title', 'description', 'user__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes'
    
    def comments_count(self, obj):
        return obj.comments.count()
    comments_count.short_description = 'Comments'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['track', 'user', 'content_short', 'created_at']
    list_filter = ['created_at', 'user__role']
    search_fields = ['content', 'user__username', 'track__title']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def content_short(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_short.short_description = 'Content'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['track', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'track__title']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['track', 'user', 'reason_short', 'created_at', 'is_resolved']
    list_filter = ['is_resolved', 'created_at', 'user__role']
    search_fields = ['reason', 'user__username', 'track__title']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    actions = ['mark_as_resolved']
    
    def reason_short(self, obj):
        return obj.reason[:50] + '...' if len(obj.reason) > 50 else obj.reason
    reason_short.short_description = 'Reason'
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
    mark_as_resolved.short_description = 'Mark selected reports as resolved'