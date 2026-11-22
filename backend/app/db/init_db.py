import asyncio
from datetime import datetime
from sqlalchemy import select
from app.core.database import engine, Base, AsyncSessionLocal
from app.core.security import get_password_hash
from app.db.models import User, UserProfile, ModelVersion, RecognitionSession, RecognitionPrediction, TranslationHistory

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables initialized successfully.")

async def seed_data():
    async with AsyncSessionLocal() as session:
        # Check if admin user exists
        stmt = select(User).where(User.email == "admin@signbridge.ai")
        result = await session.execute(stmt)
        admin = result.scalar_one_or_none()

        if not admin:
            admin = User(
                email="admin@signbridge.ai",
                hashed_password=get_password_hash("AdminPass123!"),
                full_name="SignBridge Admin",
                role="admin",
                is_active=True
            )
            session.add(admin)
            await session.flush()

            admin_profile = UserProfile(
                user_id=admin.id,
                preferred_language="en-US",
                enable_tts_auto=True,
                speech_rate=1.0,
                theme_preference="dark",
                confidence_threshold=0.65
            )
            session.add(admin_profile)
            print("Seeded default admin: admin@signbridge.ai / AdminPass123!")

        # Check if demo user exists
        stmt_user = select(User).where(User.email == "demo@signbridge.ai")
        result_user = await session.execute(stmt_user)
        demo = result_user.scalar_one_or_none()

        if not demo:
            demo = User(
                email="demo@signbridge.ai",
                hashed_password=get_password_hash("DemoPass123!"),
                full_name="Sarah Jenkins",
                role="user",
                is_active=True
            )
            session.add(demo)
            await session.flush()

            demo_profile = UserProfile(
                user_id=demo.id,
                preferred_language="en-US",
                enable_tts_auto=True,
                speech_rate=1.0,
                theme_preference="dark",
                confidence_threshold=0.65
            )
            session.add(demo_profile)
            print("Seeded default demo user: demo@signbridge.ai / DemoPass123!")

        # Seed model versions
        alphabet_classes = [chr(i) for i in range(ord('A'), ord('Z')+1)] + ["SPACE", "DEL"]
        dynamic_classes = ["HELLO", "YES", "NO", "THANK_YOU", "PLEASE", "COME", "OK", "HELP", "STOP", "GOODBYE"]

        models_to_seed = [
            {
                "model_name": "SignBridge LandmarkNet v1.0",
                "version_tag": "landmarknet-v1.0",
                "framework": "pytorch/onnx",
                "model_type": "static_alphabet",
                "classes": alphabet_classes,
                "input_shape": [21, 3],
                "test_accuracy": 0.984,
                "latency_ms": 2.1,
                "description": "Normalized 21 3D wrist-relative hand landmark multi-layer classifier for 26 ASL alphabet signs and static controls.",
                "is_active": True,
                "is_default": True
            },
            {
                "model_name": "SignBridge Temporal BiLSTM v1.0",
                "version_tag": "bilstm-v1.0",
                "framework": "tensorflow/keras",
                "model_type": "dynamic_words",
                "classes": dynamic_classes,
                "input_shape": [20, 63],
                "test_accuracy": 0.962,
                "latency_ms": 5.8,
                "description": "20-frame temporal recurrent BiLSTM sequence model for dynamic conversational ASL gestures.",
                "is_active": True,
                "is_default": False
            },
            {
                "model_name": "Legacy 8-Group CNN (Preserved)",
                "version_tag": "cnn8grps-legacy",
                "framework": "keras/h5",
                "model_type": "hybrid",
                "classes": alphabet_classes,
                "input_shape": [400, 400, 3],
                "test_accuracy": 0.915,
                "latency_ms": 24.5,
                "description": "Original pre-trained cnn8grps_rad1_model.h5 with synthetic skeleton canvas drawing and heuristic disambiguation.",
                "is_active": True,
                "is_default": False
            }
        ]

        for m_info in models_to_seed:
            stmt_m = select(ModelVersion).where(ModelVersion.version_tag == m_info["version_tag"])
            existing_m = (await session.execute(stmt_m)).scalar_one_or_none()
            if not existing_m:
                mv = ModelVersion(**m_info)
                session.add(mv)
                print(f"Seeded model version: {m_info['model_name']}")

        await session.commit()
        print("Database seeding completed.")

async def main():
    await init_models()
    await seed_data()

if __name__ == "__main__":
    asyncio.run(main())
