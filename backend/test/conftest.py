# 位置：项目根目录/tests/conftest.py
import pytest
import cv2
import numpy as np
from src.face_recognition_service import FaceRecognitionService

@pytest.fixture(scope="session")
def recognition_service():
    """全局共享的人脸识别服务实例"""
    return face_recognition_service()

@pytest.fixture
def sample_image():
    """测试用标准人脸图片"""
    img = cv2.imread("test/data/face.jpg")
    assert img is not None, "测试图片加载失败"
    return img

@pytest.fixture
def multi_face_image():
    """含多个人脸的测试图片"""
    img = cv2.imread("test/data/faces.jpg")
    assert img is not None, "多人脸测试图片加载失败"
    return img

@pytest.fixture
def no_face_image():
    """无人脸的测试图片"""
    img = cv2.imread("test/data/no_face.jpg")
    assert img is not None, "无人脸测试图片加载失败"
    return img

@pytest.fixture
def encoded_image(sample_image):
    """已编码的图片字节流"""
    _, img_bytes = cv2.imencode(".jpg", sample_image)
    return img_bytes.tobytes()

def pytest_addoption(parser):
    """自定义命令行参数"""
    parser.addoption("--slow", action="store_true", default=False, help="运行耗时长的测试")