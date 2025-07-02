import os
import logging
import yt_dlp
import tempfile
import re
from urllib.parse import urlparse, parse_qs

class YouTubeService:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        logging.info(f"YouTube service initialized with temp dir: {self.temp_dir}")
    
    def is_valid_youtube_url(self, url):
        """Check if URL is a valid YouTube URL"""
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        return youtube_regex.match(url) is not None
    
    def get_video_info(self, url):
        """Extract comprehensive video information"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Extract basic video information
                video_info = {
                    'title': info.get('title', 'Unknown'),
                    'channel': info.get('uploader', 'Unknown'),
                    'channel_id': info.get('uploader_id', ''),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'upload_date': info.get('upload_date', ''),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'webpage_url': info.get('webpage_url', url),
                    'video_id': info.get('id', ''),
                    'formats': {
                        'audio': [],
                        'video': []
                    }
                }
                
                # Process available formats
                formats = info.get('formats', [])
                
                # Target qualities we want
                target_video_heights = [360, 480, 720, 1080]
                
                for fmt in formats:
                    vcodec = fmt.get('vcodec', 'none')
                    acodec = fmt.get('acodec', 'none')
                    ext = fmt.get('ext', '')
                    height = fmt.get('height', 0)
                    abr = fmt.get('abr', 0)
                    format_id = fmt.get('format_id', '')
                    
                    # Audio format - 128kbps (look for common audio format IDs)
                    if vcodec == 'none' and acodec != 'none':
                        # Common 128kbps format IDs: 250 (webm), 140 (m4a)
                        if format_id in ['250', '140'] or (120 <= abr <= 135):
                            audio_format = {
                                'ext': 'mp3',
                                'filesize': fmt.get('filesize', 0),
                                'format_id': format_id,
                                'format_note': '128kbps',
                                'type': 'audio_only',
                                'url': fmt.get('url', '')
                            }
                            # Only add one audio format
                            if not video_info['formats']['audio']:
                                video_info['formats']['audio'].append(audio_format)
                    
                    # Video formats - only specific qualities (video only, no audio)
                    elif vcodec != 'none' and acodec == 'none':
                        if height in target_video_heights and ext == 'mp4':
                            video_format = {
                                'ext': 'mp4',
                                'filesize': fmt.get('filesize', 0),
                                'format_id': format_id,
                                'format_note': f'{height}p',
                                'type': 'video_only',
                                'url': fmt.get('url', '')
                            }
                            video_info['formats']['video'].append(video_format)
                
                # Remove duplicates and sort video formats by quality
                seen_heights = set()
                unique_video_formats = []
                for fmt in video_info['formats']['video']:
                    height = fmt['format_note']
                    if height not in seen_heights:
                        seen_heights.add(height)
                        unique_video_formats.append(fmt)
                
                video_info['formats']['video'] = sorted(unique_video_formats, 
                    key=lambda x: int(x['format_note'].replace('p', '')))
                
                return video_info
                
        except Exception as e:
            logging.error(f"Error extracting video info: {e}")
            raise Exception(f"Failed to extract video information: {str(e)}")
    
    
    
    def download_video(self, url, format_id=None, audio_only=False, quality='720p'):
        """Download video or audio file"""
        try:
            output_path = os.path.join(self.temp_dir, '%(title)s.%(ext)s')
            
            ydl_opts = {
                'outtmpl': output_path,
                'quiet': True,
                'no_warnings': True,
            }
            
            if audio_only:
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            elif format_id:
                ydl_opts['format'] = format_id
            else:
                # Select best format for specified quality
                height = int(quality.replace('p', ''))
                ydl_opts['format'] = f'best[height<={height}]'
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Find the downloaded file
                base_filename = ydl.prepare_filename(info)
                
                # Check for post-processed audio file
                if audio_only:
                    audio_file = base_filename.rsplit('.', 1)[0] + '.mp3'
                    if os.path.exists(audio_file):
                        base_filename = audio_file
                
                if not os.path.exists(base_filename):
                    raise Exception("Downloaded file not found")
                
                return {
                    'success': True,
                    'file_path': base_filename,
                    'filename': os.path.basename(base_filename),
                    'mimetype': 'audio/mpeg' if audio_only else 'video/mp4'
                }
                
        except Exception as e:
            logging.error(f"Error downloading video: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_download_url(self, url, format_id=None, audio_only=False, quality='720p'):
        """Get direct download URL for video or audio"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            if audio_only:
                ydl_opts['format'] = 'bestaudio/best'
            elif format_id:
                ydl_opts['format'] = format_id
            else:
                # Select best format for specified quality
                height = int(quality.replace('p', ''))
                ydl_opts['format'] = f'best[height<={height}]'
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Get the best format based on criteria
                formats = info.get('formats', [])
                if not formats:
                    raise Exception("No formats available")
                
                # Select the best format
                selected_format = formats[0]
                for fmt in formats:
                    if audio_only and fmt.get('acodec') != 'none':
                        selected_format = fmt
                        break
                    elif not audio_only and fmt.get('vcodec') != 'none':
                        selected_format = fmt
                        break
                
                # Generate filename
                title = info.get('title', 'video')
                title = re.sub(r'[^\w\s-]', '', title).strip()
                title = re.sub(r'[-\s]+', '-', title)
                
                ext = selected_format.get('ext', 'mp4')
                if audio_only:
                    ext = 'mp3'
                
                filename = f"{title}.{ext}"
                
                return {
                    'url': selected_format.get('url'),
                    'filename': filename,
                    'filesize': selected_format.get('filesize'),
                    'format_id': selected_format.get('format_id'),
                    'quality': selected_format.get('format_note', '')
                }
                
        except Exception as e:
            logging.error(f"Error getting download URL: {e}")
            raise Exception(f"Failed to get download URL: {str(e)}")
