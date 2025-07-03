from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import yt_dlp

app = FastAPI()

@app.get("/")
def root():
    return {"message": "YouTube API is working!"}

@app.get("/api/video-info")
def get_video_info(url: str = Query(..., description="YouTube video URL")):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'forcejson': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        audio_only = []
        video_with_audio = []

        for f in info['formats']:
            if f.get("filesize") is None or f.get("url") is None:
                continue

            entry = {
                "format_id": f["format_id"],
                "ext": f["ext"],
                "filesize_mb": round(f["filesize"] / (1024 * 1024), 2),
                "format_note": f.get("format_note", ""),
                "url": f["url"]
            }

            if f.get("height"):
                entry["resolution"] = f"{f['height']}p"

            if f.get("vcodec") == "none":
                audio_only.append(entry)
            elif f.get("acodec") != "none" and f.get("vcodec") != "none":
                video_with_audio.append(entry)

        return JSONResponse(content={
            "title": info.get("title"),
            "id": info.get("id"),
            "video_with_audio": video_with_audio,
            "audio_only": audio_only
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
