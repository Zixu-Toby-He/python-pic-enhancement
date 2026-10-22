from __future__ import annotations

import numpy
import cv2

"""
参数
	图片
		BGR888 格式
	同图灰度图
		参数调整的时候这些增强函数可能被反复调用，外部提前算好灰度图可以节省 cv2.cvtColor 开销
		支持二维纯灰度图格式，也支持三张灰度图硬拼格式
	上/下限
		上游不保证大小，需要适时交换顺序
"""

def 获取图像增强函数_保持不变():
	def 增强函数(图片:numpy.ndarray, 同图灰度图: numpy.ndarray | None = None):
		return 图片
	return 增强函数


def 获取图像增强函数_线性拓展(上限, 下限):
	def 增强函数(图片:numpy.ndarray, 同图灰度图: numpy.ndarray | None = None, 上限 = 上限, 下限 = 下限):
		if 同图灰度图 is None:
			同图灰度图 = cv2.cvtColor(图片, cv2.COLOR_BGR2GRAY)
		if 同图灰度图.ndim == 2:
			同图灰度图 = cv2.merge([同图灰度图, 同图灰度图, 同图灰度图])
		if 上限 < 下限:
			上限, 下限 = 下限, 上限
		if 上限 == 下限:
			return 图片.copy()
		返回图片 = 图片.astype(numpy.float32)
		返回图片[同图灰度图 < 下限] = 下限
		返回图片[同图灰度图 > 上限] = 上限
		返回图片 = numpy.uint8(numpy.clip(255 * (返回图片 - 下限) / (上限 - 下限), 0, 255))
		return 返回图片
	return 增强函数

def 获取图像增强函数_区间蒙版(上限, 下限):
	def 增强函数(图片:numpy.ndarray, 同图灰度图: numpy.ndarray | None = None, 上限 = 上限, 下限 = 下限):
		if 同图灰度图 is None:
			同图灰度图 = cv2.cvtColor(图片, cv2.COLOR_BGR2GRAY)
		if 同图灰度图.ndim == 2:
			同图灰度图 = cv2.merge([同图灰度图, 同图灰度图, 同图灰度图])
		返回图片 = 图片.copy()
		if 上限 < 下限:
			上限, 下限 = 下限, 上限
		返回图片[同图灰度图 < 下限] = 0
		返回图片[同图灰度图 > 上限] = 0
		return 返回图片
	return 增强函数

def 获取图像增强函数_左右边界():
	def 增强函数(图片:numpy.ndarray, 同图灰度图: numpy.ndarray | None = None):
		返回图片 = cv2.filter2D(图片, ddepth=-1, kernel=numpy.array([[-1,0,1], [-1,0,1], [-1,0,1]]))
		return 返回图片
	return 增强函数

def 获取图像增强函数_上下边界():
	def 增强函数(图片:numpy.ndarray, 同图灰度图: numpy.ndarray | None = None):
		返回图片 = cv2.filter2D(图片, ddepth=-1, kernel=numpy.array([[-1,-1,-1], [0,0,0], [1,1,1]]))
		return 返回图片
	return 增强函数

def 获取图像增强函数_四向边界():
	def 增强函数(图片:numpy.ndarray, 同图灰度图: numpy.ndarray | None = None):
		返回图片 = cv2.filter2D(图片, ddepth=-1, kernel=numpy.array([[-1,-0.5,0], [-0.5,0,0.5], [0,0.5,1]]))
		return 返回图片
	return 增强函数


