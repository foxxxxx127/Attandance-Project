import face_recognition
import cv2
import numpy as np

def compare_faces(image_path1, image_path2, tolerance=0.4):
    """
    比对两张图片是否包含同一个人
    :param image_path1: 第一张图片路径
    :param image_path2: 第二张图片路径
    :param tolerance: 相似度阈值（0.4,值越小判断越严格）
    :return: True(同一人)/ False(不同人)
    """
    # 1. 加载图片并检测人脸
    img1 = face_recognition.load_image_file(image_path1)
    img2 = face_recognition.load_image_file(image_path2)

    # 2. 提取人脸特征
    encodings1 = face_recognition.face_encodings(img1)
    encodings2 = face_recognition.face_encodings(img2)

    # 检查是否检测到人脸
    if len(encodings1) == 0:
        raise ValueError(f"未在 {image_path1} 中检测到人脸")
    if len(encodings2) == 0:
        raise ValueError(f"未在 {image_path2} 中检测到人脸")

    # 3. 计算特征相似度
    distance = face_recognition.face_distance([encodings1[0]], encodings2[0])[0]
    
    # 4. 判断是否同一人
    return distance <= tolerance

if __name__ == "__main__":
    # 使用示例
    image1 = r"C:/Users/24187/Desktop/attandance/Attandance-Project/backend/face_recog/data/a8333c7273311ab28ec8a9fbac45c43.jpg"
    image2 = r"C:/Users/24187/Desktop/attandance/Attandance-Project/backend/face_recog/data/test_face.jpg"
    result = compare_faces(image1, image2)
    print("是否是同一个人：", result)