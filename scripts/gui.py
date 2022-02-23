# -*- coding: utf-8 -*-

import os, sys, traceback
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from scripts.assist import format_conversion
from scripts.common import utils
from scripts.real_vehicle import note_vehicle_problems
from scripts.real_vehicle import filter_vehicle_problems
from scripts.sense import tm_replay_analyer
from scripts.simulation import filter_vehicle_scene


def singleton(cls, *args, **kwargs):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


class DropArea(QLabel):
    path_signal = pyqtSignal(str)

    def __init__(self, text):
        super(DropArea, self).__init__()
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setAutoFillBackground(True)
        pe = QPalette()
        pe.setColor(QPalette.WindowText, Qt.blue)
        pe.setColor(QPalette.Window, Qt.gray)
        self.setPalette(pe)
        self.setText(text)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        self.EditText(event.mimeData().urls()[0].toString())

    def EditText(self, path):
        if 0 == path.find('file:///'):
            path = path.replace('file:///', '/')
        self.setText(path)
        self.path_signal.emit(path)


class TemplateWindows(QWidget):

    def __init__(self):
        super(TemplateWindows, self).__init__()
        # 初始化UI界面
        self.init_ui()
        # 初始化控件
        self.init_element()
        # 初始化槽函数
        self.init_controller()
        # 初始化布局
        self.init_layout()

    def init_ui(self):
        pass

    def init_element(self):
        pass

    def init_controller(self):
        pass

    def init_layout(self):
        pass


'''感知测试类功能'''


# 常用KPI指标获取
class KPIWindows(TemplateWindows):
    def __init__(self):
        TemplateWindows.__init__(self)

    def init_ui(self):
        pass
        self.setStyleSheet("background-color:grey;")

    def init_element(self):
        self.btn_analy_kpi = QPushButton('开始处理数据')
        self.sense_label = DropArea('拖入感知结果')
        self.label_label = DropArea('拖入标注文件')

        self.sense_file_path = ''
        self.label_file_path = ''
        self.sense_files = None
        self.label_files = None

    def init_controller(self):
        self.btn_analy_kpi.clicked.connect(self.kpi_analy)
        self.sense_label.path_signal.connect(self.sense_callback)
        self.label_label.path_signal.connect(self.label_callback)
        self.cb = {}
        for key, value in utils.FUNCTION_SET.items():
            if value[1] == 'KPI':
                btn = QCheckBox(key, self)
                self.cb[key] = btn

    def init_layout(self):
        # 局部水平布局
        h_box = QHBoxLayout()
        h_box.addWidget(self.sense_label)
        h_box.addWidget(self.label_label)

        # 局部网络布局
        g_box = QGridLayout()
        positions = [(i, j) for i in range(8) for j in range(3)]
        for func, position in zip(self.cb.values(), positions):
            g_box.addWidget(func, *position)

        # 全局垂直布局
        global_box = QVBoxLayout()
        global_box.addLayout(h_box)
        global_box.addLayout(g_box)
        global_box.addWidget(self.btn_analy_kpi)

        self.setLayout(global_box)

    def sense_callback(self, path):
        self.sense_files = utils.get_all_files(path, '.json')

        if self.sense_files:
            self.sense_file_path = path

        else:
            self.sense_label.setText('拖入感知结果')
            print('No json in path!')

    def label_callback(self, path):
        self.label_files = utils.get_all_files(path, '.json')

        if self.label_files:
            self.label_file_path = path

        else:
            self.label_label.setText('拖入标注文件')
            print('No json in path!')

    def kpi_analy(self):
        if not self.sense_files:
            return

        func_list = []
        for key, value in self.cb.items():
            if value.isChecked():
                func_list.append(utils.FUNCTION_SET[key][0])
        if func_list:
            tm_replay_analyer.get_replay_result(self.label_files, self.sense_files, func_list)


# 无label筛选感知问题
class SenseFilterWindows(TemplateWindows):
    def __init__(self):
        TemplateWindows.__init__(self)

    def init_ui(self):
        self.setStyleSheet("background-color:grey;")

    def init_element(self):
        self.btn_analy_kpi = QPushButton('开始处理数据')
        self.sense_label = DropArea('拖入感知结果')

        self.sense_file_path = ''
        self.label_file_path = ''
        self.sense_files = None
        self.label_files = None

    def init_controller(self):
        self.btn_analy_kpi.clicked.connect(self.kpi_analy)
        self.sense_label.path_signal.connect(self.sense_callback)
        self.cb = {}
        for key, value in utils.FUNCTION_SET.items():
            if value[1] == 'SenseFilter':
                btn = QCheckBox(key, self)
                self.cb[key] = btn

    def init_layout(self):
        # 局部水平布局
        h_box = QHBoxLayout()
        h_box.addWidget(self.sense_label)

        # 局部网络布局
        g_box = QGridLayout()
        positions = [(i, j) for i in range(8) for j in range(3)]
        for func, position in zip(self.cb.values(), positions):
            g_box.addWidget(func, *position)

        # 全局垂直布局
        global_box = QVBoxLayout()
        global_box.addLayout(h_box)
        global_box.addLayout(g_box)
        global_box.addWidget(self.btn_analy_kpi)

        self.setLayout(global_box)

    def sense_callback(self, path):
        self.sense_files = utils.get_all_files(path, '.json')

        if self.sense_files:
            self.sense_file_path = path

        else:
            self.sense_label.setText('拖入感知结果')
            print('No json in path!')


    def kpi_analy(self):
        if not self.sense_files:
            return

        func_list = []
        for key, value in self.cb.items():
            if value.isChecked():
                func_list.append(utils.FUNCTION_SET[key][0])
        if func_list:
            tm_replay_analyer.get_replay_result(None, self.sense_files, func_list)


# 其它指标获取
class OtherKPIWindows(TemplateWindows):
    def __init__(self):
        TemplateWindows.__init__(self)

    def init_ui(self):
        self.setStyleSheet("background-color:grey;")

    def init_element(self):
        self.btn_analy_kpi = QPushButton('开始处理数据')
        self.sense_label = DropArea('拖入感知结果')
        self.label_label = DropArea('拖入标注文件')

        self.sense_file_path = ''
        self.label_file_path = ''
        self.sense_files = None
        self.label_files = None

    def init_controller(self):
        self.btn_analy_kpi.clicked.connect(self.kpi_analy)
        self.sense_label.path_signal.connect(self.sense_callback)
        self.label_label.path_signal.connect(self.label_callback)
        self.cb = {}
        for key, value in utils.FUNCTION_SET.items():
            if value[1] == 'OtherKPI':
                btn = QCheckBox(key, self)
                self.cb[key] = btn

    def init_layout(self):
        # 局部水平布局
        h_box = QHBoxLayout()
        h_box.addWidget(self.sense_label)
        h_box.addWidget(self.label_label)

        # 局部网络布局
        g_box = QGridLayout()
        positions = [(i, j) for i in range(8) for j in range(3)]
        for func, position in zip(self.cb.values(), positions):
            g_box.addWidget(func, *position)

        # 全局垂直布局
        global_box = QVBoxLayout()
        global_box.addLayout(h_box)
        global_box.addLayout(g_box)
        global_box.addWidget(self.btn_analy_kpi)

        self.setLayout(global_box)

    def sense_callback(self, path):
        self.sense_files = utils.get_all_files(path, '.json')

        if self.sense_files:
            self.sense_file_path = path

        else:
            self.sense_label.setText('拖入感知结果')
            print('No json in path!')

    def label_callback(self, path):
        self.label_files = utils.get_all_files(path, '.json')

        if self.label_files:
            self.label_file_path = path

        else:
            self.label_label.setText('拖入标注文件')
            print('No json in path!')

    def kpi_analy(self):
        if not self.sense_files:
            return

        func_list = []
        for key, value in self.cb.items():
            if value.isChecked():
                func_list.append(utils.FUNCTION_SET[key][0])
        if func_list:
            tm_replay_analyer.get_replay_result(self.label_files, self.sense_files, func_list)


# 问题数据绘图
class DrawWindows(TemplateWindows):
    def __init__(self):
        TemplateWindows.__init__(self)

    def init_ui(self):
        self.setStyleSheet("background-color:grey;")

    def init_element(self):
        self.btn_analy_kpi = QPushButton('开始处理数据')
        self.sense_label = DropArea('拖入原始图片')
        self.label_label = DropArea('拖入json文件')

        self.sense_file_path = ''
        self.label_file_path = ''
        self.sense_files = None
        self.label_files = None

    def init_controller(self):
        self.btn_analy_kpi.clicked.connect(self.kpi_analy)
        self.sense_label.path_signal.connect(self.sense_callback)
        self.label_label.path_signal.connect(self.label_callback)
        self.cb = {}
        for key, value in utils.FUNCTION_SET.items():
            if value[1] == 'Draw':
                btn = QCheckBox(key, self)
                self.cb[key] = btn

    def init_layout(self):
        # 局部水平布局
        h_box = QHBoxLayout()
        h_box.addWidget(self.sense_label)
        h_box.addWidget(self.label_label)

        # 局部网络布局
        g_box = QGridLayout()
        positions = [(i, j) for i in range(8) for j in range(3)]
        for func, position in zip(self.cb.values(), positions):
            g_box.addWidget(func, *position)

        # 全局垂直布局
        global_box = QVBoxLayout()
        global_box.addLayout(h_box)
        global_box.addLayout(g_box)
        global_box.addWidget(self.btn_analy_kpi)

        self.setLayout(global_box)

    def sense_callback(self, path):
        self.sense_files = utils.get_all_files(path, '.BMP')

        if self.sense_files:
            self.sense_file_path = path

        else:
            self.sense_label.setText('拖入原始图片')
            print('No json in path!')

    def label_callback(self, path):
        self.label_files = utils.get_all_files(path, '.json')

        if self.label_files:
            self.label_file_path = path

        else:
            self.label_label.setText('拖入json文件')
            print('No json in path!')

    def kpi_analy(self):
        if not self.sense_files:
            return

        func_list = []
        for key, value in self.cb.items():
            if value.isChecked():
                func_list.append(utils.FUNCTION_SET[key][0])
        if func_list:
            tm_replay_analyer.get_replay_result(self.label_files, self.sense_files, func_list)


'''仿真测试类功能'''


@singleton
class FilterSceneWindows(TemplateWindows):
    def __init__(self):
        TemplateWindows.__init__(self)

    def init_ui(self):
        self.setWindowTitle('实车场景筛选')
        self.setGeometry(600, 400, 480, 240)

    def init_element(self):
        self.filter_problem = QPushButton('开始处理数据')
        self.btn_back = QPushButton('返回主页')
        self.file_label = DropArea('拖入数据目录')
        self.cb = {}
        for key, value in utils.FUNCTION_SET.items():
            if value[1] == 'simulation':
                btn = QCheckBox(key, self)
                self.cb[key] = btn

    def init_controller(self):
        self.filter_problem.clicked.connect(self.filter_vehicle_scene)
        self.btn_back.clicked.connect(self.slot_show_main)
        self.file_label.path_signal.connect(self.file_callback)

    def init_layout(self):
        # 局部网络布局
        g_box = QGridLayout()
        positions = [(i, j) for i in range(8) for j in range(3)]
        for temp, position in zip(self.cb.values(), positions):
            g_box.addWidget(temp, *position)

        # 全局垂直布局
        v_box = QVBoxLayout()
        v_box.addWidget(self.file_label)
        v_box.addLayout(g_box)
        v_box.addWidget(self.filter_problem)
        v_box.addWidget(self.btn_back)

        self.setLayout(v_box)

    def file_callback(self, path):
        self.timestamp_log_files = utils.get_all_files(path, '.log')
        self.rosbag_files = utils.get_all_files(path, '.bag')
        if self.timestamp_log_files or self.rosbag_files:
            self.file_path = path
            return
        self.file_label.setText('拖入数据目录')
        print('No rosbag and log in path!')

    def filter_vehicle_scene(self):
        if os.path.isdir(self.file_path):
            func_list = []
            for key, value in self.cb.items():
                if value.isChecked():
                    func_list.append(utils.FUNCTION_SET[key][0])
            if func_list:
                filter_vehicle_scene.get_vehicle_scene(self.file_path, func_list)

    def slot_show_main(self):
        self.hide()
        self.mainwindows = MainWindows()
        self.mainwindows.show()


'''实车测试类功能'''


# 实车问题记录界面
@singleton
class RecordProblemWindows(TemplateWindows):
    def __init__(self):
        TemplateWindows.__init__(self)

    def init_ui(self):
        self.setWindowTitle('实车测试问题记录')
        self.setGeometry(600, 400, 900, 400)

    def init_element(self):
        self.btn_back = QPushButton('返回主页', self)
        self.btn_flush = QPushButton('更新记录')
        self._problem_list = QTableWidget()
        self.init_problem_list_module()
        self.problems_type = ['跑偏', '重刹', 'cutin不减速', '变道超调', '跟车不刹车', '新增问题']
        self.row_dict = {}

        # 添加测试信息
        self.line_tester = QLineEdit(self)
        self.line_vehicel = QLineEdit(self)
        self.line_driving_version = QLineEdit(self)
        self.line_weather = QLineEdit(self)
        self.line_road_level = QLineEdit(self)
        self.line_func = QLineEdit(self)

    def init_controller(self):
        self.btn_back.clicked.connect(self.slot_show_main)
        self.btn_flush.clicked.connect(self.flush_problem_describe)

    def init_layout(self):
        # 局部网络布局
        grid = QGridLayout()
        grid.addWidget(QLabel('测试人'), 1, 1, 1, 1), grid.addWidget(self.line_tester, 1, 2, 1, 1)
        grid.addWidget(QLabel('车辆'), 1, 3, 1, 1), grid.addWidget(self.line_vehicel, 1, 4, 1, 1)
        grid.addWidget(QLabel('整包版本'), 1, 5, 1, 1), grid.addWidget(self.line_driving_version, 1, 6, 1, 1)
        grid.addWidget(QLabel('天气'), 1, 7, 1, 1), grid.addWidget(self.line_weather, 1, 8, 1, 1)
        grid.addWidget(QLabel('道路类型'), 1, 9, 1, 1), grid.addWidget(self.line_road_level, 1, 10, 1, 1)
        grid.addWidget(QLabel('功能大类'), 1, 11, 1, 1), grid.addWidget(self.line_func, 1, 12, 1, 1)

        # 局部网络布局
        g_box = QGridLayout()
        g_box.SizeConstraint()
        positions = [(i, j) for i in range(8) for j in range(3)]
        for name, position in zip(self.problems_type, positions):
            btn = QPushButton(name, self)
            btn.clicked.connect(note_vehicle_problems.problem_record(name))
            btn.clicked.connect(self.append_problem_line)
            g_box.addWidget(btn, *position)

        # 局部垂直布局
        v_box = QVBoxLayout()
        v_box.addWidget(self._problem_list)
        v_box.addWidget(self.btn_flush)

        # 嵌套全局水平布局
        h_box = QHBoxLayout()
        h_box.addLayout(g_box, 1)
        h_box.addLayout(v_box, 2)

        # 全局垂直布局
        global_box = QVBoxLayout()
        global_box.addLayout(grid)
        global_box.addLayout(h_box)
        global_box.addWidget(self.btn_back)

        self.setLayout(global_box)

    def get_combox_text(self):
        combox_result = []
        combox_result.append(self.line_tester.text())
        combox_result.append(self.line_vehicel.text())
        combox_result.append(self.line_driving_version.text())
        combox_result.append(self.line_weather.text())
        combox_result.append(self.line_road_level.text())
        combox_result.append(self.line_func.text())
        return combox_result

    def init_problem_list_module(self):
        """
        初始化问题处理列表
        """
        self._problem_list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self._problem_list.horizontalHeader().setStretchLastSection(True)
        self._problem_list.setSelectionMode(QAbstractItemView.NoSelection)
        self._problem_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._problem_list.setColumnCount(5)
        self._problem_list.setHorizontalHeaderLabels(['NO', 'Date', 'Time', 'Problem', 'Describe'])

    def append_problem_line(self):
        """
        界面右侧增加当前问题行
        """
        row_count = self._problem_list.rowCount()
        self._problem_list.setRowCount(row_count + 1)
        df = note_vehicle_problems.get_all_problems()
        row = df.shape[0] - 1
        self.row_dict[str(row_count)] = row
        self._problem_list.setItem(row_count, 0, QTableWidgetItem(str(df.iloc[row, 0])))
        self._problem_list.setItem(row_count, 1, QTableWidgetItem(df.iloc[row, 1]))
        self._problem_list.setItem(row_count, 2, QTableWidgetItem(df.iloc[row, 2]))
        self._problem_list.setItem(row_count, 3, QTableWidgetItem(df.iloc[row, 3]))
        self._problem_list.setCellWidget(row_count, 4, QLineEdit())
        self.flush_problem_describe()

    def flush_problem_describe(self):
        df = note_vehicle_problems.get_all_problems()
        for row_count in range(self._problem_list.rowCount()):
            df.iloc[self.row_dict[str(row_count)], 4] = self._problem_list.cellWidget(row_count, 4).text()
        df.iloc[df.shape[0] - 1, [5, 6, 9, 12, 13, 15]] = self.get_combox_text()
        df.to_excel(note_vehicle_problems.FILE_NAME, index=False, engine='openpyxl')

    def slot_show_main(self):
        self.hide()
        self.mainwindows = MainWindows()
        self.mainwindows.show()


# 实车问题筛选界面
@singleton
class FilterProblemWindows(TemplateWindows):
    def __init__(self):
        TemplateWindows.__init__(self)

    def init_ui(self):
        self.setWindowTitle('实车问题筛选')
        self.setGeometry(600, 400, 480, 240)

    def init_element(self):
        self.filter_problem = QPushButton('开始处理数据')
        self.btn_back = QPushButton('返回主页')
        self.file_label = DropArea('拖入数据目录')
        self.cb = {}
        for key, value in utils.FUNCTION_SET.items():
            if value[1] == 'vehicle':
                btn = QCheckBox(key, self)
                self.cb[key] = btn

    def init_controller(self):
        self.filter_problem.clicked.connect(self.filter_vehicle_problem)
        self.btn_back.clicked.connect(self.slot_show_main)
        self.file_label.path_signal.connect(self.file_callback)

    def init_layout(self):
        # 局部网络布局
        g_box = QGridLayout()
        positions = [(i, j) for i in range(8) for j in range(3)]
        for temp, position in zip(self.cb.values(), positions):
            g_box.addWidget(temp, *position)

        # 全局垂直布局
        v_box = QVBoxLayout()
        v_box.addWidget(self.file_label)
        v_box.addLayout(g_box)
        v_box.addWidget(self.filter_problem)
        v_box.addWidget(self.btn_back)

        self.setLayout(v_box)

    def file_callback(self, path):
        self.timestamp_log_files = utils.get_all_files(path, '.log')
        self.rosbag_files = utils.get_all_files(path, '.bag')
        if self.timestamp_log_files or self.rosbag_files:
            self.file_path = path
            return
        self.file_label.setText('拖入数据目录')
        print('No rosbag and log in path!')

    def filter_vehicle_problem(self):
        if os.path.isdir(self.file_path):
            func_list = []
            for key, value in self.cb.items():
                if value.isChecked():
                    func_list.append(utils.FUNCTION_SET[key][0])
            if func_list:
                filter_vehicle_problems.get_vehicle_problem(self.file_path, func_list)

    def slot_show_main(self):
        self.hide()
        self.mainwindows = MainWindows()
        self.mainwindows.show()


# 问题数据切片界面
@singleton
class ExtractDataWindows(TemplateWindows):
    def __init__(self):
        TemplateWindows.__init__(self)

    def init_ui(self):
        self.setWindowTitle('问题数据切片')
        self.setGeometry(600, 400, 480, 360)

    def init_element(self):
        self.btn_back = QPushButton('返回主页', self)
        self.btn_extract = QPushButton('数据分拣', self)
        self.excel_label = DropArea('拖入问题记录表')
        self.file_label = DropArea('拖入数据目录')

        self.excel_path = ''
        self.file_path = ''

    def init_controller(self):
        self.btn_back.clicked.connect(self.slot_show_main)
        self.btn_extract.clicked.connect(self.extract_problem)
        self.excel_label.path_signal.connect(self.excel_callback)
        self.file_label.path_signal.connect(self.file_callback)

    def init_layout(self):
        # 全局垂直布局
        vbox = QVBoxLayout()
        vbox.addWidget(self.excel_label)
        vbox.addWidget(self.file_label)
        vbox.addWidget(self.btn_extract)
        vbox.addWidget(self.btn_back)
        self.setLayout(vbox)

    def excel_callback(self, path):
        if str(path).endswith('xlsx'):
            self.excel_path = path
            return
        self.excel_label.setText('拖入问题记录表')
        print('Not excel file!')

    def file_callback(self, path):
        self.timestamp_log_files = utils.get_all_files(path, '.log')
        self.rosbag_files = utils.get_all_files(path, '.bag')
        if self.timestamp_log_files or self.rosbag_files:
            self.file_path = path
            return
        self.file_label.setText('拖入数据目录')
        print('No rosbag and log in path!')

    def extract_problem(self):
        try:
            note_vehicle_problems.ExtractMoudle(self.file_path, self.excel_path)()
        except:
            utils.logger.info(traceback.format_exc())

    def slot_show_main(self):
        self.hide()
        self.mainwindows = MainWindows()
        self.mainwindows.show()


# 实车测试面板
class VehicleWindows(TemplateWindows):
    def __init__(self):
        TemplateWindows.__init__(self)

    def init_ui(self):
        self.setStyleSheet("background-color:blue;")

    def init_element(self):
        self.btn_problem_panel = QPushButton('实车问题记录')
        self.btn_filter_panel = QPushButton('实车问题筛选')
        self.btn_extract_panel = QPushButton('问题数据切片')

    def init_controller(self):
        self.btn_problem_panel.clicked.connect(self.slot_show_problem)
        self.btn_filter_panel.clicked.connect(self.slot_show_filter)
        self.btn_extract_panel.clicked.connect(self.slot_show_extract)
        pass

    def init_layout(self):
        vSpacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        # 局部网络布局
        g_box = QGridLayout()
        g_box.addWidget(self.btn_problem_panel)
        g_box.addWidget(self.btn_filter_panel)
        g_box.addWidget(self.btn_extract_panel)

        # 全局垂直布局
        global_box = QVBoxLayout()
        global_box.addLayout(g_box)
        global_box.addItem(vSpacer)

        self.setLayout(global_box)

    def slot_show_problem(self):
        self.mainwindows = MainWindows()
        self.mainwindows.hide()
        self.show_windows = RecordProblemWindows()
        self.show_windows.show()

    def slot_show_filter(self):
        self.mainwindows = MainWindows()
        self.mainwindows.hide()
        self.show_windows = FilterProblemWindows()
        self.show_windows.show()

    def slot_show_extract(self):
        self.mainwindows = MainWindows()
        self.mainwindows.hide()
        self.show_windows = ExtractDataWindows()
        self.show_windows.show()


# 仿真测试面板
class SimulationWindows(TemplateWindows):
    def __init__(self):
        TemplateWindows.__init__(self)

    def init_ui(self):
        self.setStyleSheet("background-color:blue;")

    def init_element(self):
        self.btn_scene_pannel = QPushButton('场景数据筛选')
        self.btn_case_pannel = QPushButton('仿真用例生成')
        self.btn_evaluate_pannel = QPushButton('仿真结果评测')

    def init_controller(self):
        self.btn_scene_pannel.clicked.connect(self.slot_show_filter)

    def init_layout(self):
        vSpacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)

        # 局部网络布局
        g_box = QGridLayout()
        g_box.addWidget(self.btn_scene_pannel)
        g_box.addWidget(self.btn_case_pannel)
        g_box.addWidget(self.btn_evaluate_pannel)

        # 全局垂直布局
        global_box = QVBoxLayout()
        global_box.addLayout(g_box)
        global_box.addItem(vSpacer)

        self.setLayout(global_box)

    def slot_show_filter(self):
        self.mainwindows = MainWindows()
        self.mainwindows.hide()
        self.show_windows = FilterSceneWindows()
        self.show_windows.show()


# 感知测试面板
class SenseWindows(TemplateWindows):
    def __init__(self):
        TemplateWindows.__init__(self)

    def init_ui(self):
        pass

    def init_element(self):
        self.btn_kpi_panel = QPushButton('KPI指标')
        self.btn_problem_panel = QPushButton('筛选问题')
        self.btn_other_panel = QPushButton('其它功能')
        self.btn_draw_panel = QPushButton('问题绘图')

        self.form1 = KPIWindows()
        self.form2 = SenseFilterWindows()
        self.form3 = OtherKPIWindows()
        self.form4 = DrawWindows()

    def init_controller(self):
        self.btn_kpi_panel.clicked.connect(self.btn_press1_clicked)
        self.btn_problem_panel.clicked.connect(self.btn_press2_clicked)
        self.btn_other_panel.clicked.connect(self.btn_press3_clicked)
        self.btn_draw_panel.clicked.connect(self.btn_press4_clicked)

    def init_layout(self):
        # 局部水平布局
        h_box = QHBoxLayout()
        h_box.addWidget(self.btn_kpi_panel)
        h_box.addWidget(self.btn_problem_panel)
        h_box.addWidget(self.btn_other_panel)
        h_box.addWidget(self.btn_draw_panel)

        # 局部堆叠布局
        widget = QWidget()
        self.stacked_layout = QStackedLayout()
        widget.setLayout(self.stacked_layout)

        self.stacked_layout.addWidget(self.form1)
        self.stacked_layout.addWidget(self.form2)
        self.stacked_layout.addWidget(self.form3)
        self.stacked_layout.addWidget(self.form4)

        # 全局垂直布局
        global_box = QVBoxLayout()
        global_box.addLayout(h_box)
        global_box.addWidget(widget)

        self.setLayout(global_box)

    def btn_press1_clicked(self):
        self.stacked_layout.setCurrentIndex(0)

    def btn_press2_clicked(self):
        self.stacked_layout.setCurrentIndex(1)

    def btn_press3_clicked(self):
        self.stacked_layout.setCurrentIndex(2)

    def btn_press4_clicked(self):
        self.stacked_layout.setCurrentIndex(3)


# 辅助功能面板
class AssistWindows(TemplateWindows):
    def __init__(self):
        TemplateWindows.__init__(self)

    def init_ui(self):
        self.setStyleSheet("background-color:grey;")

    def init_element(self):
        self.btn_img2avi = QPushButton('图片转视频', self)
        self.btn_png2yuv = QPushButton('PNG图片转YUV', self)
        self.btn_png2bmp = QPushButton('PNG图片转BMP', self)
        self.btn_transform_3d = QPushButton('transform_3d', self)

        self.file_label = DropArea('拖入原始数据目录')
        self.result_label = DropArea('拖入目标存储目录')
        self.file_path = ''
        self.save_file_path = ''

    def init_controller(self):
        self.btn_img2avi.clicked.connect(self.img_conversed_video)
        self.btn_png2yuv.clicked.connect(self.png_conversed_yuv)
        self.btn_png2bmp.clicked.connect(self.png_conversed_bmp)
        self.btn_transform_3d.clicked.connect(self.trans_3d)
        self.file_label.path_signal.connect(self.file_callback)
        self.result_label.path_signal.connect(self.save_path_callback)

    def init_layout(self):
        # vSpacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)

        # 局部网络布局
        g_box = QGridLayout()
        g_box.addWidget(self.btn_img2avi, 0, 0)
        g_box.addWidget(self.btn_png2yuv, 0, 1)
        g_box.addWidget(self.btn_png2bmp, 0, 2)
        g_box.addWidget(self.btn_transform_3d, 1, 0)

        # 局部水平布局
        h_box = QHBoxLayout()
        h_box.addWidget(self.file_label)
        h_box.addWidget(self.result_label)

        # 全局垂直布局
        global_box = QVBoxLayout()
        global_box.addLayout(h_box)
        global_box.addLayout(g_box)
        # global_box.addItem(vSpacer)

        self.setLayout(global_box)

    def file_callback(self, path):
        if os.path.exists(path):
            self.file_path = path
        else:
            self.file_label.setText('拖原始数据目录')
            print('目录不存在')

    def save_path_callback(self, path):
        if os.path.isdir(path):
            self.save_file_path = path
        else:
            self.file_label.setText('拖入目标存储目录')
            print('目录不存在')

    def img_conversed_video(self):
        if os.path.isdir(self.file_path):
            format_conversion.img_to_video(self.file_path, '.bmp', self.save_file_path)
            format_conversion.img_to_video(self.file_path, '.png', self.save_file_path)

    def png_conversed_bmp(self):
        if self.file_path:
            format_conversion.png_to_bmp(self.file_path, self.save_file_path)

    def png_conversed_yuv(self):
        if self.file_path:
            format_conversion.png_to_yuv(self.file_path, self.save_file_path)

    def trans_3d(self):
        if self.file_path:
            format_conversion.transform_3d(self.file_path, self.save_file_path)

    # def label_split_more(self):
    #     if not self.file_path:
    #         return
    #     tm_format_conversion.split_label_file(self.file_path, self.save_file_path)


# process main windows
@singleton
class MainWindows(TemplateWindows):
    def __init__(self):
        TemplateWindows.__init__(self)

    def init_ui(self):
        self.setWindowTitle('欢迎使用纽劢测试工具')
        self.setGeometry(600, 400, 640, 360)

    def init_element(self):
        self.btn_first_panel = QPushButton('实车测试')
        self.btn_second_panel = QPushButton('仿真测试')
        self.btn_third_panel = QPushButton('感知测试')
        self.btn_fourth_panel = QPushButton('辅助功能')

        self.form1 = VehicleWindows()
        self.form2 = SimulationWindows()
        self.form3 = SenseWindows()
        # self.form3 = KPIWindows()
        self.form4 = AssistWindows()

    def init_controller(self):
        self.btn_first_panel.clicked.connect(self.btn_press1_clicked)
        self.btn_second_panel.clicked.connect(self.btn_press2_clicked)
        self.btn_third_panel.clicked.connect(self.btn_press3_clicked)
        self.btn_fourth_panel.clicked.connect(self.btn_press4_clicked)

    def init_layout(self):
        vSpacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        # 左侧局部垂直布局
        v_box1 = QVBoxLayout()
        v_box1.addWidget(self.btn_first_panel)
        v_box1.addWidget(self.btn_second_panel)
        v_box1.addWidget(self.btn_third_panel)
        v_box1.addWidget(self.btn_fourth_panel)
        v_box1.addItem(vSpacer)
        # v_box1.addStretch(1)

        # 右侧局部堆叠布局
        widget = QWidget()
        self.stacked_layout = QStackedLayout()
        widget.setLayout(self.stacked_layout)
        widget.setStyleSheet("background-color:white;")

        self.stacked_layout.addWidget(self.form1)
        self.stacked_layout.addWidget(self.form2)
        self.stacked_layout.addWidget(self.form3)
        self.stacked_layout.addWidget(self.form4)

        # 全局水平布局
        global_box = QHBoxLayout()
        global_box.addLayout(v_box1)
        global_box.addWidget(widget)

        self.setLayout(global_box)

    def btn_press1_clicked(self):
        self.stacked_layout.setCurrentIndex(0)

    def btn_press2_clicked(self):
        self.stacked_layout.setCurrentIndex(1)

    def btn_press3_clicked(self):
        self.stacked_layout.setCurrentIndex(2)

    def btn_press4_clicked(self):
        self.stacked_layout.setCurrentIndex(3)


def main():
    app = QApplication(sys.argv)
    Main = MainWindows()
    Main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
