from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./attendance.db"
    FACE_MODEL_PATH: str = "models/face_recognition_sface_2021dec.onnx"
    FACE_DETECTOR_PATH: str = "models/face_detection_yunet_2023mar.onnx"
    GPS_TOLERANCE_KM: float = 0.1
    FACE_MATCH_THRESHOLD: float = 0.5
    API_KEY: str = "secure-key-123"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()