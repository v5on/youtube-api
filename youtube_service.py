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
                
                # Get available MP4 video qualities (144p to 1080p+)
                video_qualities = []
                audio_qualities = []
                
                formats = info.get('formats', [])
                
                # Find available qualities
                for fmt in formats:
                    if not fmt:
                        continue
                    
                    # MP4 video formats only (144p and above)
                    if fmt.get('ext') == 'mp4' and fmt.get('vcodec') != 'none':
                        height = fmt.get('height')
                        if height and height >= 144:
                            quality = f"{height}p"
                            if quality not in video_qualities:
                                video_qualities.append(quality)
                    
                    # Audio formats for MP3 conversion (128-320kbps range)
                    elif fmt.get('vcodec') == 'none' and fmt.get('acodec') != 'none':
                        abr = fmt.get('abr')
                        if abr and 128 <= abr <= 320:
                            quality = f"{int(abr)}kbps"
                            if quality not in audio_qualities:
                                audio_qualities.append(quality)
                
                # Add standard qualities that yt-dlp can handle
                standard_video = ['144p', '240p', '360p', '480p', '720p', '1080p']
                for q in standard_video:
                    if q not in video_qualities:
                        video_qualities.append(q)
                
                standard_audio = ['128kbps', '192kbps', '256kbps', '320kbps']
                for q in standard_audio:
                    if q not in audio_qualities:
                        audio_qualities.append(q)
                
                # Sort qualities
                video_qualities.sort(key=lambda x: int(x.replace('p', '')))
                audio_qualities.sort(key=lambda x: int(x.replace('kbps', '')))
                
                # Minimal response - only what's needed
                return {
                    'title': info.get('title', 'Unknown'),
                    'video_qualities': video_qualities,
                    'audio_qualities': audio_qualities
                }
                
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
            
            # Also try to extract from format_note
            if height == 0:
                format_note = fmt.get('format_note', '').lower()
                if '144p' in format_note:
                    height = 144
                elif '240p' in format_note:
                    height = 240
                elif '360p' in format_note:
                    height = 360
                elif '480p' in format_note:
                    height = 480
                elif '720p' in format_note:
                    height = 720
                elif '1080p' in format_note:
                    height = 1080
                elif '1440p' in format_note:
                    height = 1440
                elif '2160p' in format_note or '4k' in format_note:
                    height = 2160
            
            # Skip if we still can't determine height
            if height == 0:
                logging.debug(f"Skipping format {fmt.get('format_id')} - no height info")
                continue
                
            # Group by quality ranges
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
        
        # Remove empty quality groups and log what we found
        result = {k: v for k, v in quality_map.items() if v}
        logging.debug(f"Video quality groups found: {list(result.keys())}")
        return result
    
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
                # Use yt-dlp's smart format selection to automatically combine best video+audio
                height = int(quality.replace('p', ''))
                # This format string tells yt-dlp to pick the best video <= height with best audio
                ydl_opts['format'] = f'best[height<={height}]/bestvideo[height<={height}]+bestaudio/best[height<={height}]'
            
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
                
                # Determine actual quality from the downloaded file
                actual_quality = quality
                if audio_only:
                    actual_quality = quality.replace('kbps', '') + 'kbps' if 'kbps' in quality else '192kbps'
                else:
                    actual_quality = quality.replace('p', '') + 'p' if 'p' in quality else '144p'
                
                return {
                    'success': True,
                    'download_url': base_filename,  # This is the local file path
                    'quality': actual_quality,
                    'format': 'mp3' if audio_only else 'mp4'
                }
                
        except Exception as e:
            logging.error(f"Error downloading video: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_download_url(self, url, format_id=None, audio_only=False, quality='720p'):
        """Get direct download URL for video or audio by actually downloading the file"""
        try:
            # Download the file first to get a direct downloadable URL
            download_result = self.download_video(url, format_id, audio_only, quality)
            
            if not download_result.get('success'):
                raise Exception(download_result.get('error', 'Download failed'))
            
            # Return the file path as download URL and the quality
            return {
                'download_url': download_result['download_url'],
                'quality': download_result['quality']
            }
                
        except Exception as e:
            logging.error(f"Error getting download URL: {e}")
            raise Exception(f"Failed to get download URL: {str(e)}")
