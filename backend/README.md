# MusicRev - Django REST API

A comprehensive music management system built with Django REST Framework, featuring JWT authentication and PostgreSQL database integration.

## Project Overview

MusicRev is a Django-based REST API that provides a complete music library management system. It allows users to manage artists, albums, tracks, and playlists with full CRUD operations. The project uses Django REST Framework for API development, JWT for authentication, and PostgreSQL for data persistence.

## Features

- **Django REST Framework API** - Full RESTful API with ViewSets and serializers
- **JWT Authentication** - Secure token-based authentication with access and refresh tokens
- **PostgreSQL Database** - Robust relational database for data persistence
- **Tracks App** - Complete music management with the following models:
  - **Artist** - Music artists with bio information
  - **Album** - Music albums with release dates and cover images
  - **Track** - Individual songs with duration, lyrics, and audio files
  - **Playlist** - Custom playlists with track ordering
  - **PlaylistTrack** - Junction model for playlist-track relationships
- **Admin Interface** - Django admin for easy data management
- **Search, Filtering, and Ordering** - Advanced query capabilities for all endpoints
- **Spanish Localization** - Interface configured for Spanish language

## Requirements

### Installed Packages
- Django 5.2.6
- djangorestframework 3.16.1
- djangorestframework-simplejwt 5.5.1
- psycopg2-binary 2.9.10

### Required Package (needs installation)
- django-filter - For advanced filtering capabilities

### System Requirements
- Python 3.11+
- PostgreSQL 12+
- Virtual environment (recommended)

## Installation & Setup

### 1. Virtual Environment Activation

```bash
# Navigate to project directory
cd C:\Users\julia\OneDrive\Documentos\MusicRev\backend

# Activate virtual environment (Windows)
venv\Scripts\activate

# For Linux/Mac
source venv/bin/activate
```

### 2. Install Required Packages

```bash
# Install django-filter (required for filtering)
pip install django-filter

# If you need to reinstall all packages
pip install django djangorestframework djangorestframework-simplejwt psycopg2-binary django-filter
```

### 3. Database Setup (PostgreSQL)

```sql
-- Connect to PostgreSQL as superuser
psql -U postgres

-- Create database
CREATE DATABASE musicrev_db;

-- Create user (if needed)
CREATE USER postgres WITH PASSWORD 'password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE musicrev_db TO postgres;

-- Exit
\q
```

### 4. Migration Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
# Follow prompts to create admin user
```

### 6. Run Development Server

```bash
python manage.py runserver
# Server will start at http://127.0.0.1:8000/
```

## API Endpoints

### Authentication Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/token/` | POST | Obtain JWT access and refresh tokens |
| `/api/auth/token/refresh/` | POST | Refresh JWT access token |

### Tracks App Endpoints

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/api/artists/` | GET, POST | List and create artists |
| `/api/artists/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update, delete specific artist |
| `/api/albums/` | GET, POST | List and create albums |
| `/api/albums/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update, delete specific album |
| `/api/tracks/` | GET, POST | List and create tracks |
| `/api/tracks/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update, delete specific track |
| `/api/playlists/` | GET, POST | List and create playlists |
| `/api/playlists/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update, delete specific playlist |
| `/api/playlist-tracks/` | GET, POST | List and add tracks to playlists |
| `/api/playlist-tracks/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update, delete playlist track entry |

### Query Parameters

All endpoints support the following query parameters:
- `search` - Search across specified fields
- `ordering` - Order results by specified fields
- `page` - Paginate results (page number)
- `page_size` - Number of results per page

## Authentication

### Obtaining Tokens

```bash
# Obtain access and refresh tokens
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'

# Response
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Using Tokens in Requests

```bash
# Include the access token in the Authorization header
curl -X GET http://127.0.0.1:8000/api/artists/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Token Refresh

```bash
# Refresh access token using refresh token
curl -X POST http://127.0.0.1:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

**Token Configuration:**
- Access token lifetime: 60 minutes
- Refresh token lifetime: 1 day
- Algorithm: HS256

## Models Overview

### Artist
Represents music artists with bio information.
- **Fields**: `name`, `bio`, `created_at`, `updated_at`
- **Relationships**: One-to-many with Album and Track

### Album
Represents music albums with release information.
- **Fields**: `title`, `artist`, `release_date`, `cover_image`, `created_at`, `updated_at`
- **Relationships**: Many-to-one with Artist, one-to-many with Track

### Track
Represents individual songs with metadata.
- **Fields**: `title`, `album`, `artist`, `duration`, `audio_file`, `lyrics`, `created_at`, `updated_at`
- **Relationships**: Many-to-one with Artist and Album, many-to-many with Playlist through PlaylistTrack

### Playlist
Represents custom playlists with track ordering.
- **Fields**: `name`, `description`, `tracks`, `created_at`, `updated_at`
- **Relationships**: Many-to-many with Track through PlaylistTrack

### PlaylistTrack
Junction model for playlist-track relationships with ordering.
- **Fields**: `playlist`, `track`, `order`, `added_at`
- **Relationships**: Many-to-one with Playlist and Track

## Usage Examples

### Create an Artist

```bash
curl -X POST http://127.0.0.1:8000/api/artists/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "The Beatles",
    "bio": "Legendary British rock band"
  }'
```

### Create an Album

```bash
curl -X POST http://127.0.0.1:8000/api/albums/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Abbey Road",
    "artist": 1,
    "release_date": "1969-09-26",
    "cover_image": "https://example.com/abbey-road.jpg"
  }'
```

### Create a Track

```bash
curl -X POST http://127.0.0.1:8000/api/tracks/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Come Together",
    "artist": 1,
    "album": 1,
    "duration": "PT4M20S",
    "lyrics": "Here come old flat top..."
  }'
```

### Create a Playlist

```bash
curl -X POST http://127.0.0.1:8000/api/playlists/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Classic Rock Favorites",
    "description": "Best classic rock songs"
  }'
```

### Add Track to Playlist

```bash
curl -X POST http://127.0.0.1:8000/api/playlist-tracks/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "playlist": 1,
    "track": 1,
    "order": 1
  }'
```

### Search Artists

```bash
# Search for artists containing "Beatles"
curl -X GET "http://127.0.0.1:8000/api/artists/?search=Beatles" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter and Order Albums

```bash
# Get albums by specific artist, ordered by release date
curl -X GET "http://127.0.0.1:8000/api/albums/?artist=1&ordering=-release_date" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Admin Interface

Access the Django admin interface at: `http://127.0.0.1:8000/admin/`

Use your superuser credentials to log in and manage:
- Users and groups
- All music models (Artists, Albums, Tracks, Playlists)
- Authentication tokens

### Admin Features
- Full CRUD operations for all models
- Search and filtering capabilities
- Bulk actions
- User management

## Configuration Notes

### Important Settings

1. **Security**: The `SECRET_KEY` in settings.py should be changed for production use
2. **Debug Mode**: Currently set to `DEBUG = True` - should be `False` in production
3. **Allowed Hosts**: Currently empty - configure for production deployment
4. **Database**: Configured for PostgreSQL with local connection

### Localization
- Language: Spanish (es-es)
- Time Zone: UTC

### JWT Configuration
- Access token lifetime: 60 minutes
- Refresh token lifetime: 1 day
- Algorithm: HS256
- Token type: Bearer

### Current Limitations
- `django-filter` package needs to be installed for advanced filtering
- Some filter backends are temporarily commented out in views.py
- No pagination configuration explicitly set (uses DRF defaults)

### Environment Variables (Recommended for Production)

Consider using environment variables for sensitive settings:
```python
import os
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the documentation
2. Review the code comments
3. Create an issue in the repository

---

**Note**: This is a development environment setup. For production deployment, ensure proper security configurations, environment variables, and deployment procedures are followed.