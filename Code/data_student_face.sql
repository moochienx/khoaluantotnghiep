-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Máy chủ: 127.0.0.1
-- Thời gian đã tạo: Th3 13, 2023 lúc 02:14 AM
-- Phiên bản máy phục vụ: 10.4.27-MariaDB
-- Phiên bản PHP: 8.0.25

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Cơ sở dữ liệu: `data_student_face`
--

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `history_check`
--

CREATE TABLE `history_check` (
  `msv` int(11) NOT NULL,
  `name` text NOT NULL,
  `date` text NOT NULL,
  `clas` text NOT NULL,
  `subject` text NOT NULL,
  `result` text NOT NULL,
  `day` varchar(50) NOT NULL,
  `time` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `infor_student`
--

CREATE TABLE `infor_student` (
  `msv` int(11) NOT NULL,
  `name` text NOT NULL,
  `date` text NOT NULL,
  `clas` text NOT NULL,
  `face_location` varchar(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `infor_student`
--

INSERT INTO `infor_student` (`msv`, `name`, `date`, `clas`, `face_location`) VALUES
(637906, 'Nguyen Van Chien', '27-12-2000', 'K63CNPMP', 'C:/Users/Moo/Desktop/Project_KL/‫Image/image1.png'),
(637906, 'Person 1', '30-11-2000', 'K63CNPMP', 'C:/Users/Moo/Desktop/Project_KL/‫Image/image10.png'),
(637906, 'Person 2', '22-06-2000', 'K63CNPMP', 'C:/Users/Moo/Desktop/Project_KL/‫Image/image2.png'),
(637906, 'Person 3', '31-05-2000', 'K63CNPMP', 'C:/Users/Moo/Desktop/Project_KL/‫Image/image3.png'),
(637906, 'Person 4', '30-09-2000', 'K63CNPMP', 'C:/Users/Moo/Desktop/Project_KL/‫Image/image4.png'),
(637906, 'Person 5', '24-01-2000', 'K63CNPMP', 'C:/Users/Moo/Desktop/Project_KL/‫Image/image5.png'),
(637906, 'Person 6', '23-08-2000', 'K63CNPMP', 'C:/Users/Moo/Desktop/Project_KL/‫Image/image6.png'),
(637906, 'Person 7', '30-09-2000', 'K63CNPMP', 'C:/Users/Moo/Desktop/Project_KL/‫Image/image7.png'),
(637906, 'Person 8', '18-10-2000', 'K63CNPMP', 'C:/Users/Moo/Desktop/Project_KL/‫Image/image8.png'),
(637906, 'Person 9', '12-06-2000', 'K63CNPMP', 'C:/Users/Moo/Desktop/Project_KL/‫Image/image9.png');

--
-- Chỉ mục cho các bảng đã đổ
--

--
-- Chỉ mục cho bảng `history_check`
--
ALTER TABLE `history_check`
  ADD PRIMARY KEY (`msv`,`day`,`time`);

--
-- Chỉ mục cho bảng `infor_student`
--
ALTER TABLE `infor_student`
  ADD PRIMARY KEY (`msv`,`face_location`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
