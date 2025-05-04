import cv2
import numpy as np
from typing import Optional
from app.config.settings import settings

class FaceRecognitionService:
    def __init__(self):
        self.detector = cv2.FaceDetectorYN_create(
            settings.FACE_DETECTOR_PATH, 
            "", 
            (320, 320)
        )
        self.recognizer = cv2.FaceRecognizerSF_create(
            settings.FACE_MODEL_PATH, 
            ""
        )

    def process_image(self, image_bytes: bytes) -> np.ndarray:
        """将字节流转换为OpenCV图像格式"""
        return cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)

    def detect_faces(self, image: np.ndarray) -> Optional[list]:
        """人脸检测"""
        _, faces = self.detector.detect(image)
        return faces

    def get_face_encoding(self, image: np.ndarray) -> Optional[np.ndarray]:
        """获取人脸特征编码"""
        faces = self.detect_faces(image)
        if not faces:
            return None
            
        # 选择最大人脸并对齐
        largest_face = max(faces, key=lambda f: f[2]*f[3])
        aligned = self.recognizer.alignCrop(image, largest_face)
        return self.recognizer.feature(aligned)

    def verify_face(
        self, 
        current_encoding: np.ndarray, 
        registered_encodings: list
    ) -> float:
        """人脸比对验证"""
        return max(
            self.recognizer.match(current_encoding, reg_enc, cv2.FaceRecognizerSF_FR_COSINE)
            for reg_enc in registered_encodings
        )