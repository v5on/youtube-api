import os
import logging
import yt_dlp
import tempfile
import re
from urllib.parse import urlparse, parse_qs


class YouTubeService:

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        logging.info(
            f"YouTube service initialized with temp dir: {self.temp_dir}")

    def is_valid_youtube_url(self, url):
        """Check if URL is a valid YouTube URL"""
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
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
                        'filesize': fmt.get('filesize', 0),
                        'format_note': fmt.get('format_note', ''),
                        'url': fmt.get('url', ''),
                        'height': fmt.get('height', 0),
                        'width': fmt.get('width', 0),
                        'fps': fmt.get('fps', 0),
                        'abr': fmt.get('abr', 0),
                        'tbr': fmt.get('tbr', 0)
                    }

                    # Categorize formats
                    vcodec = fmt.get('vcodec', 'none')
                    acodec = fmt.get('acodec', 'none')
                    ext = fmt.get('ext', '')
                    height = fmt.get('height', 0)

                    # Video formats (with or without audio)
                    if vcodec != 'none' and height > 0:
                        # Clean format note for video
                        if height <= 144:
                            format_info['quality_label'] = '144p'
                        elif height <= 240:
                            format_info['quality_label'] = '240p'
                        elif height <= 360:
                            format_info['quality_label'] = '360p'
                        elif height <= 480:
                            format_info['quality_label'] = '480p'
                        elif height <= 720:
                            format_info['quality_label'] = '720p'
                        elif height <= 1080:
                            format_info['quality_label'] = '1080p'
                        elif height <= 1440:
                            format_info['quality_label'] = '1440p'
                        else:
                            format_info['quality_label'] = '2160p'

                        format_info[
                            'type'] = 'video_with_audio' if acodec != 'none' else 'video_only'
                        video_formats.append(format_info)

                    # Audio formats
                    elif vcodec == 'none' and acodec != 'none':
                        abr = fmt.get('abr', 0)
                        # Clean format note for audio
                        if abr <= 128:
                            format_info['quality_label'] = '128kbps'
                        elif abr <= 192:
                            format_info['quality_label'] = '192kbps'
                        elif abr <= 256:
                            format_info['quality_label'] = '256kbps'
                        else:
                            format_info['quality_label'] = '320kbps'

                        format_info['type'] = 'audio_only'
                        audio_formats.append(format_info)

                # Sort video formats by height (quality)
                video_formats.sort(key=lambda x: x.get('height', 0))

                # Sort audio formats by bitrate
                audio_formats.sort(key=lambda x: x.get('abr', 0))

                # Group formats
                video_info['formats'] = {
                    'video': video_formats,
                    'audio': audio_formats
                }

                return video_info

        except Exception as e:
            logging.error(f"Error extracting video info: {e}")
            raise Exception(f"Failed to extract video information: {str(e)}")

    def download_video(self,
                       url,
                       format_id=None,
                       audio_only=False,
                       quality='720p'):
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
            return {'success': False, 'error': str(e)}

    def get_video_info(self, url):
        """Extract simplified video information with one best format per quality"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                video_info = {
                    'title': info.get('title', 'Unknown'),
                    'channel': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'webpage_url': info.get('webpage_url', url),
                    'video_id': info.get('id', ''),
                    'formats': {
                        'video': {},
                        'audio': None
                    }
                }

                formats = info.get('formats', [])
                quality_map = {
                }  # quality_label => format with highest bitrate

                best_audio = None

                for fmt in formats:
                    vcodec = fmt.get('vcodec', 'none')
                    acodec = fmt.get('acodec', 'none')
                    height = fmt.get('height')
                    abr = fmt.get('abr')

                    # Skip formats without URL or essential info
                    if not fmt.get('url') or (vcodec == 'none'
                                              and acodec == 'none'):
                        continue

                    # AUDIO
                    if vcodec == 'none' and acodec != 'none':
                        if not best_audio or fmt.get(
                                'abr', 0) > best_audio.get('abr', 0):
                            best_audio = {
                                'url': fmt['url'],
                                'format_id': fmt['format_id'],
                                'quality_label':
                                f"{abr}kbps" if abr else 'Audio',
                                'ext': fmt['ext'],
                                'filesize': fmt.get('filesize', None)
                            }

                    # VIDEO
                    elif height:
                        if height <= 144:
                            label = '144p'
                        elif height <= 240:
                            label = '240p'
                        elif height <= 360:
                            label = '360p'
                        elif height <= 480:
                            label = '480p'
                        elif height <= 720:
                            label = '720p'
                        elif height <= 1080:
                            label = '1080p'
                        elif height <= 1440:
                            label = '1440p'
                        else:
                            label = '2160p'

                        prev = quality_map.get(label)
                        # Replace only if this format has better bitrate
                        if not prev or fmt.get('tbr', 0) > prev.get('tbr', 0):
                            quality_map[label] = {
                                'url': fmt['url'],
                                'format_id': fmt['format_id'],
                                'quality_label': label,
                                'ext': fmt['ext'],
                                'filesize': fmt.get('filesize', None)
                            }

                # Sort video formats by quality (label like 360p, 480p etc.)
                sorted_qualities = sorted(
                    quality_map.items(),
                    key=lambda x: int(x[0].replace('p', '')))

                video_info['formats']['video'] = [
                    v for _, v in sorted_qualities
                ]
                video_info['formats']['audio'] = best_audio

                return video_info

        except Exception as e:
            logging.error(f"Error extracting video info: {e}")
            raise Exception(f"Failed to extract video information: {str(e)}")
