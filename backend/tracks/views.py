from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Track, Comment, Like, Report
from .serializers import (
    TrackSerializer, CommentSerializer, LikeSerializer, 
    ReportSerializer, UserSerializer, UserRegistrationSerializer,
    UserProfileUpdateSerializer, ReportedTrackSerializer
)
from .permissions import IsOwnerOrAdmin, IsAuthenticatedForWrite, IsAdminOnly

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de usuarios.
    Registro público, gestión de usuarios por admin.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOnly]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action in ['update_profile', 'profile']:
            return UserProfileUpdateSerializer
        return UserSerializer
    
    @action(detail=False, methods=['post'], permission_classes=[])
    def register(self, request):
        """Registro de nuevos usuarios - acceso público"""
        data = request.data.copy()
        serializer = UserRegistrationSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticatedForWrite])
    def profile(self, request):
        """Ver perfil del usuario autenticado"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'], permission_classes=[IsAuthenticatedForWrite])
    def update_profile(self, request):
        """Actualizar perfil del usuario autenticado"""
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticatedForWrite])
    def my_tracks(self, request):
        """Ver tracks del usuario autenticado"""
        tracks = request.user.tracks.all()
        serializer = TrackSerializer(tracks, many=True)
        return Response(serializer.data)


class TrackViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de tracks.
    - Todos pueden ver (incluye guests)
    - Usuarios autenticados pueden crear
    - Solo propietario o admin pueden editar/eliminar
    """
    queryset = Track.objects.filter(is_active=True)
    serializer_class = TrackSerializer
    permission_classes = [IsOwnerOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'user__username']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filtrar por usuario si se especifica"""
        queryset = Track.objects.filter(is_active=True)
        user_id = self.request.query_params.get('user', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset
    
    def perform_create(self, serializer):
        """Asignar el usuario actual al track"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Obtener comentarios de un track"""
        track = self.get_object()
        comments = track.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticatedForWrite])
    def like(self, request, pk=None):
        """Dar/quitar like a un track"""
        track = self.get_object()
        like, created = Like.objects.get_or_create(
            track=track,
            user=request.user
        )
        
        if not created:
            # Si ya existe, eliminar el like (toggle)
            like.delete()
            return Response({'liked': False}, status=status.HTTP_200_OK)
        
        return Response({'liked': True}, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticatedForWrite])
    def unlike(self, request, pk=None):
        """Quitar like de un track"""
        track = self.get_object()
        try:
            like = Like.objects.get(track=track, user=request.user)
            like.delete()
            return Response({'liked': False}, status=status.HTTP_200_OK)
        except Like.DoesNotExist:
            return Response({'error': 'No has dado like a este track'}, 
                          status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticatedForWrite])
    def report(self, request, pk=None):
        """Reportar un track"""
        track = self.get_object()
        reason = request.data.get('reason', '')
        
        if not reason:
            return Response({'error': 'Se requiere una razón para el reporte'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si ya reportó este track
        if Report.objects.filter(track=track, user=request.user).exists():
            return Response({'error': 'Ya has reportado este track'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        report = Report.objects.create(
            track=track,
            user=request.user,
            reason=reason
        )
        
        serializer = ReportSerializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminOnly])
    def reported(self, request):
        """Ver tracks reportados (solo admin)"""
        reported_tracks = Track.objects.filter(reports__is_resolved=False).distinct()
        serializer = ReportedTrackSerializer(reported_tracks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['put'], permission_classes=[IsAdminOnly])
    def deactivate(self, request, pk=None):
        """Desactivar un track (solo admin)"""
        track = self.get_object()
        track.is_active = False
        track.save()
        
        # Marcar reportes como resueltos
        track.reports.update(is_resolved=True)
        
        return Response({'deactivated': True, 'message': 'Track desactivado y reportes resueltos'})
    
    @action(detail=True, methods=['put'], permission_classes=[IsAdminOnly])
    def resolve_reports(self, request, pk=None):
        """Resolver todos los reportes de un track (solo admin)"""
        track = self.get_object()
        track.reports.update(is_resolved=True)
        return Response({'resolved': True, 'message': 'Reportes resueltos'})


class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de reportes (solo admin).
    """
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAdminOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'is_resolved']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filtrar reportes no resueltos por defecto"""
        queryset = Report.objects.all()
        resolved = self.request.query_params.get('resolved', None)
        if resolved is not None:
            if resolved.lower() == 'true':
                queryset = queryset.filter(is_resolved=True)
            elif resolved.lower() == 'false':
                queryset = queryset.filter(is_resolved=False)
        return queryset
    
    @action(detail=True, methods=['put'])
    def resolve(self, request, pk=None):
        """Marcar reporte como resuelto"""
        report = self.get_object()
        report.is_resolved = True
        report.save()
        
        serializer = self.get_serializer(report)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estadísticas de reportes"""
        from django.db.models import Count
        
        total_reports = Report.objects.count()
        unresolved_reports = Report.objects.filter(is_resolved=False).count()
        resolved_reports = Report.objects.filter(is_resolved=True).count()
        
        # Tracks más reportados
        most_reported = Track.objects.annotate(
            report_count=Count('reports')
        ).filter(report_count__gt=0).order_by('-report_count')[:5]
        
        most_reported_data = [{
            'track_id': track.id,
            'track_title': track.title,
            'user': track.user.username,
            'report_count': track.report_count
        } for track in most_reported]
        
        return Response({
            'total_reports': total_reports,
            'unresolved_reports': unresolved_reports,
            'resolved_reports': resolved_reports,
            'most_reported_tracks': most_reported_data
        })


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de comentarios.
    - Todos pueden ver comentarios
    - Solo usuarios autenticados pueden crear
    - Solo propietario o admin pueden editar/eliminar
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrAdmin]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filtrar comentarios por track si se especifica"""
        queryset = Comment.objects.all()
        track_id = self.request.query_params.get('track', None)
        if track_id:
            queryset = queryset.filter(track_id=track_id)
        return queryset
    
    def perform_create(self, serializer):
        """Asignar el usuario actual al comentario"""
        serializer.save(user=self.request.user)


class LikeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para likes.
    Usado principalmente para estadísticas.
    """
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticatedForWrite]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filtrar likes por usuario o track"""
        queryset = Like.objects.all()
        user_id = self.request.query_params.get('user', None)
        track_id = self.request.query_params.get('track', None)
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if track_id:
            queryset = queryset.filter(track_id=track_id)
            
        return queryset


class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de reportes.
    - Usuarios pueden crear reportes
    - Solo admins pueden ver todos y resolver
    """
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    
    def get_permissions(self):
        """
        Asignar permisos según la acción:
        - Crear: usuarios autenticados
        - Listar/Resolver: solo admins
        """
        if self.action == 'create':
            permission_classes = [IsAuthenticatedForWrite]
        else:
            permission_classes = [IsAdminOnly]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filtrar reportes no resueltos por defecto"""
        queryset = Report.objects.all()
        if self.request.user.is_authenticated and self.request.user.role == 'admin':
            resolved = self.request.query_params.get('resolved', None)
            if resolved is not None:
                queryset = queryset.filter(is_resolved=resolved.lower() == 'true')
        return queryset
    
    def perform_create(self, serializer):
        """Asignar el usuario actual al reporte"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminOnly])
    def resolve(self, request, pk=None):
        """Resolver un reporte (solo admin)"""
        report = self.get_object()
        report.is_resolved = True
        report.save()
        
        # Opcionalmente, desactivar el track reportado
        if request.data.get('deactivate_track', False):
            report.track.is_active = False
            report.track.save()
        
        serializer = ReportSerializer(report)
        return Response(serializer.data)