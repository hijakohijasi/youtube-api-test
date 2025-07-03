from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
import httpx
import os

from utils import download_file, merge_audio_video

app = FastAPI()
API_URL = "https://youtube-api-production-e07a.up.railway.app/api/video-info"

@app.get("/")
def root():
    return {"status": "Sub API working ✅"}

@app.get("/process")
async def process_youtube(url: str = Query(...), format: str = Query("video")):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{API_URL}?url={url}")
            data = resp.json()

        if not data.get("success"):
            return JSONResponse({"error": "Failed to fetch from main API"}, status_code=400)

        formats = data["data"]["formats"]
        title = data["data"]["title"].replace(" ", "_").replace("/", "_")

        if format == "audio":
            audio_url = formats["audio"]["url"]
            audio_path = await download_file(audio_url, "webm")
            final_path = os.path.join("temp", f"{title}.mp3")

            subprocess.run([
                "ffmpeg", "-i", audio_path, "-vn", "-ab", "192k", "-ar", "44100",
                "-y", final_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            return FileResponse(final_path, media_type="audio/mpeg", filename=f"{title}.mp3")

        elif format == "video":
            video_480p = next((v for v in formats["video"] if v["quality_label"] == "480p"), formats["video"][0])
            video_path = await download_file(video_480p["url"], "mp4")
            audio_path = await download_file(formats["audio"]["url"], "webm")

            merged_path = merge_audio_video(video_path, audio_path)
            return FileResponse(merged_path, media_type="video/mp4", filename=f"{title}.mp4")

        else:
            return JSONResponse({"error": "Invalid format. Use 'audio' or 'video'"}, status_code=400)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
