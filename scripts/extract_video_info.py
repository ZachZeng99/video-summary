#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Smart Video Extractor with Auto-Auth
Automatically detects auth requirement and guides user through setup
"""

import json
import re
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class VideoInfo:
    """Video information data structure"""
    platform: str
    title: str
    author: str
    duration: int
    duration_formatted: str
    subtitles: List[Dict]
    segments: List[Dict]
    error: Optional[str] = None


def get_config_dir() -> Path:
    """Get the config directory path, works in any environment"""
    # Try multiple methods to find the correct path
    script_dir = Path(__file__).parent.absolute()
    config_dir = script_dir.parent / "config"
    
    # If config directory doesn't exist, create it
    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
    
    return config_dir


def check_bilibili_auth() -> bool:
    """Check if Bilibili authentication is configured"""
    try:
        config_dir = get_config_dir()
        config_file = config_dir / "auth.json"
        
        if not config_file.exists():
            # Create empty config file
            config = {"sessdata": "", "platform": "bilibili"}
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return False
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return bool(config.get('sessdata') and config.get('sessdata').strip())
    except Exception as e:
        print(f"Warning: Error checking auth config: {e}", file=sys.stderr)
        return False


def save_bilibili_auth(sessdata: str) -> bool:
    """Save Bilibili authentication to config file"""
    try:
        config_dir = get_config_dir()
        config_file = config_dir / "auth.json"
        
        config = {
            "sessdata": sessdata,
            "platform": "bilibili"
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving auth config: {e}", file=sys.stderr)
        return False


def auto_setup_bilibili_auth():
    """Interactive setup for Bilibili authentication with detailed instructions"""
    print("\n" + "="*70)
    print("🔐 需要 Bilibili 认证")
    print("="*70)
    print()
    print("此视频需要 Bilibili 登录才能获取字幕。")
    print()
    print("📋 获取 SESSDATA 的详细步骤：")
    print()
    print("方法 1 - 使用文档（推荐）：")
    print("   1. 访问: https://nemo2011.github.io/bilibili-api/#/get-credential")
    print("   2. 按照页面上的说明操作")
    print("   3. 复制获取到的 SESSDATA")
    print()
    print("方法 2 - 手动获取：")
    print("   1. 打开 Chrome/Edge 浏览器")
    print("   2. 访问 https://www.bilibili.com 并登录你的账号")
    print("   3. 按 F12 打开开发者工具")
    print("   4. 点击 'Application' (应用) 标签")
    print("   5. 左侧找到 'Storage' → 'Cookies' → 'https://www.bilibili.com'")
    print("   6. 在右侧列表中找到 'SESSDATA' 行")
    print("   7. 双击 Value 列的值，复制完整内容")
    print()
    print("⚠️  安全提示：")
    print("   • SESSDATA 是你的登录凭证，请勿分享给他人")
    print("   • 凭证将保存在本地 config/auth.json 文件中")
    print("   • 可随时删除该文件清除登录状态")
    print()
    print("-"*70)
    
    try:
        sessdata = input("\n请粘贴 SESSDATA (或按回车取消): ").strip()
    except EOFError:
        # Non-interactive environment
        print("\n❌ 无法读取输入，请重试")
        return False
    except KeyboardInterrupt:
        print("\n\n❌ 用户取消")
        return False
    
    if not sessdata:
        print("\n❌ 未输入 SESSDATA，操作取消")
        return False
    
    # Validate input looks like SESSDATA
    if len(sessdata) < 20:
        print("\n⚠️  输入的内容看起来不像是有效的 SESSDATA（太短了）")
        retry = input("是否重新输入? (y/n): ").strip().lower()
        if retry == 'y':
            return auto_setup_bilibili_auth()
        return False
    
    # Save to config
    if save_bilibili_auth(sessdata):
        print(f"\n✅ 认证信息已保存！")
        print(f"   位置: {get_config_dir() / 'auth.json'}")
        return True
    else:
        print("\n❌ 保存认证信息失败")
        return False


def identify_platform(url: str) -> Optional[str]:
    """Identify video platform from URL"""
    youtube_patterns = [
        r'youtube\.com/watch\?v=',
        r'youtu\.be/',
        r'youtube\.com/shorts/'
    ]
    bilibili_patterns = [
        r'bilibili\.com/video/[Bb][Vv]',
        r'b23\.tv/',
        r'bilibili\.com/bangumi/play/'
    ]
    
    url_lower = url.lower()
    
    for pattern in youtube_patterns:
        if re.search(pattern, url_lower):
            return 'youtube'
    
    for pattern in bilibili_patterns:
        if re.search(pattern, url_lower):
            return 'bilibili'
    
    return None


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human-readable string"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def calculate_segments(duration: int) -> List[Tuple[int, int]]:
    """Calculate time segments based on video duration"""
    if duration < 600:  # < 10 minutes
        return [(0, duration)]
    elif duration < 1800:  # 10-30 minutes
        segment_duration = duration // 3
        return [
            (0, segment_duration),
            (segment_duration, segment_duration * 2),
            (segment_duration * 2, duration)
        ]
    else:  # > 30 minutes
        segment_duration = 600  # 10 minutes per segment
        segments = []
        for start in range(0, duration, segment_duration):
            end = min(start + segment_duration, duration)
            segments.append((start, end))
            if len(segments) >= 10:  # Max 10 segments
                break
        return segments


def extract_youtube_info(url: str) -> VideoInfo:
    """Extract information from YouTube video using yt-dlp Python API"""
    try:
        try:
            import yt_dlp
            import requests
        except ImportError as e:
            return VideoInfo(
                platform='youtube',
                title='',
                author='',
                duration=0,
                duration_formatted='',
                subtitles=[],
                segments=[],
                error=f"Missing dependency: {e}. Run: pip install yt-dlp requests"
            )
        
        # Configure yt-dlp
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['zh', 'zh-CN', 'zh-TW', 'en', 'ja', 'ko'],
            'quiet': True,
            'no_warnings': True,
        }
        
        # Extract video info
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                video_data = ydl.extract_info(url, download=False)
            except Exception as e:
                return VideoInfo(
                    platform='youtube',
                    title='',
                    author='',
                    duration=0,
                    duration_formatted='',
                    subtitles=[],
                    segments=[],
                    error=f"Failed to extract video info: {e}"
                )
            
            duration = int(video_data.get('duration', 0))
            title = video_data.get('title', 'Unknown')
            author = video_data.get('uploader', 'Unknown')
            
            # Extract subtitles by downloading them
            subtitles = []
            
            # Try manual subtitles first
            subs_data = video_data.get('subtitles', {})
            automatic_captions = video_data.get('automatic_captions', {})
            
            # Find available subtitle
            subtitle_url = None
            
            for lang in ['zh', 'zh-CN', 'zh-TW', 'en', 'ja', 'ko']:
                if lang in subs_data and subs_data[lang]:
                    for sub in subs_data[lang]:
                        if sub.get('url'):
                            subtitle_url = sub['url']
                            break
                if subtitle_url:
                    break
                
                # Try automatic captions
                if lang in automatic_captions and automatic_captions[lang]:
                    for sub in automatic_captions[lang]:
                        if sub.get('url'):
                            subtitle_url = sub['url']
                            break
                if subtitle_url:
                    break
            
            # Download and parse subtitle
            if subtitle_url:
                try:
                    response = requests.get(subtitle_url, timeout=10)
                    if response.status_code == 200:
                        content = response.text
                        
                        # Try to parse as JSON
                        try:
                            json_data = json.loads(content)
                            if 'events' in json_data:
                                for event in json_data['events']:
                                    if 'segs' in event:
                                        start = event.get('tStartMs', 0) / 1000.0
                                        end = start + (event.get('dDurationMs', 0) / 1000.0)
                                        text = ''.join(seg.get('utf8', '') for seg in event['segs'])
                                        if text.strip():
                                            subtitles.append({
                                                'start': start,
                                                'end': end,
                                                'text': text.strip()
                                            })
                            elif 'body' in json_data:
                                for entry in json_data['body']:
                                    subtitles.append({
                                        'start': float(entry.get('from', 0)),
                                        'end': float(entry.get('to', 0)),
                                        'text': entry.get('content', '').strip()
                                    })
                        except json.JSONDecodeError:
                            pass
                        
                except Exception as e:
                    print(f"Warning: Failed to download subtitle: {e}", file=sys.stderr)
        
        # Calculate segments
        segments_data = calculate_segments(duration)
        segments = []
        
        for start, end in segments_data:
            segment_subs = [
                sub for sub in subtitles
                if start <= sub['start'] < end
            ]
            
            segment_text = ' '.join([sub['text'] for sub in segment_subs])
            
            segments.append({
                'start': start,
                'end': end,
                'start_formatted': format_duration(start),
                'end_formatted': format_duration(end),
                'text': segment_text,
                'subtitles_count': len(segment_subs)
            })
        
        return VideoInfo(
            platform='youtube',
            title=title,
            author=author,
            duration=duration,
            duration_formatted=format_duration(duration),
            subtitles=subtitles,
            segments=segments
        )
        
    except Exception as e:
        import traceback
        return VideoInfo(
            platform='youtube',
            title='',
            author='',
            duration=0,
            duration_formatted='',
            subtitles=[],
            segments=[],
            error=f"Extraction error: {str(e)}\n{traceback.format_exc()}"
        )


def extract_bilibili_info(url: str) -> VideoInfo:
    """Extract information from Bilibili video with auto-auth"""
    # Check if authenticated
    if not check_bilibili_auth():
        print("\n⚠️  首次使用 Bilibili 功能，需要配置认证")
        if not auto_setup_bilibili_auth():
            return VideoInfo(
                platform='bilibili',
                title='',
                author='',
                duration=0,
                duration_formatted='',
                subtitles=[],
                segments=[],
                error="Bilibili 认证配置失败或取消"
            )
        print("\n✅ 认证完成，继续提取视频...")
    
    # Now extract with authentication
    try:
        from bilibili_api import video, Credential
        from bilibili_api.exceptions import CredentialNoSessdataException
        import asyncio
        import requests
    except ImportError as e:
        return VideoInfo(
            platform='bilibili',
            title='',
            author='',
            duration=0,
            duration_formatted='',
            subtitles=[],
            segments=[],
            error=f"Missing dependency: {e}. Run: pip install bilibili-api-python requests"
        )
    
    # Load credential
    try:
        config_dir = get_config_dir()
        config_file = config_dir / "auth.json"
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        sessdata = config.get('sessdata', '')
        if not sessdata:
            return VideoInfo(
                platform='bilibili',
                title='',
                author='',
                duration=0,
                duration_formatted='',
                subtitles=[],
                segments=[],
                error="认证信息为空，请重新配置"
            )
        
        credential = Credential(sessdata=sessdata)
    except Exception as e:
        return VideoInfo(
            platform='bilibili',
            title='',
            author='',
            duration=0,
            duration_formatted='',
            subtitles=[],
            segments=[],
            error=f"加载认证信息失败: {e}"
        )
    
    # Extract BV number
    bv_match = re.search(r'[Bb][Vv]([a-zA-Z0-9]+)', url)
    if not bv_match:
        return VideoInfo(
            platform='bilibili',
            title='',
            author='',
            duration=0,
            duration_formatted='',
            subtitles=[],
            segments=[],
            error="Could not extract BV number from URL"
        )
    
    bvid = f"BV{bv_match.group(1)}"
    
    # Create video object
    v = video.Video(bvid=bvid, credential=credential)
    
    async def get_video_data():
        """Get all video data including info and subtitles"""
        info = await v.get_info()
        cid = info.get('cid')
        
        subtitles_data = []
        
        if cid:
            try:
                subtitle_list = await v.get_subtitle(cid=cid)
                
                if subtitle_list and isinstance(subtitle_list, dict):
                    if 'subtitles' in subtitle_list and subtitle_list['subtitles']:
                        print(f"\n📝 找到 {len(subtitle_list['subtitles'])} 个字幕，正在下载...")
                        for sub_info in subtitle_list['subtitles']:
                            subtitle_url = sub_info.get('subtitle_url', '')
                            if subtitle_url:
                                # Fix relative URL
                                if subtitle_url.startswith('//'):
                                    subtitle_url = 'https:' + subtitle_url
                                
                                try:
                                    print(f"   下载 {sub_info.get('lan_doc', 'unknown')} 字幕...")
                                    resp = requests.get(subtitle_url, timeout=10)
                                    if resp.status_code == 200:
                                        subtitle_json = resp.json()
                                        body = subtitle_json.get('body', [])
                                        print(f"   ✓ 获取 {len(body)} 条字幕")
                                        for entry in body:
                                            subtitles_data.append({
                                                'start': float(entry.get('from', 0)),
                                                'end': float(entry.get('to', 0)),
                                                'text': entry.get('content', '').strip()
                                            })
                                        break  # Use first available subtitle
                                except Exception as e:
                                    print(f"   ✗ 下载失败: {e}")
                                    continue
                    elif 'body' in subtitle_list:
                        for entry in subtitle_list['body']:
                            subtitles_data.append({
                                'start': float(entry.get('from', 0)),
                                'end': float(entry.get('to', 0)),
                                'text': entry.get('content', '').strip()
                            })
            except Exception:
                pass
        
        return info, subtitles_data
    
    try:
        info, subtitles = asyncio.run(get_video_data())
    except Exception as e:
        return VideoInfo(
            platform='bilibili',
            title='',
            author='',
            duration=0,
            duration_formatted='',
            subtitles=[],
            segments=[],
            error=f"Failed to fetch video data: {e}"
        )
    
    title = info.get('title', 'Unknown')
    author = info.get('owner', {}).get('name', 'Unknown')
    duration = info.get('duration', 0)
    
    # Calculate segments
    segments_data = calculate_segments(duration)
    segments = []
    
    for start, end in segments_data:
        segment_subs = [
            sub for sub in subtitles
            if start <= sub['start'] < end
        ]
        
        segment_text = ' '.join([sub['text'] for sub in segment_subs])
        
        segments.append({
            'start': start,
            'end': end,
            'start_formatted': format_duration(start),
            'end_formatted': format_duration(end),
            'text': segment_text,
            'subtitles_count': len(segment_subs)
        })
    
    return VideoInfo(
        platform='bilibili',
        title=title,
        author=author,
        duration=duration,
        duration_formatted=format_duration(duration),
        subtitles=subtitles,
        segments=segments
    )


def print_help():
    """Print detailed help message"""
    help_text = """
Video Summary Tool - 视频字幕提取工具
=====================================

Usage: python extract_video_info.py <video_url>

支持的平台:
  • YouTube - 无需认证，自动提取字幕
  • Bilibili - 首次使用需要 SESSDATA 认证

示例:
  python extract_video_info.py "https://www.youtube.com/watch?v=xxx"
  python extract_video_info.py "https://www.bilibili.com/video/BVxxx"

Bilibili 认证说明:
  1. 首次使用 Bilibili 功能时，脚本会提示输入 SESSDATA
  2. 获取方法：
     • 访问: https://nemo2011.github.io/bilibili-api/#/get-credential
     • 或手动: F12 → Application → Cookies → bilibili.com → 复制 SESSDATA
  3. 粘贴 SESSDATA 后，认证信息会保存在 config/auth.json
  4. 后续使用无需再次输入

配置文件位置:
  config/auth.json (已添加到 .gitignore，不会被提交)
"""
    print(help_text)


def main():
    """Main entry point"""
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        print_help()
        sys.exit(0)
    
    url = sys.argv[1]
    
    url = sys.argv[1]
    
    # Identify platform
    platform = identify_platform(url)
    
    if not platform:
        result = VideoInfo(
            platform='unknown',
            title='',
            author='',
            duration=0,
            duration_formatted='',
            subtitles=[],
            segments=[],
            error="Unsupported platform. Supported: YouTube, Bilibili"
        )
    elif platform == 'youtube':
        result = extract_youtube_info(url)
    elif platform == 'bilibili':
        result = extract_bilibili_info(url)
    else:
        result = VideoInfo(
            platform='unknown',
            title='',
            author='',
            duration=0,
            duration_formatted='',
            subtitles=[],
            segments=[],
            error="Unknown platform"
        )
    
    # Output as JSON
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
