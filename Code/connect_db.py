import mysql.connector
import pandas as pd

class DataBase:
    def connect(self):
        try:
            # Cấu hình kết nối
            config = {
                'user': 'root',
                'password': '',
                'host': '127.0.0.1',
                'database': 'data_student_face'
            }
            # Tạo kết nối
            self.conn = mysql.connector.connect(**config)
            if self.conn:
                # Tạo đối tượng cursor
                self.cursor = self.conn.cursor()
            else:
                return False
        except mysql.connector.Error as error:
            return False

    def get_history_data(self):
        self.connect()
        # Thực hiện truy vấn
        query = 'SELECT * FROM history_check'
        try:
            self.cursor.execute(query)
            # Lấy kết quả truy vấn
            result = self.cursor.fetchall()
            data = pd.DataFrame(result)
            # Đóng cursor và kết nối
            self.cursor.close()
            self.conn.close()
            return data
        except mysql.connector.Error as error:
            self.cursor.close()
            self.conn.close()
            return False

    def insert_history_data(self, msv, name, date, clas, result, day, time, subject):
        self.connect()
        # Kiểm tra dữ liệu đã tồn tại hay chưa
        sql = "SELECT * FROM history_check WHERE msv=%s AND time=%s"
        self.cursor.execute(sql, (msv, time))
        if self.cursor.fetchone() is not None:
            self.cursor.close()
            self.conn.close()
            return 2
        # Thực hiện truy vấn
        query = "INSERT INTO history_check (msv, name, date, clas, result, day, time, subject) " \
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        try:
            self.cursor.execute(query, (msv, name, date, clas, result, day, time, subject))
            self.conn.commit()
            # Đóng cursor và kết nối
            self.cursor.close()
            self.conn.close()
            return 1
        except mysql.connector.Error as error:
            self.cursor.close()
            self.conn.close()
            return False

    def update_data(self, msv, name, date, clas, face_location, key_msv, key_face):
        self.connect()
        # Thực hiện truy vấn
        query = f"UPDATE infor_student SET " \
                f"msv = {msv}, " \
                f"name = '{name}', " \
                f"date = '{date}', " \
                f"clas = '{clas}', " \
                f"face_location = '{face_location}' " \
                f"WHERE msv = {key_msv} AND face_location = '{key_face}'"
        try:
            self.cursor.execute(query)
            self.conn.commit()
            self.cursor.close()
            self.conn.close()
            return True
        except mysql.connector.Error as error:
            self.cursor.close()
            self.conn.close()
            return False

    def del_data(self, msv, face_location):
        self.connect()
        query = "DELETE FROM infor_student WHERE msv = %s AND face_location = %s"
        try:
            self.cursor.execute(query, (msv, face_location))
            self.conn.commit()
            # Đóng cursor và kết nối
            self.cursor.close()
            self.conn.close()
            return True
        except mysql.connector.Error as error:
            self.cursor.close()
            self.conn.close()
            return False

    def insert_data(self, msv, name, date, clas, face_location):
        self.connect()
        # Kiểm tra dữ liệu đã tồn tại hay chưa
        sql = "SELECT * FROM infor_student WHERE msv=%s AND face_location=%s"
        self.cursor.execute(sql, (msv, face_location))
        if self.cursor.fetchone() is not None:
            self.cursor.close()
            self.conn.close()
            return 2
        # Thực hiện truy vấn
        query = "INSERT INTO infor_student (msv, name, date, clas, face_location) VALUES (%s, %s, %s, %s, %s)"
        try:
            self.cursor.execute(query, (msv, name, date, clas, face_location))
            self.conn.commit()

            # Đóng cursor và kết nối
            self.cursor.close()
            self.conn.close()
            return 1
        except mysql.connector.Error as error:
            self.cursor.close()
            self.conn.close()
            return False

    def get_data(self):
        self.connect()
        query = 'SELECT * FROM infor_student'
        try:
            self.cursor.execute(query)

            # Lấy kết quả truy vấn
            result = self.cursor.fetchall()
            data = pd.DataFrame(result)

            # Đóng cursor và kết nối
            self.cursor.close()
            self.conn.close()

            return data
        except mysql.connector.Error as error:
            self.cursor.close()
            self.conn.close()
            return False