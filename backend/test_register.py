import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'musicrev.settings')
django.setup()

from django.contrib.auth import get_user_model
from tracks.serializers import UserRegistrationSerializer

# Probar el serializador directamente
data = {
    'username': 'testuser',
    'password': 'testpass123',
    'email': 'test@example.com'
}

serializer = UserRegistrationSerializer(data=data)
if serializer.is_valid():
    user = serializer.save()
    print(f"Usuario creado: {user.username} (ID: {user.id})")
else:
    print(f"Errores: {serializer.errors}")