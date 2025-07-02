# YouTube Downloader API

A powerful REST API for downloading YouTube videos with multiple format options and comprehensive metadata extraction. Built with Flask and yt-dlp.

## Features

- 🎥 **Multiple Video Formats**: Support for MP4 from 144p to 1080p
- 🎵 **Audio Only Downloads**: MP3 with various bitrates (128kbps - 320kbps)
- 📊 **Rich Metadata**: Extract video information including title, views, duration, thumbnails
- 🔗 **Direct Download Links**: Get temporary download URLs that expire in 6 hours
- 📱 **Video Preview Pages**: Watch videos before downloading with embedded player
- 🌐 **REST API**: All endpoints use GET requests for easy integration

## API Endpoints

### 1. Get Video Information
```
GET /api/video-info?url=YOUTUBE_URL
```
Returns comprehensive video metadata and available formats.

### 2. Direct Download
```
GET /api/download?url=YOUTUBE_URL&quality=720p&audio_only=false
```
Downloads the video/audio file directly.

### 3. Get Download Link
```
GET /api/download-link?url=YOUTUBE_URL&quality=720p&audio_only=false
```
Returns a temporary download URL.

### 4. Create Preview Link
```
GET /api/create-preview-link?url=YOUTUBE_URL
```
Creates a preview page with embedded video player and download options.

## Deployment

### Deploy on Railway.com

1. Fork this repository
2. Connect your GitHub account to Railway
3. Create a new project and select your forked repository
4. Railway will automatically detect the configuration from `railway.json`
5. Deploy and your API will be live!

**Environment Variables:**
- `SESSION_SECRET`: Set a random secret key for session management

### Deploy on Vercel.com

1. Fork this repository
2. Connect your GitHub account to Vercel
3. Import your forked repository
4. Vercel will automatically use the configuration from `vercel.json`
5. Deploy and your API will be live!

**Note:** Vercel has limitations for serverless functions. Large file downloads might timeout.

### Local Development

1. Clone the repository:
```bash
git clone <your-repo-url>
cd youtube-downloader-api
```

2. Install dependencies:
```bash
pip install flask yt-dlp gunicorn werkzeug
```

3. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:5000`

## Usage Examples

### Get Video Information
```bash
curl "https://your-domain.com/api/video-info?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Download Video (720p)
```bash
curl -L "https://your-domain.com/api/download?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ&quality=720p" -o video.mp4
```

### Download Audio Only
```bash
curl -L "https://your-domain.com/api/download?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ&audio_only=true" -o audio.mp3
```

### Get Download Link
```bash
curl "https://your-domain.com/api/download-link?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ&quality=1080p"
```

### Create Preview Link
```bash
curl "https://your-domain.com/api/create-preview-link?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## Parameters

| Parameter | Type | Description | Default | Required |
|-----------|------|-------------|---------|----------|
| `url` | string | YouTube video URL | - | Yes |
| `quality` | string | Video quality: 144p, 240p, 360p, 480p, 720p, 1080p | 720p | No |
| `audio_only` | boolean | Download audio only | false | No |
| `format_id` | string | Specific format ID from video info | - | No |

## Response Format

All API responses follow this structure:

```json
{
  "success": true,
  "data": { ... },
  "error": "Error message if success is false"
}
```

## Preview Pages

Visit `/video/{VIDEO_ID}` to access a preview page where users can:
- Watch the YouTube video with embedded player
- See video metadata (title, channel, views, likes, duration)
- Choose from multiple download options
- Get direct download links

Example: `https://your-domain.com/video/dQw4w9WgXcQ`

## Rate Limiting & Considerations

- **No built-in rate limiting**: Implement your own if needed
- **File cleanup**: Temporary files are automatically cleaned up after 5 minutes
- **Download links**: Expire after 6 hours for security
- **Large files**: May timeout on serverless platforms like Vercel

## Technical Stack

- **Backend**: Python Flask
- **Video Processing**: yt-dlp
- **Frontend**: Bootstrap 5 (dark theme), Vanilla JavaScript
- **Web Server**: Gunicorn (production)

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Support

For issues and questions, please create an issue in the GitHub repository.