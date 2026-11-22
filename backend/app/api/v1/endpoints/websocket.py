from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Optional
import json
import asyncio
from app.ml.recognition_engine import recognition_engine
from app.services.translation_service import translation_service
from app.core.database import AsyncSessionLocal
from app.db.repositories.session_repo import SessionRepository

router = APIRouter(tags=["Real-Time Streaming WebSocket"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_json(self, websocket: WebSocket, data: Dict[str, Any]):
        await websocket.send_text(json.dumps(data))

manager = ConnectionManager()

@router.websocket("/ws/recognize")
async def websocket_recognition_endpoint(websocket: WebSocket):
    """
    Ultra-low latency bidirectional WebSocket:
    Receives continuous 21-landmark arrays from client browser;
    Performs real-time normalizer, classification, temporal smoothing,
    and returns immediate prediction + live sentence updates.
    """
    await manager.connect(websocket)
    session_tokens: List[str] = []
    current_session_id: Optional[str] = None

    try:
        while True:
            raw_text = await websocket.receive_text()
            try:
                data = json.loads(raw_text)
            except Exception:
                continue

            msg_type = data.get("type", "frame")

            if msg_type == "init":
                current_session_id = data.get("session_id")
                session_tokens = []
                recognition_engine.reset_state()
                await manager.send_json(websocket, {
                    "type": "init_ack",
                    "status": "connected",
                    "session_id": current_session_id
                })

            elif msg_type == "frame":
                landmarks = data.get("landmarks", [])
                handedness = data.get("handedness", "Right")
                model_pref = data.get("model", "landmarknet")
                raw_pixel_points = data.get("raw_pixel_points")
                bbox = data.get("bbox")

                if len(landmarks) == 21:
                    pred_res = recognition_engine.process_frame(
                        landmarks=landmarks,
                        handedness=handedness,
                        model_preference=model_pref,
                        raw_pixel_points=raw_pixel_points,
                        bbox=bbox
                    )

                    # Dynamic word triggers take precedence
                    dyn_word = pred_res.get("dynamic_word")
                    if dyn_word:
                        session_tokens.append(dyn_word)
                        # Re-calculate sentence
                        trans = translation_service.assemble_sentence(session_tokens)
                        await manager.send_json(websocket, {
                            "type": "dynamic_word",
                            "word": dyn_word,
                            "confidence": pred_res.get("dynamic_confidence", 0.9),
                            "sentence": trans["sentence"],
                            "tts_text": trans["tts_text"],
                            "latency_ms": pred_res["latency_ms"]
                        })
                    else:
                        # Static alphabet token stabilization
                        if pred_res["is_new_token"] and not pred_res["is_unknown"]:
                            active_token = pred_res["active_stable_label"]
                            session_tokens.append(active_token)
                            trans = translation_service.assemble_sentence(session_tokens)

                            # Record in DB if session active
                            if current_session_id:
                                async with AsyncSessionLocal() as db:
                                    repo = SessionRepository(db)
                                    await repo.add_prediction(
                                        session_id=current_session_id,
                                        predicted_label=active_token,
                                        confidence=pred_res["confidence"],
                                        top3=pred_res["top3"],
                                        latency_ms=pred_res["latency_ms"]
                                    )

                            await manager.send_json(websocket, {
                                "type": "new_token",
                                "token": active_token,
                                "sentence": trans["sentence"],
                                "current_word": trans["current_word"],
                                "suggestions": trans["suggestions"],
                                "tts_text": trans["tts_text"]
                            })

                        # Always broadcast current live frame state
                        await manager.send_json(websocket, {
                            "type": "prediction",
                            "label": pred_res["label"],
                            "stabilized_label": pred_res["stabilized_label"],
                            "confidence": pred_res["confidence"],
                            "is_unknown": pred_res["is_unknown"],
                            "top3": pred_res["top3"],
                            "latency_ms": pred_res["latency_ms"],
                            "stability_ratio": pred_res["stability_ratio"],
                            "model_used": pred_res["model_used"]
                        })

            elif msg_type == "commit_word":
                # User selected one of the suggested words
                chosen_word = data.get("word")
                if chosen_word:
                    # Remove characters of current partial word and replace with chosen_word
                    trans = translation_service.assemble_sentence(session_tokens)
                    curr = trans["current_word"]
                    for _ in range(len(curr)):
                        if session_tokens:
                            session_tokens.pop()
                    session_tokens.append(chosen_word)
                    session_tokens.append("SPACE")
                    new_trans = translation_service.assemble_sentence(session_tokens)
                    await manager.send_json(websocket, {
                        "type": "sentence_update",
                        "sentence": new_trans["sentence"],
                        "current_word": "",
                        "suggestions": [],
                        "tts_text": new_trans["tts_text"]
                    })

            elif msg_type == "clear":
                session_tokens.clear()
                recognition_engine.reset_state()
                await manager.send_json(websocket, {
                    "type": "sentence_update",
                    "sentence": "",
                    "current_word": "",
                    "suggestions": [],
                    "tts_text": ""
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)
