Music Review (Proyecto CRUD con roles)
Descripción

Music Review es una plataforma web de prueba donde los usuarios pueden subir, ver y comentar música, con un sistema de roles y CRUD completo.
El objetivo principal es demostrar la integración de backend y frontend con autenticación, permisos y consumo de API.

Tecnologías
Backend

Django + Django REST Framework (DRF)

Manejo de CRUD, roles, auth y JWT.

PostgreSQL

Base de datos para usuarios, música, comentarios, likes y reportes.

Roles y permisos
Rol	Permisos principales
Visitante	Ver música en homepage
Usuario	Subir música, dar like, comentar, reportar contenido
Admin	Eliminar cualquier música, comentarios o reports

Funcionalidades principales

Autenticación

Registro e inicio de sesión con JWT.

Roles aplicados automáticamente.

Música

Subir, listar, editar y eliminar tracks (según rol).

Mostrar feed de música en homepage.

Interacción social

Likes y comentarios por usuario.

Reportes de contenido inapropiado.