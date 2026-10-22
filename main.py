import sys
import pathlib

import numpy
import cv2

import PyQt5.QtWidgets

import 图像增强

当前路径 = pathlib.Path(__file__).absolute().parent

if __name__ == "__main__":
	应用实例 = PyQt5.QtWidgets.QApplication(sys.argv)

	图1 = cv2.imdecode(numpy.fromfile(当前路径 / "图片" / "1.jpg", dtype="uint8"), cv2.IMREAD_COLOR_BGR)
	图2 = cv2.imdecode(numpy.fromfile(当前路径 / "图片" / "2.jpg", dtype="uint8"), cv2.IMREAD_COLOR_BGR)

	增强管理器 = 图像增强.增强管理器(图1)
	增强管理器.设置参数()

	增强管理器.更换效果图例(图2)
	增强管理器.设置参数()

	cv2.imshow("pic 1", 增强管理器.图像增强(图1))
	cv2.imshow("pic 2", 增强管理器.图像增强(图2))
	cv2.waitKey()
	cv2.destroyAllWindows()

	sys.exit(0)
