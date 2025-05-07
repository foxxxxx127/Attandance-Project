import cv2
import numpy as np
import pytest
import Face_recognition_service
import setting

class TestFaceRecognition:
    @pytest.fixture(autouse=True)
    def setup(self):
        """初始化测试环境"""
        self.service = Face_recognition_service()
        self.valid_image = cv2.imread("tests/data/test_face.jpg")
        _, self.img_bytes = cv2.imencode(".jpg", self.valid_image)
    
    def test_process_image_valid(self):
        """测试有效的图像处理"""
        processed = self.service.process_image(self.img_bytes.tobytes())
        assert isinstance(processed, np.ndarray)
        assert processed.shape == self.valid_image.shape

    def test_detect_faces_single(self):
        """测试单人脸检测"""
        processed = self.service.process_image(self.img_bytes.tobytes())
        faces = self.service.detect_faces(processed)
        assert len(faces) == 1

    def test_feature_extraction(self):
        """测试特征提取有效性"""
        processed = self.service.process_image(self.img_bytes.tobytes())
        encoding = self.service.get_face_encoding(processed)
        assert encoding is not None
        assert encoding.shape == (256,)  # 根据实际模型维度调整

    def test_verification_accuracy(self):
        """测试比对准确性"""
        # 准备测试数据
        processed = self.service.process_image(self.img_bytes.tobytes())
        encoding1 = self.service.get_face_encoding(processed)
        
        # 同一人的不同照片
        img2 = cv2.imread("tests/data/test_face_variant.jpg") 
        encoding2 = self.service.get_face_encoding(img2)
        
        # 不同人的照片
        img3 = cv2.imread("tests/data/another_face.jpg")
        encoding3 = self.service.get_face_encoding(img3)

        # 验证相似度
        same_score = self.service.verify_face(encoding1, [encoding2])
        diff_score = self.service.verify_face(encoding1, [encoding3])
        
        assert same_score > 0.7  # 同一人阈值
        assert diff_score < 0.3  # 不同人阈值

    def test_no_face_handling(self):
        """测试无人脸场景处理"""
        no_face_img = cv2.imread("tests/data/no_face.jpg")
        encoding = self.service.get_face_encoding(no_face_img)
        assert encoding is None

if __name__ == "__main__":
    pytest.main(["-s", __file__])