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
                    'formats': []
                }
                
                # Process available formats
                formats = info.get('formats', [])
                video_formats = []
                audio_formats = []
                
                for fmt in formats:
                    format_info = {
                        'format_id': fmt.get('format_id', ''),
                        'ext': fmt.get('ext', ''),
                        'quality': fmt.get('quality', 0),
                        'resolution': fmt.get('resolution', ''),
                        'height': fmt.get('height', 0),
                        'width': fmt.get('width', 0),
                        'fps': fmt.get('fps', 0),
                        'vcodec': fmt.get('vcodec', ''),
                        'acodec': fmt.get('acodec', ''),
                        'filesize': fmt.get('filesize', 0),
                        'tbr': fmt.get('tbr', 0),
                        'vbr': fmt.get('vbr', 0),
                        'abr': fmt.get('abr', 0),
                        'format_note': fmt.get('format_note', ''),
                        'url': fmt.get('url', ''),
                        'protocol': fmt.get('protocol', ''),
                    }
                    
                    # Categorize formats
                    vcodec = fmt.get('vcodec', 'none')
                    acodec = fmt.get('acodec', 'none')
                    ext = fmt.get('ext', '')
                    
                    # Only include video+audio combined formats (no video-only formats)
                    if vcodec != 'none' and acodec != 'none':
                        # Video with audio combined - this is what we want
                        if ext in ['mp4', 'webm', 'mkv'] and fmt.get('height', 0) > 0:
                            format_info['type'] = 'video_with_audio'
                            video_formats.append(format_info)
                    elif vcodec == 'none' and acodec != 'none':
                        # Audio only formats
                        if ext in ['mp3', 'm4a', 'webm', 'ogg'] and fmt.get('abr', 0) > 0:
                            format_info['type'] = 'audio_only'
                            audio_formats.append(format_info)
                
                # Sort formats by quality
                video_formats.sort(key=lambda x: x.get('quality', 0), reverse=True)
                audio_formats.sort(key=lambda x: x.get('abr', 0), reverse=True)
                
                # Create quality-based format groups
                quality_groups = {
                    'video_formats': self._group_video_formats(video_formats),
                    'audio_formats': self._group_audio_formats(audio_formats)
                }
                
                video_info['formats'] = quality_groups
                video_info['available_qualities'] = self._get_available_qualities(video_formats)
                
                return video_info
                
        except Exception as e:
            logging.error(f"Error extracting video info: {e}")
            raise Exception(f"Failed to extract video information: {str(e)}")
    
    def _group_video_formats(self, formats):
        """Group video formats by quality"""
        quality_map = {
            '144p': [], '240p': [], '360p': [], '480p': [], '720p': [], '1080p': [], '1440p': [], '2160p': []
        }
        
        for fmt in formats:
            height = fmt.get('height', 0)
            # If height is not available, try to parse from resolution string
            if height == 0:
                resolution = fmt.get('resolution', '')
                if 'x' in resolution:
                    try:
                        height = int(resolution.split('x')[1])
                    except:
                        height = 0
            
            if height == 0:
                continue
                
            if height <= 144:
                quality_map['144p'].append(fmt)
            elif height <= 240:
                quality_map['240p'].append(fmt)
            elif height <= 360:
                quality_map['360p'].append(fmt)
            elif height <= 480:
                quality_map['480p'].append(fmt)
            elif height <= 720:
                quality_map['720p'].append(fmt)
            elif height <= 1080:
                quality_map['1080p'].append(fmt)
            elif height <= 1440:
                quality_map['1440p'].append(fmt)
            elif height <= 2160:
                quality_map['2160p'].append(fmt)
        
        # Remove empty quality groups
        return {k: v for k, v in quality_map.items() if v}
    
    def _group_audio_formats(self, formats):
        """Group audio formats by bitrate"""
        bitrate_map = {
            '128kbps': [], '192kbps': [], '256kbps': [], '320kbps': []
        }
        
        for fmt in formats:
            abr = fmt.get('abr', 0)
            if abr <= 128:
                bitrate_map['128kbps'].append(fmt)
            elif abr <= 192:
                bitrate_map['192kbps'].append(fmt)
            elif abr <= 256:
                bitrate_map['256kbps'].append(fmt)
            else:
                bitrate_map['320kbps'].append(fmt)
        
        # Remove empty bitrate groups
        return {k: v for k, v in bitrate_map.items() if v}
    
    def _get_available_qualities(self, formats):
        """Get list of available video qualities"""
        qualities = set()
        for fmt in formats:
            height = fmt.get('height', 0)
            if height <= 144:
                qualities.add('144p')
            elif height <= 240:
                qualities.add('240p')
            elif height <= 360:
                qualities.add('360p')
            elif height <= 480:
                qualities.add('480p')
            elif height <= 720:
                qualities.add('720p')
            elif height <= 1080:
                qualities.add('1080p')
            elif height <= 1440:
                qualities.add('1440p')
            elif height <= 2160:
                qualities.add('2160p')
        
        return sorted(list(qualities), key=lambda x: int(x.replace('p', '')))
    
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
