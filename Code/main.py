from gui import Ui_Main
import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QDate
import datetime
import numpy as np
import pandas as pd
import re
import cv2
import datetime
from connect_db import DataBase
from camera import Camera
from excel import Excel


class MyApplication:
    def __init__(self):
        #super().__init__()
        self.app = QtWidgets.QApplication(sys.argv)
        screen_resolution = self.app.desktop().screenGeometry()
        self.width, self.height = screen_resolution.width(), screen_resolution.height()
        self.Main = QtWidgets.QWidget()
        self.ui = Ui_Main()
        self.ui.setupUi(self.Main)

        self.message_box = QMessageBox()
        self.message_box.setWindowTitle("Thông báo !!")

        # Tự động căn chỉnh hàng cột
        self.ui.table_Student.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.ui.table_Student.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.table_Student.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.ui.table_Student.horizontalHeader().setSectionResizeMode(6, QtWidgets.QHeaderView.Stretch)

        self.ui.table_Data_Face.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.ui.table_Data_Face.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.ui.table_Data_Face.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.ui.table_Data_Face.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)

        self.ui.table_Data_history.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.table_Data_history.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.ui.table_Data_history.horizontalHeader().setSectionResizeMode(6, QtWidgets.QHeaderView.Stretch)
        self.ui.table_Data_history.horizontalHeader().setSectionResizeMode(7, QtWidgets.QHeaderView.Stretch)

        self.dialogs = []

        self.ui.date_Edit.setDateRange(QDate(1990, 1, 1), QDate.currentDate())
        self.set_number_cam()
        self.set_data()
        self.set_history_data()
        self.set_style(1)
        self.ui.verticalSlider.setValue(500)
        self.ui.label_check_level.setStyleSheet(" QLabel{ color: OrangeRed ; } ")
        self.ui.label_check_level.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.ui.label_check_level.setText("Tiêu Chuẩn\n60%")

        self.ui.class_Button.clicked.connect(self.select_excel_file)
        self.ui.check_Button.clicked.connect(self.start_check)
        self.ui.checked_Button.clicked.connect(self.end_checked)
        self.ui.link_save_Button.clicked.connect(self.get_link_save)
        self.ui.open_camera_Button.clicked.connect(self.open_camera)
        self.ui.get_face_Button.clicked.connect(self.get_face)
        self.ui.save_face_Button.clicked.connect(self.save_face)
        self.ui.re_Button.clicked.connect(self.re_set_data)
        self.ui.get_all_Button.clicked.connect(self.get_all_data)
        self.ui.update_Button.clicked.connect(self.update_data)
        self.ui.delete_Button.clicked.connect(self.delete_data)
        self.ui.get_Button.clicked.connect(self.get_data)
        self.ui.search_Button.clicked.connect(self.search_data)
        self.ui.tool_Button.clicked.connect(self.open_Menu)
        self.ui.verticalSlider.valueChanged.connect(self.get_level)
        self.ui.search_Button_history.clicked.connect(self.search_history)
        self.ui.reset_history_Button.clicked.connect(self.re_set_history_data)
        self.ui.yes_checkBox.stateChanged.connect(self.filter_data)
        self.ui.no_checkBox.stateChanged.connect(self.filter_data)

    def filter_data(self):
        show_yes = self.ui.yes_checkBox.isChecked()
        show_no = self.ui.no_checkBox.isChecked()
        num_row = self.ui.table_Data_history.rowCount()
        if not show_yes and not show_no:
            for i in range(num_row):
                self.ui.table_Data_history.setRowHidden(i, False)
        else:
            for i in range(num_row):
                item = self.ui.table_Data_history.item(i, 5)
                if (item.text() == "Có mặt" and not show_yes) or (item.text() == "Vắng mặt" and not show_no):
                    self.ui.table_Data_history.setRowHidden(i, True)
                else:
                    self.ui.table_Data_history.setRowHidden(i, False)

    def re_set_data(self):
        check = self.set_data()
        if not check:
            self.message_box.setText("Kết nối với cơ sở dữ liệu khuôn mặt thất bại!")
            self.message_box.exec_()

    def re_set_history_data(self):
        check = self.set_history_data()
        if not check:
            self.message_box.setText("Kết nối với cơ sở dữ liệu khuôn mặt thất bại!")
            self.message_box.exec_()

    def get_number_cam(self, id):
        if id == 1:
            # Lấy ra cam muốn điểm danh
            num_cam = self.ui.camera_comboBox.currentText()
        else:
            # Lấy ra cam muốn điểm danh
            num_cam = self.ui.camera_comboBox_get.currentText()
        # Sử dụng biểu thức chính quy để tìm số camera
        num_cam = re.findall(r'\d+', num_cam)
        # Ép kiểu số lượng sinh viên từ list sang int
        num_cam = num_cam[0]
        # Ép kiểu, trừ đi 1 vì số cam bắt đầu từ 0
        num_cam = int(num_cam)
        num_cam = num_cam - 1
        return num_cam

    def set_number_cam(self):
        cam = Camera()
        nb_cam = cam.check_number_cam()
        for i in range(nb_cam):
            self.ui.camera_comboBox.addItem(f"Camera {i + 1}", i)
            self.ui.camera_comboBox_get.addItem(f"Camera {i + 1}", i)

    def accept_data(self):
        accept = QMessageBox(self.Main)
        accept.setWindowTitle("Thông báo")
        accept.setText("Bạn có chắn chắn thực hiện ?")
        accept.addButton(QMessageBox.Yes).setText("Có!")
        accept.addButton(QMessageBox.No).setText("Không!")
        accept.setDefaultButton(QMessageBox.No)
        reply = accept.exec_()
        if reply == QMessageBox.No:
            return False
        else:
            return True

    def select_excel_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        self.file_name, _ = QFileDialog.getOpenFileName(self.Main, 'Chọn Tệp Excel', '',
                                                   'Tệp Excel (*.xlsx);', options=options)
        # Nhập tệp Excel, nếu tệp lỗi đưa ra thông báo
        if self.file_name:
            self.ui.checked_Button.setEnabled(False)
            ex = Excel()
            data = ex.get_excel_file(self.file_name)
            if data is False:
                self.message_box.setText("Đọc tệp thất bại! Vui lòng kiểm tra lại tệp")
                self.message_box.exec_()
                return 0
            else:
                # Lấy ra hàng cột của data Frame
                num_rows = data.shape[0]
                self.ui.table_Student.setRowCount(num_rows)
                num_cols = self.ui.table_Student.columnCount()
                for i in range(num_rows):
                    for j in range(num_cols - 2):
                        item = QtWidgets.QTableWidgetItem(str(data.iloc[i, j]))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.ui.table_Student.setItem(i, j, item)
            for i in range(num_rows):
                item_checked = QtWidgets.QTableWidgetItem("Chưa điểm danh")
                self.ui.table_Student.setItem(i, 5, item_checked)
                item_checked_date = QtWidgets.QTableWidgetItem(" ")
                self.ui.table_Student.setItem(i, 6, item_checked_date)
            self.ui.check_Button.setEnabled(True)
        self.ui.table_Student.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.ui.table_Student.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.table_Student.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.ui.table_Student.horizontalHeader().setSectionResizeMode(6, QtWidgets.QHeaderView.Stretch)

    def start_check(self):
        self.ui.open_camera_Button.setEnabled(False)
        self.ui.checked_Button.setEnabled(False)
        self.ui.check_Button.setEnabled(False)
        num_cam = self.get_number_cam(1)
        # Lấy ra chỉ số nhận diện khuôn mặt
        level = self.ui.verticalSlider.value()
        level = level / 1000
        # Mảng chứa mã sinh viên
        data = []
        # Lấy ra tổng số lượng msv(tổng số hàng)
        num_rows = self.ui.table_Student.rowCount()
        for i in range(num_rows):
            # Lấy ra giá trị mã sinh viên của hàng thứ i của cột Mã sinh viên
            value = self.ui.table_Student.item(i, 0).text()
            # Thêm giá trị vào mảng
            data.append(value)
        # Mảng có kiểu dữ liệu là Text, trong db để kiểu dữ liệu là int
        numbers_msv = list(map(int, data))
        cam = Camera()
        st_checked = cam.camera_check(numbers_msv, num_cam, level)
        if isinstance(st_checked, pd.DataFrame):
            # Kết quả điểm danh
            for i in range(num_rows):
                item_checked = QtWidgets.QTableWidgetItem("Có mặt")
                item_not_checked = QtWidgets.QTableWidgetItem("Vắng mặt")
                item_msv = self.ui.table_Student.item(i, 0).text()
                item_msv = int(item_msv)
                if item_msv in st_checked["msv"].values:
                    self.ui.table_Student.setItem(i, 5, item_checked)
                    item_time = str(st_checked.loc[st_checked['msv'] == item_msv, 'time'].values[0])
                    item_time = item_time.split(" ")
                    item_time = item_time[1]
                    # item_time = QtWidgets.QTableWidgetItem(str(st_checked.loc[st_checked['msv'] == item_msv, 'time'].values[0]))
                    item_time = QtWidgets.QTableWidgetItem(item_time)
                    item_time.setTextAlignment(Qt.AlignCenter)
                    self.ui.table_Student.setItem(i, 6, item_time)
                else:
                    self.ui.table_Student.setItem(i, 5, item_not_checked)
                    item_time = QtWidgets.QTableWidgetItem(datetime.datetime.now().strftime("%H:%M:%S"))
                    item_time.setTextAlignment(Qt.AlignCenter)
                    self.ui.table_Student.setItem(i, 6, item_time)
            self.ui.checked_Button.setEnabled(True)
        elif st_checked == 0:
            self.message_box.setText("Mở camera thất bại! \nVui lòng kiểm tra lại!")
            self.message_box.exec_()
        elif st_checked == 1:
            self.message_box.setText("Kết nối với cơ sở dữ liệu khuôn mặt thất bại !\n"
                                     "Vui lòng kiểm tra lại!")
            self.message_box.exec_()
        elif st_checked == 2:
            self.message_box.setText("Không có dữ liệu khuôn mặt của danh sách trên!\n"
                                     "Vui lòng kiểm tra lại!")
            self.message_box.exec_()
        self.ui.check_Button.setEnabled(True)
        self.ui.open_camera_Button.setEnabled(True)

    def end_checked(self):
        data_checked = []
        num_rows = self.ui.table_Student.rowCount()
        num_cols = self.ui.table_Student.columnCount()
        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
        for i in range(num_rows):
            item_msv = self.ui.table_Student.item(i, 5).text()
            data_checked.append(item_msv)
        result = pd.DataFrame(columns=["msv", "name", "name2", "date", "clas", "result", "time"])
        for i in range(num_rows):
            data = []
            for j in range(num_cols):
                item = self.ui.table_Student.item(i, j).text()
                data.append(item)
            data_insert = pd.DataFrame(pd.DataFrame([data], columns=result.columns))
            result = pd.concat([result, data_insert], axis=0)
        result["full_name"] = pd.concat([result["name"], result["name2"]], axis=1).agg(' '.join, axis=1)
        result = result.drop(["name", "name2"], axis=1)
        day = pd.DataFrame(index=result.index, columns=['day'])
        day["day"] = current_date
        result = pd.concat([result, day], axis=1)
        ex = Excel()
        cn = DataBase()
        try:
            write_data = ex.write_excel_file(self.file_name, data_checked)
            for index, row, in result.iterrows():
                cn.insert_history_data(row["msv"], row["full_name"], row["date"],
                                       row["clas"], row["result"], row["day"], row["time"], write_data)
        except Exception as e:
            self.message_box.setText("Lưu dữ liệu vào CSDL thất bại!")
            self.message_box.exec_()
            return False
        if write_data:
            self.message_box.setText("Dữ liệu điểm danh đã được lưu vào CSDL và tệp Excel!")
            self.message_box.exec_()
        else:
            self.message_box.setText("Lưu dữ liệu điểm danh thất bại! \nVui lòng đóng tệp nếu đang mở!")
            self.message_box.exec_()
        self.set_history_data()

    def get_link_save(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        self.link = QFileDialog.getExistingDirectory(self.Main, "Chọn thư mục", "", options=options)
        if self.link:
            self.ui.label_Link_Save.setText(self.link)
            self.ui.open_camera_Button.setEnabled(True)

    def open_camera(self):
        self.ui.check_Button.setEnabled(False)
        check = self.ui.label_Link_Save.text()
        img_name = self.ui.name_img_Line.text()
        if re.search(r'[\\/:*?"<>|]', img_name):
            self.message_box.setText("Tên ảnh không được chứa những ký tự dưới đây : "
                                     "\n/ \\ : * ? \" < > |")
            self.message_box.exec_()
            return 0
        elif check == "":
            self.message_box.setText("Vui lòng nhập chọn đường dẫn!")
            self.message_box.exec_()
            return 0
        elif img_name == "":
            self.message_box.setText("Vui lòng nhập tên ảnh!")
            self.message_box.exec_()
            return 0
        else:
            num_cam = self.get_number_cam(2)
            cam = Camera()
            get_img = cam.camera_photo(num_cam, self.link, img_name)
            if get_img is False:
                self.message_box.setText("Mở camera thất bại!\nVui lòng kiểm tra lại.")
                self.message_box.exec_()
                self.ui.check_Button.setEnabled(True)
                return 0
            elif get_img is None:
                self.ui.check_Button.setEnabled(True)
                return 0
            else:
                self.message_box.setText("Chụp ảnh thành công!")
                self.message_box.exec_()
                image = cv2.imread(self.link + '/' + img_name + ".png")
                cv2.imshow("Ảnh đã chụp", image)
        self.ui.check_Button.setEnabled(True)

    def get_face(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        self.file_name_img, _ = QFileDialog.getOpenFileName(self.Main, 'Chọn Ảnh', '', 'Ảnh (*.png *.jpg );',
                                                       options=options)
        if self.file_name_img:
            self.ui.label_img_get.setText(self.file_name_img)
            self.ui.save_face_Button.setEnabled(True)

    def save_face(self):
        msv = self.ui.msv_Line.text()
        name = self.ui.name_Line.text()
        date = self.ui.date_Edit.date().toString('dd-MM-yyyy')
        clas = self.ui.clas_Line.text()
        try:
            check_msv = int(msv)
        except ValueError:
            check_msv = False
        if msv == "" or name == "" or clas == "":
            self.message_box.setText("Vui lòng nhập đủ thông tin sinh viên!")
            self.message_box.exec_()
            return 0
        elif check_msv is False:
            self.message_box.setText("Vui lòng nhập đúng định dạng mã sinh viên!")
            self.message_box.exec_()
            return 0
        else:
            cn = DataBase()
            try:
                data = cn.insert_data(msv, name, date, clas, self.file_name_img)
            except Exception as e:
                self.message_box.setText("Thêm dữ liệu thất bại!\nVui lòng kiểm tra lại kết nối ")
                self.message_box.exec_()
                return False
            if data == 1:
                self.message_box.setText("Thêm dữ liệu thành công!")
                self.message_box.exec_()
                self.set_data()
            elif data == 2:
                self.message_box.setText("Thêm dữ liệu thất bại!\nDữ liệu này đã tồn tại! ")
                self.message_box.exec_()

    def set_data(self):
        cn = DataBase()
        try:
            data = cn.get_data()
        except Exception as e:
            return False
        # Lấy ra số hàng
        row = data.shape[0]
        # Thiết lập,lấy ra số hàng cột
        self.ui.table_Data_Face.setRowCount(row)
        num_col = self.ui.table_Data_Face.columnCount()
        num_row = self.ui.table_Data_Face.rowCount()
        for i in range(num_row):
            for j in range(num_col - 2):
                item = data.iloc[i, j]
                item = str(item)
                item = QtWidgets.QTableWidgetItem(item)
                item.setTextAlignment(Qt.AlignCenter)
                self.ui.table_Data_Face.setItem(i, j, item)

        for i in range(num_row):
            item = data.iloc[i, 2]
            item = str(item)
            item = item.split("-")
            date = QDate(int(item[2]), int(item[1]), int(item[0]))
            date_edit = QDateEdit(date, self.Main)
            date_edit.setCalendarPopup(True)
            date_edit.setDisplayFormat("dd-MM-yyyy")
            date_edit.setDateRange(QDate(1990, 1, 1), QDate.currentDate())
            date_edit.setStyleSheet("QDateEdit {font-size: 16px; font-family: Times New Roman;} ")
            self.ui.table_Data_Face.setCellWidget(i, 2, date_edit)

        for i in range(num_row):
            button = QPushButton("...", self.Main)
            button.clicked.connect(lambda state, row=i: self.select_Image(row))
            self.ui.table_Data_Face.setCellWidget(i, 5, button)
        for i in range(num_row):
            checkbox = QCheckBox()
            self.ui.table_Data_Face.setCellWidget(i, 6, checkbox)
        return True

    def select_Image(self, row):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name_img, _ = QFileDialog.getOpenFileName(self.Main, 'Chọn Ảnh', '', 'Ảnh (*.png *.jpg );',
                                                       options=options)
        if file_name_img:
            item = QtWidgets.QTableWidgetItem(file_name_img)
            self.ui.table_Data_Face.setItem(row, 4, item)

    def get_all_data(self):
        num_row = self.ui.table_Data_Face.rowCount()
        all_check = True
        for i in range(num_row):
            checkbox = self.ui.table_Data_Face.cellWidget(i, 6)
            if not checkbox.isChecked():
                all_check = False
                break
        if all_check:
            for i in range(num_row):
                checkbox = self.ui.table_Data_Face.cellWidget(i, 6)
                checkbox.setChecked(False)
        else:
            for i in range(num_row):
                checkbox = self.ui.table_Data_Face.cellWidget(i, 6)
                checkbox.setChecked(True)

    def update_data(self):
        cn = DataBase()
        try:
            data = cn.get_data()
        except Exception as e:
            self.message_box.setText("Kết nối với cơ sở dữ liệu khuôn mặt thất bại!")
            self.message_box.exec_()
            return False
        accept = self.accept_data()
        if accept is False:
            return 0
        num_row = self.ui.table_Data_Face.rowCount()
        raw_msv = []
        raw_face = []
        data_msv = []
        data_name = []
        data_face = []
        data_date = []
        data_clas = []
        for i in range(num_row):
            checkbox = self.ui.table_Data_Face.cellWidget(i, 6)
            if checkbox.isChecked():
                item_msv = self.ui.table_Data_Face.item(i, 0).text()
                data_msv.append(item_msv)
                item_name = self.ui.table_Data_Face.item(i, 1).text()
                data_name.append(item_name)
                item_date = self.ui.table_Data_Face.cellWidget(i, 2)
                item_date = item_date.date().toString('dd-MM-yyyy')
                data_date.append(item_date)
                item_clas = self.ui.table_Data_Face.item(i, 3).text()
                data_clas.append(item_clas)
                item_face = self.ui.table_Data_Face.item(i, 4).text()
                data_face.append(item_face)
                raw_msv.append(data.iloc[i, 0])
                raw_face.append(data.iloc[i, 4])
        i = 0
        result = []
        for x in data_msv:
            update_data = cn.update_data(x, data_name[i], data_date[i], data_clas[i], data_face[i], raw_msv[i],
                                         raw_face[i])
            if update_data is False:
                result.append(0)
            elif update_data is True:
                result.append(1)
            elif update_data == 2:
                result.append(2)
            i = i + 1
        count_True = result.count(1)
        count_False = result.count(0)
        self.message_box.setText(f"Số hàng sửa thành công: {count_True} hàng!\n"
                                 f"Số hàng sửa thất bại: {count_False} hàng!\n ")
        self.message_box.exec_()
        self.set_data()

    def delete_data(self):
        cn = DataBase()
        try:
            data = cn.get_data()
        except Exception as e:
            self.message_box.setText("Kết nối với cơ sở dữ liệu khuôn mặt thất bại!")
            self.message_box.exec_()
            return False
        accept = self.accept_data()
        if accept is False:
            return 0
        data_msv = []
        data_face = []
        num_row = self.ui.table_Data_Face.rowCount()
        for i in range(num_row):
            checkbox = self.ui.table_Data_Face.cellWidget(i, 6)
            if checkbox.isChecked():
                item_msv = self.ui.table_Data_Face.item(i, 0).text()
                data_msv.append(item_msv)
                item_face = self.ui.table_Data_Face.item(i, 4).text()
                data_face.append(item_face)
        i = 0
        result = []
        for x in data_msv:
            delete_data = cn.del_data(x, data_face[i])
            if delete_data is False:
                result.append(0)
            elif delete_data is True:
                result.append(1)
            i = i + 1
        count_True = result.count(1)
        count_False = result.count(0)
        self.message_box.setText(f"Số hàng xóa thành công: {count_True} hàng!\n"
                                 f"Số hàng xóa thất bại: {count_False} hàng! ")
        self.message_box.exec_()
        self.set_data()

    def close_dialogs(self):
        for dialog in self.dialogs:
            dialog.close()
        self.dialogs = []

    def get_data(self):
        self.close_dialogs()
        num_row = self.ui.table_Data_Face.rowCount()
        result = pd.DataFrame(columns=["msv", "name", "date", "clas", "face"])
        for i in range(num_row):
            checkbox = self.ui.table_Data_Face.cellWidget(i, 6)
            if checkbox.isChecked():
                item_msv = self.ui.table_Data_Face.item(i, 0).text()
                item_name = self.ui.table_Data_Face.item(i, 1).text()
                item_date = self.ui.table_Data_Face.cellWidget(i, 2)
                item_date = item_date.date().toString('dd-MM-yyyy')
                item_clas = self.ui.table_Data_Face.item(i, 3).text()
                item_face = self.ui.table_Data_Face.item(i, 4).text()
                data_date = pd.DataFrame({"msv": item_msv,
                                          "name": item_name,
                                          "date": item_date,
                                          "clas": item_clas,
                                          "face": item_face},
                                         index=[0])
                result = pd.concat([result, data_date], axis=0)
        x = 0
        y = 0

        dialog_size = (300, 300)
        num_cols = self.width // dialog_size[0]
        num_rows = (self.height + dialog_size[1] - 1) // dialog_size[1]
        max_dialogs = num_cols * num_rows
        num = result.shape[0]
        for i in range(num):
            if i >= max_dialogs:
                break
            dialog = QDialog(self.Main)
            dialog.setWindowTitle(f"{result.iloc[i, 1]}")
            dialog.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
            dialog.resize(*dialog_size)
            dialog.move(x, y)

            # Ảnh sinh viên
            image_layout = QHBoxLayout()
            image_label = QLabel(dialog)
            pixmap = QPixmap(result.iloc[i, 4])
            if pixmap.width() > dialog_size[0] // 2 or pixmap.height() > dialog_size[1] // 2:
                # Nếu ảnh quá to thì chỉnh lại kích thước
                pixmap = pixmap.scaledToWidth(dialog_size[0] // 2)
            if pixmap.isNull():
                # Không mở được ảnh thì hiển thị thông báo
                image_label.setText("Không mở được ảnh!!\n")
            else:
                image_label.setPixmap(pixmap)
            image_layout.addWidget(image_label)

            text_layout = QHBoxLayout()
            text_label = QLabel(f"Mã sinh viên: {result.iloc[i, 0]}"
                                f"\nHọ tên: {result.iloc[i, 1]}"
                                f"\nNgày sinh: {result.iloc[i, 2]}"
                                f"\nLớp: {result.iloc[i, 3]}",
                                dialog)
            text_layout.addWidget(text_label)

            main_layout = QVBoxLayout(dialog)
            main_layout.addLayout(text_layout)
            main_layout.addLayout(image_layout)
            main_layout.setAlignment(Qt.AlignCenter)

            self.dialogs.append(dialog)
            x += dialog_size[0]
            if x + dialog_size[0] > self.width:
                x = 0
                y += dialog_size[1] + 31
        num_created = len(self.dialogs)
        for dialog in self.dialogs:
            dialog.show()
        if num_created < num:
            self.message_box.setText(f"Đã đạt tới số lượng thông tin hiển thị "
                                     f"tối đa so với kích thước màn hình!\n")
            self.message_box.exec_()

    def search_data(self):
        cn = DataBase()
        try:
            data = cn.get_data()
        except Exception as e:
            self.message_box.setText("Kết nối với cơ sở dữ liệu khuôn mặt thất bại!")
            self.message_box.exec_()
            return False
        msv_check = []
        msv = self.ui.line_Search.text()
        try:
            check_msv = int(msv)
        except ValueError:
            check_msv = False
        if msv == "":
            self.message_box.setText("Vui lòng nhập mã sinh viên!")
            self.message_box.exec_()
            return 0
        elif check_msv is False:
            self.message_box.setText("Vui lòng nhập đúng định dạng mã sinh viên!")
            self.message_box.exec_()
            return 0
        msv = int(msv)
        msv_check.append(msv)
        data_check = data[data[0].isin(msv_check)]
        if data_check.empty:
            self.message_box.setText("Không tìm thấy thông tin sinh viên!")
            self.message_box.exec_()
            return 0
        num_col = self.ui.table_Data_Face.columnCount()
        num_row = data_check.shape[0]
        self.ui.table_Data_Face.setRowCount(num_row)
        self.ui.table_Data_Face.setColumnCount(num_col)
        for i in range(num_row):
            for j in range(num_col - 2):
                item = data_check.iloc[i, j]
                item = str(item)
                item = QtWidgets.QTableWidgetItem(item)
                item.setTextAlignment(Qt.AlignCenter)
                self.ui.table_Data_Face.setItem(i, j, item)
        for i in range(num_row):
            checkbox = QCheckBox()
            self.ui.table_Data_Face.setCellWidget(i, 6, checkbox)

    def open_Menu(self):
        dialog = QDialog()
        grid_layout = QGridLayout()
        dialog.setWindowTitle('Thiết lập')
        dialog.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        dialog.resize(400, 100)
        layout = QVBoxLayout(dialog)
        radio_1 = QRadioButton('Chế độ sáng')
        radio_2 = QRadioButton('Chế độ tối')
        button_group = QButtonGroup(dialog)
        button_group.addButton(radio_1)
        button_group.addButton(radio_2)
        layout.addWidget(radio_1)
        layout.addWidget(radio_2)
        if self.mode == 1:
            radio_1.setChecked(True)
        elif self.mode == 2:
            radio_2.setChecked(True)

        def radio_click(button):
            if button == radio_1:
                self.set_style(1)
            elif button == radio_2:
                self.set_style(2)

        button_group.buttonClicked.connect(radio_click)
        dialog.setLayout(grid_layout)
        dialog.exec_()

    def get_level(self):
        level_value = self.ui.verticalSlider.value()
        text = ""
        x = None

        if level_value >= 350 and level_value <= 353:
            self.ui.label_check_level.setStyleSheet(" QLabel{ color: Red ; } ")
            text = f"Cực Nghiêm Ngặt\n 1%"
        elif level_value > 353 and level_value <= 400:
            self.ui.label_check_level.setStyleSheet(" QLabel{ color: Red ; } ")
            x = (level_value - 350) / 250 * 100
            text = f"Cực Nghiêm Ngặt\n {int(x)}%"
        elif level_value > 400 and level_value <= 475:
            self.ui.label_check_level.setStyleSheet(" QLabel{ color: Crimson ; } ")
            x = (level_value - 350) / 250 * 100
            text = f"Nghiêm Ngặt\n {int(x)}%"
        elif level_value > 475 and level_value <= 525:
            self.ui.label_check_level.setStyleSheet(" QLabel{ color: OrangeRed ; } ")
            x = (level_value - 350) / 250 * 100
            text = f"Tiêu Chuẩn\n {int(x)}%"
        elif level_value > 525 and level_value <= 550:
            self.ui.label_check_level.setStyleSheet(" QLabel{ color: Green ; } ")
            x = (level_value - 350) / 250 * 100
            text = f"Cao\n {int(x)}%"
        elif level_value > 550 and level_value <= 600:
            self.ui.label_check_level.setStyleSheet(" QLabel{ color: Teal ; } ")
            x = (level_value - 350) / 250 * 100
            text = f"Cực Cao\n {int(x)}%"
        self.ui.label_check_level.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.ui.label_check_level.setText(text)

    def search_history(self):
        cn = DataBase()
        try:
            data = cn.get_history_data()
        except Exception as e:
            self.message_box.setText("Kết nối với cơ sở dữ liệu khuôn mặt thất bại!")
            self.message_box.exec_()
            return 0
        line_search = self.ui.line_Search_history.text()
        if line_search == "":
            self.message_box.setText("Vui lòng nhập thông tin cần tìm kiếm!")
            self.message_box.exec_()
            return 0
        msv_check = []
        if self.ui.msv_radioButton.isChecked():
            try:
                msv = int(line_search)
            except ValueError:
                msv = False
            if msv is False:
                self.message_box.setText("Vui lòng nhập đúng định dạng mã sinh viên!")
                self.message_box.exec_()
                return 0
            msv_check.append(msv)
            data_check = data[data[0].isin(msv_check)]
        elif self.ui.clas_radioButton.isChecked():
            msv = line_search
            msv_check.append(msv)
            data_check = data[data[3].isin(msv_check)]
        elif self.ui.subject_radioButton.isChecked():
            msv = line_search
            msv_check.append(msv)
            data_check = data[data[4].isin(msv_check)]
        elif self.ui.time_radioButton.isChecked():
            msv = line_search
            msv_check.append(msv)
            data_check = data[data[6].isin(msv_check)]

        if data_check.empty:
            self.message_box.setText("Không tìm thấy lịch sử điểm danh của sinh viên!")
            self.message_box.exec_()
            return 0
        num_col = self.ui.table_Data_history.columnCount()
        num_row = data_check.shape[0]
        self.ui.table_Data_history.setRowCount(num_row)
        self.ui.table_Data_history.setColumnCount(num_col)
        for i in range(num_row):
            for j in range(num_col):
                item = data_check.iloc[i, j]
                item = str(item)
                item = QtWidgets.QTableWidgetItem(item)
                item.setTextAlignment(Qt.AlignCenter)
                self.ui.table_Data_history.setItem(i, j, item)

    def set_history_data(self):
        cn = DataBase()
        try:
            data = cn.get_history_data()
        except Exception as e:
            return False
        # Lấy ra số hàng
        row = data.shape[0]
        # Thiết lập,lấy ra số hàng cột
        self.ui.table_Data_history.setRowCount(row)
        num_col = self.ui.table_Data_history.columnCount()
        num_row = self.ui.table_Data_history.rowCount()
        for i in range(num_row):
            for j in range(num_col):
                item = data.iloc[i, j]
                item = str(item)
                item = QtWidgets.QTableWidgetItem(item)
                item.setTextAlignment(Qt.AlignCenter)
                self.ui.table_Data_history.setItem(i, j, item)
        return True

    def set_style(self, mode):
        self.mode = mode
        light_Style = "QPushButton { background-color: #7FFFD4; } " \
                      "QPushButton:hover { background-color: #00FA9A; border-radius: 7px; } " \
                      "QSlider {background-color: #7FFFD4;} " \
                      "QSlider:hover {background-color: #00FA9A;border-radius: 7px; } " \
                      "QComboBox { background-color: #7FFFD4; } " \
                      "QComboBox:hover { background-color: #00FA9A; border-radius: 7px; } " \
                      "QTabBar::tab { background-color: #7FFFD4; } " \
                      "QTabBar::tab:hover { background-color: #00FA9A; } " \
                      "QLineEdit { background-color: #7FFFD4; } " \
                      "QLineEdit:hover { background-color: #00FA9A; border-radius: 7px; }" \
                      "QDateEdit QCalendarWidget QWidget { background-color: blue; color: white; }" \

        light_Form = "QToolButton { background-color: #7FFFD4; color: black; } " \
                     "QToolButton:hover { background-color: #00FA9A; border-radius: 7px; }"

        dark_Form = "QWidget { background-color: #1f1f1f; color: white; } " \
                    "QToolButton { background-color: #2c2c2c; color: white; } " \
                    "QToolButton:hover { background-color: #414141; border-radius: 7px; }"

        dark_Style = "QPushButton { background-color: #2c2c2c; color: white; } " \
                     "QPushButton:hover { background-color: #414141; border-radius: 7px; } " \
                     "QTableWidget { background-color: #242526; } " \
                     "QTableCornerButton::section { background-color: #242526; } " \
                     "QHeaderView::section{ background-color: #242526; } " \
                     "QComboBox { background-color: #2c2c2c; color: white; } " \
                     "QComboBox:hover { background-color: #414141; border-radius: 7px; } " \
                     "QSlider { background-color: #2c2c2c; color: white; } " \
                     "QSlider:hover { background-color: #414141; border-radius: 7px; } " \
                     "QTabBar::tab { background-color: #2c2c2c; } " \
                     "QTabBar::tab:hover { background-color: #414141; } " \
                     "QTabWidget::pane{ background-color: #2c2c2c; } " \
                     "QLineEdit { background-color: #2c2c2c; color: white; } " \
                     "QLineEdit:hover { background-color: #414141; border-radius: 7px; } "
        if mode == 1:
            self.app.setStyleSheet(light_Form)
            self.ui.tabWidget.setStyleSheet(light_Style)
        elif mode == 2:
            self.app.setStyleSheet(dark_Form)
            self.ui.tabWidget.setStyleSheet(dark_Style)

    def run(self):
        self.Main.show()
        self.app.exec_()

if __name__ == '__main__':
    app = MyApplication()
    app.run()
