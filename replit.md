# YouTube Downloader API

## Overview

This is a Flask-based REST API for downloading YouTube videos and extracting video metadata. The application provides a web interface for testing the API and supports multiple video/audio formats with quality options. Built with Python Flask, it uses yt-dlp for YouTube video processing and provides both programmatic API access and a user-friendly web interface.

## System Architecture

### Backend Architecture
- **Framework**: Flask with Python 3.x
- **Video Processing**: yt-dlp library for YouTube video extraction and download
- **Web Server**: Flask development server (suitable for development/testing)
- **Template Engine**: Jinja2 (Flask's default templating engine)
- **Static File Serving**: Flask's built-in static file handler

### Frontend Architecture
- **UI Framework**: Bootstrap 5 (dark theme) with Font Awesome icons
- **JavaScript**: Vanilla ES6+ for interactive functionality
- **Styling**: Custom CSS with Bootstrap theme overrides
- **Layout**: Responsive design with Bootstrap grid system

## Key Components

### Core Application Files
- **app.py**: Main Flask application with route definitions and request handling
- **main.py**: Application entry point for running the Flask server
- **youtube_service.py**: Service layer handling YouTube URL validation and video processing
- **templates/**: HTML templates using Jinja2 templating
- **static/**: Client-side JavaScript and CSS assets

### API Endpoints
- **GET /**: Main page with API documentation and testing interface
- **POST /api/video-info**: Extract video metadata and available formats
- **POST /api/download**: Download video in specified format and quality

### Service Layer
- **YouTubeService**: Encapsulates yt-dlp functionality for video processing
- URL validation using regex patterns
- Temporary file management for downloads
- Format extraction and quality options

## Data Flow

1. **Client Request**: User submits YouTube URL via web interface or API call
2. **URL Validation**: Service validates YouTube URL format
3. **Video Processing**: yt-dlp extracts video information and available formats
4. **Response Generation**: API returns metadata or initiates download
5. **File Management**: Temporary files are created for downloads and cleaned up automatically
6. **Client Response**: JSON data or file download sent to client

## External Dependencies

### Python Packages
- **Flask**: Web framework for API and routing
- **yt-dlp**: YouTube video extraction and download library
- **Werkzeug**: WSGI utilities (ProxyFix middleware)

### Frontend Dependencies (CDN)
- **Bootstrap 5**: CSS framework for responsive UI
- **Font Awesome 6**: Icon library for UI elements

### System Dependencies
- **Python 3.x**: Runtime environment
- **ffmpeg**: Required by yt-dlp for video/audio processing (implicit dependency)

## Deployment Strategy

### Current Setup
- Development server configuration using Flask's built-in server
- Host: 0.0.0.0 (accepts connections from any IP)
- Port: 5000
- Debug mode enabled for development

### File Management
- Temporary directory creation for download files
- Automatic cleanup of temporary files after 5 minutes
- Thread-based cleanup to avoid blocking main application

### Configuration
- Environment-based secret key configuration
- ProxyFix middleware for reverse proxy compatibility
- Configurable logging levels

## User Preferences

Preferred communication style: Simple, everyday language.

## Changelog

Changelog:
- July 02, 2025. Initial setup with YouTube Downloader API
- July 02, 2025. Updated all API endpoints to use GET requests instead of POST
- July 02, 2025. Modified video format filtering to only include video+audio combined formats and audio-only formats (removed video-only formats)
- July 02, 2025. Added video preview page functionality with embedded YouTube player
- July 02, 2025. Updated API documentation to reflect GET method usage with query parameters