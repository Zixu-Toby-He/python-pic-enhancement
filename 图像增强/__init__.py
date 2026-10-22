"""
图像增强模块
该模块每个函数均为 def f(原始图像: numpy.ndarray) -> numpy.ndarray:
输入一个 shape = (长,高,3) 的 numpy.ndarray 记录 bgr 数据，返回增强后的图像，形状与原来相同
"""
from __future__ import annotations

import copy
import inspect
import typing

import cv2
import numpy
import PyQt5.QtCore
import PyQt5.QtGui
import PyQt5.QtWidgets

from . import 工具函数


class _图像显示控件(PyQt5.QtWidgets.QLabel):
	def __init__(self, 母控件=None):
		super().__init__(母控件)
		self.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
		self.setMinimumSize(360, 280)
		self.setText("暂无效果图")
		self._原始图像 = None

	def 设置图像(self, 图像: numpy.ndarray):
		if 图像 is None or 图像.size == 0:
			self._原始图像 = None
			self.setPixmap(PyQt5.QtGui.QPixmap())
			self.setText("暂无效果图")
			return

		if 图像.ndim == 2:
			显示图像 = cv2.cvtColor(图像, cv2.COLOR_GRAY2RGB)
		else:
			显示图像 = cv2.cvtColor(图像, cv2.COLOR_BGR2RGB)
		显示图像 = numpy.ascontiguousarray(显示图像)
		高度, 宽度, 通道数 = 显示图像.shape
		每行字节数 = 通道数 * 宽度
		Q图像 = PyQt5.QtGui.QImage(
			显示图像.data,
			宽度,
			高度,
			每行字节数,
			PyQt5.QtGui.QImage.Format_RGB888,
		).copy()
		self._原始图像 = PyQt5.QtGui.QPixmap.fromImage(Q图像)
		self._刷新缩放图像()

	def resizeEvent(self, 事件):
		super().resizeEvent(事件)
		self._刷新缩放图像()

	def _刷新缩放图像(self):
		if self._原始图像 is None:
			return
		self.setPixmap(self._原始图像.scaled(
			self.size(),
			PyQt5.QtCore.Qt.KeepAspectRatio,
			PyQt5.QtCore.Qt.SmoothTransformation,
		))


class 增强工具:
	def __init__(self, 获取图像增强函数: typing.Callable):
		self.获取函数 = 获取图像增强函数
		self.工具名称 = 获取图像增强函数.__name__.removeprefix("获取图像增强函数_")
		self.函数签名 = inspect.signature(获取图像增强函数)
		self.参数名称 = tuple(self.函数签名.parameters.keys())
		self.函数数值 = {
			名称: 参数.default if 参数.default is not inspect.Parameter.empty else 0
			for 名称, 参数 in self.函数签名.parameters.items()
		}

	def 图像增强(self, 图片: numpy.ndarray):
		return self.获取函数(**self.函数数值)(图片)

	def 生成设定数值控件(self, 母控件=None, 变化回调: typing.Callable | None = None):
		"""
		每个变量
		---
		[变量名:label] ['=':lable] [数值:spinbox] [弹簧控件] [最小允许值:spinbox] [slider] [最大允许值:spinbox]
		---
		最小允许值初始默认为 0
		最大允许值初始默认为 255
		"""
		容器 = PyQt5.QtWidgets.QWidget(母控件)
		布局 = PyQt5.QtWidgets.QGridLayout(容器)
		布局.setContentsMargins(4, 4, 4, 4)

		if not self.参数名称:
			布局.addWidget(PyQt5.QtWidgets.QLabel("该工具没有可调参数", 容器), 0, 0)
			return 容器

		for 行号, 名称 in enumerate(self.参数名称):
			当前数值 = int(self.函数数值[名称])
			最小值 = min(0, 当前数值)
			最大值 = max(255, 当前数值)

			名称标签 = PyQt5.QtWidgets.QLabel(名称, 容器)
			等号标签 = PyQt5.QtWidgets.QLabel("=", 容器)
			数值框 = PyQt5.QtWidgets.QSpinBox(容器)
			下限框 = PyQt5.QtWidgets.QSpinBox(容器)
			滑块 = PyQt5.QtWidgets.QSlider(PyQt5.QtCore.Qt.Horizontal, 容器)
			上限框 = PyQt5.QtWidgets.QSpinBox(容器)

			for 数值控件 in (数值框, 下限框, 上限框):
				数值控件.setRange(-1_000_000, 1_000_000)
			下限框.setFixedWidth(50)
			上限框.setFixedWidth(50)
			数值框.setRange(最小值, 最大值)
			下限框.setValue(最小值)
			上限框.setValue(最大值)
			滑块.setRange(最小值, 最大值)
			数值框.setValue(当前数值)
			滑块.setValue(当前数值)

			数值框.valueChanged.connect(滑块.setValue)
			滑块.valueChanged.connect(数值框.setValue)

			def 更新数值(数值, 参数名称=名称):
				self.函数数值[参数名称] = 数值
				if 变化回调 is not None:
					变化回调()

			def 更新下限(数值, 当前数值框=数值框, 当前滑块=滑块, 当前上限框=上限框):
				if 数值 > 当前上限框.value():
					当前上限框.setValue(数值)
				当前数值框.setMinimum(数值)
				当前滑块.setMinimum(数值)

			def 更新上限(数值, 当前数值框=数值框, 当前滑块=滑块, 当前下限框=下限框):
				if 数值 < 当前下限框.value():
					当前下限框.setValue(数值)
				当前数值框.setMaximum(数值)
				当前滑块.setMaximum(数值)

			数值框.valueChanged.connect(更新数值)
			下限框.valueChanged.connect(更新下限)
			上限框.valueChanged.connect(更新上限)

			布局.addWidget(名称标签, 行号, 0)
			布局.addWidget(等号标签, 行号, 1)
			布局.addWidget(数值框,   行号, 2)
			布局.addWidget(下限框,   行号, 4)
			布局.addWidget(滑块,     行号, 5)
			布局.addWidget(上限框,   行号, 6)
			布局.setColumnStretch(3, 1)

		return 容器

	def 生成简介(self):
		"""
		"工具名称\n---\n变量1: 数值\n变量2: 数值\n...\n"
		最多显示两个变量，多退少补，用于增强管理器的简约按钮显示
		"""
		文本行 = [self.工具名称, "---"]
		文本行.extend(
			f"{名称}: {self.函数数值[名称]}"
			for 名称 in self.参数名称[:2]
		)
		return "\n".join(文本行)


class 增强管理器:
	def __init__(self, 图例):
		self.增强工具链: dict[str, 增强工具] = {}
		for 函数 in [
			工具函数.获取图像增强函数_线性拓展,
			工具函数.获取图像增强函数_四向边界,
			工具函数.获取图像增强函数_区间蒙版,
			工具函数.获取图像增强函数_左右边界,
			工具函数.获取图像增强函数_上下边界,
		]:
			工具 = 增强工具(函数)
			self.增强工具链[工具.工具名称] = 工具
		self.输出链路: list[增强工具] = []
		self.临时输出链路: list[增强工具] = []
		self.更换效果图例(图例)

	def 更换效果图例(self, 图例新图: numpy.ndarray):
		if not isinstance(图例新图, numpy.ndarray) or 图例新图.size == 0:
			raise ValueError("效果图例必须是非空的 numpy.ndarray")
		if 图例新图.ndim != 3 or 图例新图.shape[2] != 3:
			raise ValueError("效果图例必须是 BGR 三通道图像")
		self.图例原图 = 图例新图.copy()
		灰度 = cv2.cvtColor(图例新图, cv2.COLOR_BGR2GRAY)
		self.图例灰度 = cv2.merge([灰度, 灰度, 灰度])
		self.图例增强更新()

	def 设置参数(self):
		"""
		显示链路编辑器。链路纵向排列；工具参数变化时实时刷新效果图。
		确认后提交临时链路，取消则保留调用前的正式链路。
		---
		新界面
		---
		[[效果图显示:group] [分隔线] [链路滚动区:group]]
		[右下角按钮盒不变]
		---
		链路滚动区不再采用蛇形，整个 group 用 vbox 填充（需要有垂直滚动条）
		[输入]
		[下箭头:图案]
		[工具]
		[下箭头:图案]
		[工具]
		[下箭头:图案]
		...
		[输出]

		另：
		按钮点击逻辑不需要修改，但按钮字体大一号
		按钮文字与按钮上下边框需要有0.5字高的边距，横向长度固定15字宽
		"""
		self.同步链路("fork")
		窗口 = PyQt5.QtWidgets.QDialog()
		窗口.setWindowTitle("图像增强参数设置")
		窗口.resize(1180, 680)
		窗口布局 = PyQt5.QtWidgets.QVBoxLayout(窗口)

		主要区域 = PyQt5.QtWidgets.QGroupBox(窗口)
		主要布局 = PyQt5.QtWidgets.QHBoxLayout(主要区域)
		窗口布局.addWidget(主要区域, 1)

		效果图区域 = PyQt5.QtWidgets.QGroupBox("效果图", 主要区域)
		效果图区域.setObjectName("效果图区域")
		效果图布局 = PyQt5.QtWidgets.QVBoxLayout(效果图区域)
		效果图显示 = _图像显示控件(效果图区域)
		效果图布局.addWidget(效果图显示)
		主要布局.addWidget(效果图区域, 7)

		分隔线 = PyQt5.QtWidgets.QFrame(主要区域)
		分隔线.setFrameShape(PyQt5.QtWidgets.QFrame.VLine)
		分隔线.setFrameShadow(PyQt5.QtWidgets.QFrame.Sunken)
		主要布局.addWidget(分隔线)

		链路区域 = PyQt5.QtWidgets.QGroupBox("增强链路", 主要区域)
		链路区域.setObjectName("链路区域")
		链路区域布局 = PyQt5.QtWidgets.QVBoxLayout(链路区域)
		链路滚动区 = PyQt5.QtWidgets.QScrollArea(链路区域)
		链路滚动区.setObjectName("链路滚动区")
		链路滚动区.setWidgetResizable(True)
		链路滚动区.setHorizontalScrollBarPolicy(PyQt5.QtCore.Qt.ScrollBarAlwaysOff)
		链路滚动区.setVerticalScrollBarPolicy(PyQt5.QtCore.Qt.ScrollBarAsNeeded)
		链路容器 = PyQt5.QtWidgets.QWidget(链路滚动区)
		链路布局 = PyQt5.QtWidgets.QVBoxLayout(链路容器)
		链路布局.setAlignment(PyQt5.QtCore.Qt.AlignTop | PyQt5.QtCore.Qt.AlignHCenter)
		链路滚动区.setWidget(链路容器)
		链路区域布局.addWidget(链路滚动区)
		主要布局.addWidget(链路区域, 3)

		按钮盒 = PyQt5.QtWidgets.QDialogButtonBox(
			PyQt5.QtWidgets.QDialogButtonBox.Ok | PyQt5.QtWidgets.QDialogButtonBox.Cancel,
			PyQt5.QtCore.Qt.Horizontal,
			窗口,
		)
		按钮盒.button(PyQt5.QtWidgets.QDialogButtonBox.Ok).setText("确认")
		按钮盒.button(PyQt5.QtWidgets.QDialogButtonBox.Cancel).setText("取消")
		按钮盒.accepted.connect(窗口.accept)
		按钮盒.rejected.connect(窗口.reject)
		窗口布局.addWidget(按钮盒, 0, PyQt5.QtCore.Qt.AlignRight)

		展开位置: int | str | None = None

		def 清空链路布局():
			while 链路布局.count():
				布局项 = 链路布局.takeAt(0)
				控件 = 布局项.widget()
				if 控件 is not None:
					控件.deleteLater()

		def 设置链路按钮外观(按钮, 附加样式="", 字号增量=1, 尺寸比例=1.0):
			字体 = 按钮.font()
			if 字体.pointSize() > 0:
				字体.setPointSize(字体.pointSize() + 字号增量)
			else:
				字体.setPixelSize(字体.pixelSize() + 字号增量)
			按钮.setFont(字体)
			字体度量 = PyQt5.QtGui.QFontMetrics(字体)
			垂直留白 = max(1, 字体度量.height() // 2)
			按钮.setStyleSheet(f"QPushButton {{ padding: {垂直留白}px 0; {附加样式} }}")
			标准宽度 = 字体度量.horizontalAdvance("字" * 15) + 4
			按钮.setFixedWidth(标准宽度)
			if 尺寸比例 != 1.0:
				按钮.setFixedWidth(max(1, round(标准宽度 * 尺寸比例)))

		def 刷新效果图():
			try:
				self.图例增强更新()
				效果图显示.设置图像(self.图例增强)
				效果图显示.setToolTip("")
			except (cv2.error, TypeError, ValueError, ZeroDivisionError) as 异常:
				效果图显示.setPixmap(PyQt5.QtGui.QPixmap())
				效果图显示.setText(f"预览生成失败\n{异常}")
				效果图显示.setToolTip(str(异常))

		def 展开工具(索引):
			nonlocal 展开位置
			展开位置 = 索引
			刷新链路布局()

		def 收起工具():
			nonlocal 展开位置
			展开位置 = None
			刷新链路布局()

		def 删除工具(索引):
			nonlocal 展开位置
			self.临时输出链路.pop(索引)
			展开位置 = None
			刷新链路布局()
			刷新效果图()

		def 添加工具(工具名称):
			nonlocal 展开位置
			self.临时输出链路.append(copy.deepcopy(self.增强工具链[工具名称]))
			展开位置 = "输出"
			刷新链路布局()
			刷新效果图()

		def 生成展开工具控件(索引):
			工具 = self.临时输出链路[索引]
			控件 = PyQt5.QtWidgets.QGroupBox(工具.工具名称, 链路容器)
			布局 = PyQt5.QtWidgets.QVBoxLayout(控件)
			删除栏 = PyQt5.QtWidgets.QHBoxLayout()
			删除栏.addStretch(1)
			删除按钮 = PyQt5.QtWidgets.QPushButton("删除该工具", 控件)
			设置链路按钮外观(删除按钮, 尺寸比例=0.5)
			删除按钮.clicked.connect(lambda _=False, 当前索引=索引: 删除工具(当前索引))
			删除栏.addWidget(删除按钮)
			布局.addLayout(删除栏)
			布局.addWidget(工具.生成设定数值控件(控件, 刷新效果图))
			收起栏 = PyQt5.QtWidgets.QHBoxLayout()
			收起栏.addStretch(1)
			收起按钮 = PyQt5.QtWidgets.QPushButton("收起", 控件)
			设置链路按钮外观(收起按钮, 尺寸比例=0.5)
			收起按钮.clicked.connect(收起工具)
			收起栏.addWidget(收起按钮)
			布局.addLayout(收起栏)
			return 控件

		def 生成输出展开控件():
			控件 = PyQt5.QtWidgets.QGroupBox("添加优化工具", 链路容器)
			布局 = PyQt5.QtWidgets.QVBoxLayout(控件)
			for 工具名称 in self.增强工具链:
				按钮 = PyQt5.QtWidgets.QPushButton(工具名称, 控件)
				设置链路按钮外观(按钮)
				按钮.clicked.connect(lambda _=False, 名称=工具名称: 添加工具(名称))
				布局.addWidget(按钮)
			收起按钮 = PyQt5.QtWidgets.QPushButton("收起", 控件)
			设置链路按钮外观(收起按钮, 尺寸比例=0.5)
			收起按钮.clicked.connect(收起工具)
			布局.addWidget(收起按钮)
			return 控件

		def 刷新链路布局():
			清空链路布局()
			展开控件 = None

			输入按钮 = PyQt5.QtWidgets.QPushButton("输入", 链路容器)
			输入按钮.setObjectName("输入节点")
			输入按钮.setEnabled(False)
			设置链路按钮外观(输入按钮, "background: #c62828; color: white; font-weight: bold;", 2)
			链路布局.addWidget(输入按钮, 0, PyQt5.QtCore.Qt.AlignHCenter)

			for 索引, 工具 in enumerate(self.临时输出链路):
				箭头标签 = PyQt5.QtWidgets.QLabel("↓", 链路容器)
				箭头标签.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
				链路布局.addWidget(箭头标签, 0, PyQt5.QtCore.Qt.AlignHCenter)
				if 展开位置 == 索引:
					工具控件 = 生成展开工具控件(索引)
					展开控件 = 工具控件
					链路布局.addWidget(工具控件)
				else:
					工具控件 = PyQt5.QtWidgets.QPushButton(工具.生成简介(), 链路容器)
					设置链路按钮外观(工具控件)
					工具控件.clicked.connect(lambda _=False, 当前索引=索引: 展开工具(当前索引))
					链路布局.addWidget(工具控件, 0, PyQt5.QtCore.Qt.AlignHCenter)

			箭头标签 = PyQt5.QtWidgets.QLabel("↓", 链路容器)
			箭头标签.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
			链路布局.addWidget(箭头标签, 0, PyQt5.QtCore.Qt.AlignHCenter)
			if 展开位置 == "输出":
				输出控件 = 生成输出展开控件()
				展开控件 = 输出控件
				链路布局.addWidget(输出控件)
			else:
				输出控件 = PyQt5.QtWidgets.QPushButton("输出\n（添加优化工具）", 链路容器)
				输出控件.setObjectName("输出节点")
				设置链路按钮外观(输出控件, "background: #1565c0; color: white; font-weight: bold;", 2)
				输出控件.clicked.connect(lambda: 展开工具("输出"))
				链路布局.addWidget(输出控件, 0, PyQt5.QtCore.Qt.AlignHCenter)

			if 展开控件 is not None:
				def 滚动到展开控件(当前控件=展开控件):
					链路布局.activate()
					链路容器.adjustSize()
					链路滚动区.ensureWidgetVisible(当前控件, 10, 10)

				PyQt5.QtCore.QTimer.singleShot(
					0,
					滚动到展开控件,
				)

		刷新链路布局()
		刷新效果图()
		if 窗口.exec_() == PyQt5.QtWidgets.QDialog.Accepted:
			self.同步链路("merge")
		else:
			self.同步链路("fork")

	def 同步链路(self, mode: typing.Literal["fork", "merge"] = "merge"):
		"""
		fork  从正式输出链路创建互不联动的临时链路。
		merge 将临时链路提交为互不联动的正式输出链路。
		"""
		if mode == "fork":
			self.临时输出链路 = copy.deepcopy(self.输出链路)
		elif mode == "merge":
			self.输出链路 = copy.deepcopy(self.临时输出链路)
		else:
			raise ValueError(f"不支持的同步模式: {mode}")
		self.图例增强更新()

	def 图例增强更新(self):
		self.图例增强 = self.图例原图.copy()
		for 工具 in self.临时输出链路:
			self.图例增强 = 工具.图像增强(self.图例增强)

	def 图像增强(self, 图像):
		for 工具 in self.输出链路:
			图像 = 工具.图像增强(图像)
		return 图像
