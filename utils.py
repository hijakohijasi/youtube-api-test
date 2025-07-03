import aiofiles
import asyncio
import os
import httpx
import uuid
import subprocess

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

async def download_file(url, ext):
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(TEMP_DIR, filename)

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        async with aiofiles.open(filepath, 'wb') as f:
            await f.write(response.content)
    
    return filepath

def merge_audio_video(video_path, audio_path):
    output_path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}_merged.mp4")
    cmd = [
        "ffmpeg", "-i", video_path, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-strict", "experimental", output_path, "-y"
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_path
