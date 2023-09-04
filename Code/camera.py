import face_recognition
import cv2
import numpy as np
import pandas as pd
import datetime
from connect_db import DataBase

class Camera():

    def open_camera(self, cam):
        # Mở webcam
        self.video_capture = cv2.VideoCapture(cam)
        # Không mở được camera thì trả về 0
        if not self.video_capture.isOpened():
            return False

    def check_number_cam(self):
        # Khởi tạo camera = 0
        num_cameras = 0
        i = 0
        # Lặp lại cho đến khi không mở được camera
        while True:
            # Mở camera
            camera = cv2.VideoCapture(i)
            # Kiểm tra xem camera có mở được hay không
            if camera.isOpened():
                # Nếu mở đc thì tiếp tục mở camera tiếp theo
                num_cameras += 1
                # Đóng camera
                camera.release()
                # Tăng số lượng camera lên 1
                i += 1
            else:
                # Nếu không còn camera thì dừng
                break
        if num_cameras == 0:
            return 1
        else:
            return num_cameras

    def camera_photo(self, cam, link, img_name):
        self.open_camera(cam)
        while True:
            # Đọc khung hình từ video
            ret, frame = self.video_capture.read()

            # Kiểm tra xem có đọc được khung hình hay không
            if not ret:
                break
            # Chỉnh kích thước frame về bằng một nửa và tỷ lệ thuận với màn hình
            frame = cv2.resize(frame, None, fx=0.50, fy=0.50, interpolation=cv2.INTER_LINEAR)

            # Hiển thị hình ảnh kết quả
            cv2.imshow('Camera', frame)

            # Ấn Enter Lưu ảnh
            img_save = link + '/' + img_name + ".png"

            wait_key = cv2.waitKey(1)

            if wait_key == 13:
                cv2.imwrite(img_save, frame)
                # Giải phóng dữ liệu
                self.video_capture.release()
                cv2.destroyAllWindows()
                return True
            # Ấn ESC để thoát camera
            elif wait_key == 27:
                # Giải phóng dữ liệu
                self.video_capture.release()
                cv2.destroyAllWindows()
                return None
    def camera_check(self, msv, cam, level):
        self.open_camera(cam)
        if not self.video_capture.isOpened():
            return 0

        # Lấy ra tất cả các sinh viên
        cn = DataBase()
        try:
            data = cn.get_data()
        except Exception as e:
            return 1
        # Biến copy ra các sinh viên cần điểm danh từ tổng cơ sở dữ liệu
        data_check = data[data[0].isin(msv)]
        if data_check.empty:
            return 2
        else:
            # Lấy ra số hàng của data
            len_face = len(data_check)
        # Khởi tạo biến
        face_img_loca = []
        known_face = [] #
        known_name = [] #
        known_msv = [] #
        result = pd.DataFrame(columns=["msv", "time"])

        # Lấy ra và lưu tên
        for x in range(len_face):
            known_msv.append(data_check.iloc[x, 0])
            known_name.append(data_check.iloc[x, 1])
        # Lấy ra và lưu địa chỉ ảnh
        for x in range(len_face):
            face_img_loca.append(data_check.iloc[x, 4])
        # Lấy ra ảnh, tạo mảng mã hóa chứa khuôn mặt đã của những người đã biết
        for x in face_img_loca:
            image = face_recognition.load_image_file(x)
            known_face.append(face_recognition.face_encodings(image)[0])

        # Khởi tạo biến
        location = []
        encoding = []

        while True:
            # Đọc khung hình từ video
            ret, frame = self.video_capture.read()

            # Kiểm tra xem có đọc được khung hình hay không
            if not ret:
                break

            # Chỉnh kích thước frame nhỏ lại và tỷ lệ thuận với màn hình
            frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_LINEAR)

            # Thay đổi kích thước khung hình của video thành kích thước 1/4 để xử lý nhận dạng khuôn mặt nhanh hơn
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert BGR (màu OpenCV sử dụng) sang màu RGB
            rgb_small_frame = small_frame[:, :, ::-1]

            # Tìm tất cả các khuôn mặt và mã hóa khuôn mặt trong khung hình hiện tại của video
            location = face_recognition.face_locations(rgb_small_frame)
            encoding = face_recognition.face_encodings(rgb_small_frame, location)
            face_landmarks = face_recognition.face_landmarks(rgb_small_frame, location)

            face_names = []
            face_msv = []
            for face in encoding:
                # Xem khuôn mặt có khớp với các khuôn mặt đã biết không
                find = face_recognition.compare_faces(known_face, face, tolerance=level)
                name = "Khong Co Du Lieu"
                # So sánh khuôn mặt với khuôn mặt đã biết với độ trùng khớp nhỏ nhất
                face_distances = face_recognition.face_distance(known_face, face)
                # Lấy ra khuôn mặt có độ trùng khớp nhất
                finded = np.argmin(face_distances)
                # Nếu khuôn mặt này trùng với khuôn mặt đã biết thì gán tên, msv
                if find[finded]:
                    name = known_name[finded]
                    msv = known_msv[finded]
                    # Ép kiểu sang text để vẽ lên khuôn mặt
                    text_msv = str(msv)
                face_names.append(name)

                if name != "Khong Co Du Lieu":
                    face_msv.append(text_msv)
                    for i in range(len(data_check)):
                        if data_check.iloc[i][0] == msv:
                            current_datetime = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                            data_date = pd.DataFrame({"msv": [data_check.iloc[i][0]], "time": [current_datetime]})
                            result = pd.concat([result, data_date], axis=0)
                else:
                    face_msv.append(" ")

            # Hiển thị kết quả
            for (top, right, bottom, left), name, msv, landmarks in zip(location, face_names, face_msv, face_landmarks):
                # Tăng các thông số lên 4 lần vì kích thước xử lý nhận dạng là 1/4
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Vẽ hình xung quanh khuôn mặt
                # Góc trên bên trái
                cv2.line(frame, (left, top), (left, top + 15), (255, 128, 0), 3)
                cv2.line(frame, (left, top), (left + 15, top), (255, 128, 0), 3)

                # Góc trên bên phải
                cv2.line(frame, (right, top), (right, top + 15), (255, 128, 0), 3)
                cv2.line(frame, (right, top), (right - 15, top), (255, 128, 0), 3)

                # Góc dưới bên trái
                cv2.line(frame, (left, bottom), (left, bottom - 15), (255, 128, 0), 3)
                cv2.line(frame, (left, bottom), (left + 15, bottom), (255, 128, 0), 3)

                # Góc dưới bên phải
                cv2.line(frame, (right, bottom), (right, bottom - 15), (255, 128, 0), 3)
                cv2.line(frame, (right, bottom), (right - 15, bottom), (255, 128, 0), 3)


                cv2.putText(frame, name, (left, bottom + 30), cv2.FONT_HERSHEY_COMPLEX, 0.75, (0, 0, 0), 5)
                cv2.putText(frame, name, (left, bottom + 30), cv2.FONT_HERSHEY_COMPLEX, 0.75, (255, 255, 255), 1)
                cv2.putText(frame, msv, (left, bottom + 60), cv2.FONT_HERSHEY_COMPLEX, 0.75, (0, 0, 0), 5)
                cv2.putText(frame, msv, (left, bottom + 60), cv2.FONT_HERSHEY_COMPLEX, 0.75, (255, 255, 255), 1)

                for landmark_type, landmark_points in landmarks.items():
                    for point in landmark_points:
                        # Tăng kích thước vị trí lên 4 lần
                        scaled_point = (4 * point[0], 4 * point[1])
                        cv2.circle(frame, scaled_point, 1, (255, 128, 0), -1)

            # Hiển thị hình ảnh kết quả
            cv2.imshow('Camera', frame)

            # Ấn ESC để thoát camera
            if cv2.waitKey(1) == 27:
                break

        # Giải phóng dữ liệu
        self.video_capture.release()
        cv2.destroyAllWindows()
        result = result.drop_duplicates(subset='msv', keep='last')
        return result







