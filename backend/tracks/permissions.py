from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso personalizado que permite:
    - Usuarios autenticados: leer todo, editar/eliminar solo su contenido
    - Admins: leer/escribir/eliminar todo
    - Visitantes: solo leer
    """
    
    def has_permission(self, request, view):
        # Permitir lectura a todos (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Requerir autenticación para escritura
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Lectura: todos pueden ver
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Escritura/Eliminación: solo propietario o admin
        return (
            request.user == obj.user or 
            (request.user and request.user.role == 'admin')
        )


class IsAuthenticatedForWrite(permissions.BasePermission):
    """
    Permiso que permite:
    - Lectura a todos (incluye visitantes no autenticados)
    - Escritura solo a usuarios autenticados
    """
    
    def has_permission(self, request, view):
        # Lectura: todos pueden ver
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Escritura: requiere autenticación
        return request.user and request.user.is_authenticated


class IsAdminOnly(permissions.BasePermission):
    """
    Permiso que solo permite acceso a administradores
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'
    
    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'