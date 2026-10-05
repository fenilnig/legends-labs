import os
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from typing import Dict, Any

from legends_labs.server.engines.fish_engine import FishSpeechEngine

from legends_labs.server.engine_manager import EngineManager

app = FastAPI(title="Legend's Labs Local Inference Server")

# Engine registry
engine_dict = {
    "Fish Speech 1.5": FishSpeechEngine()
}
engine_manager = EngineManager(engine_dict)

def verify_token(token: str):
    expected = os.environ.get("LL_API_TOKEN")
    if not expected or token != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    return True

@app.websocket("/ws/inference/tts")
async def tts_websocket(websocket: WebSocket):
    await websocket.accept()
    
    try:
        # Expect first message to be authentication
        auth_data = await websocket.receive_json()
        token = auth_data.get("token")
        
        try:
            verify_token(token)
            await websocket.send_json({"status": "authenticated"})
        except HTTPException:
            await websocket.send_json({"error": "Unauthorized"})
            await websocket.close()
            return

        # Wait for the generation payload
        payload = await websocket.receive_json()
        engine_name = payload.get("engine", "Mock")
        text = payload.get("text", "")
        reference_audio = payload.get("reference_audio", "")
        reference_text = payload.get("reference_text", "")
        output_path = payload.get("output_path", "")
        emotion_level = payload.get("emotion_level", 50)
            
        engine = engine_manager.get_engine(engine_name)
        
        try:
            # Check if engine takes emotion_level via inspection or just pass it as kwargs
            # For our scaffold, only Chatterbox takes emotion_level currently, but we can pass it via kwargs safely
            import inspect
            sig = inspect.signature(engine.generate)
            kwargs = {}
            if "emotion_level" in sig.parameters:
                kwargs["emotion_level"] = emotion_level
            if "reference_text" in sig.parameters:
                kwargs["reference_text"] = reference_text
                
            async for progress_update in engine.generate(text, reference_audio, output_path, **kwargs):
                await websocket.send_json(progress_update)
        except Exception as e:
            import traceback
            tb_str = traceback.format_exc()
            print(f"INFERENCE ERROR: {str(e)}\n{tb_str}")
            await websocket.send_json({"error": str(e), "traceback": tb_str})
            
        await websocket.close()
        
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket Error: {e}")

if __name__ == "__main__":
    uvicorn.run("legends_labs.server.main:app", host="127.0.0.1", port=54321, log_level="info")
