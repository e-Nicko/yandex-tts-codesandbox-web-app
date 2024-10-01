from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from pydantic import BaseModel
import uvicorn
from datetime import datetime
from utils import (
    get_iam_token_from_sa_key,
    synthesize_text,
    upload_audio_to_object_storage,
    recognize_speech_long_running,
    get_recognition_result
)

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Замените на конкретные домены в продакшене
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextToSpeechRequest(BaseModel):
    text: str

# Подключаем папку со статическими файлами
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/ui/", response_class=HTMLResponse)
async def ui():
    with open("static/index.html", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/")
async def read_root():
    return {
        "service": "HighlightReader API",
        "status": "running",
        "version": "1.0.0",
        "description": "This API allows you to synthesize text to speech and align spoken words with timestamps.",
        "documentation_url": "/docs",
        "developer_contact": {
            "email": "e-Nicko@ya.ru",
            "github": "https://github.com/e-Nicko"
        },
        "server_time": datetime.utcnow().isoformat() + "Z"
    }

@app.post("/synthesize")
async def synthesize(request: TextToSpeechRequest):
    try:
        iam_token = get_iam_token_from_sa_key()
        if not iam_token:
            raise HTTPException(status_code=500, detail="Failed to obtain IAM token")

        audio_file = synthesize_text(iam_token, request.text)
        if not audio_file:
            raise HTTPException(status_code=500, detail="Failed to synthesize speech")

        audio_uri = upload_audio_to_object_storage(audio_file)
        if not audio_uri:
            raise HTTPException(status_code=500, detail="Failed to upload audio file")

        operation_id = recognize_speech_long_running(iam_token, audio_uri)
        if not operation_id:
            raise HTTPException(status_code=500, detail="Failed to start speech recognition")

        recognition_result = get_recognition_result(iam_token, operation_id)
        if not recognition_result:
            raise HTTPException(status_code=500, detail="Failed to get recognition result")

        result = {
            "audio_url": audio_uri,
            "original_text": request.text,
            "words": []
        }

        for chunk in recognition_result:
            alternatives = chunk.get('alternatives', [])
            for alternative in alternatives:
                words = alternative.get('words', [])
                for word_info in words:
                    start_time = int(float(word_info['startTime'].rstrip('s')) * 1000)
                    end_time = int(float(word_info['endTime'].rstrip('s')) * 1000)
                    result["words"].append({
                        "word": word_info['word'],
                        "start_time": start_time,
                        "end_time": end_time
                    })
        return result

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)