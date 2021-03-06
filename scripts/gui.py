# -*- coding: utf-8 -*-
import itertools
import json
import os, sys, traceback
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from allpairspy import AllPairs
import pandas as pd

from scripts.common.utils import logger

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.assist import format_conversion
from scripts.real_vehicle import note_vehicle_problems
from scripts.real_vehicle import filter_vehicle_scene
from scripts.sense import tm_replay_analyer
from scripts.common import utils
from collections import OrderedDict


def singleton(cls):
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
        # 美化界面
        self.init_qss()

    def init_ui(self):
        pass

    def init_element(self):
        pass

    def init_controller(self):
        pass

    def init_layout(self):
        pass

    def init_qss(self):
        pass


'''感知测试类功能'''


# 常用KPI指标获取
class KPIWindows(TemplateWindows):
    def __init__(self):
        TemplateWindows.__init__(self)

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
        self.cb = OrderedDict()
        for key, value in utils.FUNCTION_SET.items():
            if value[1] == 'KPI':
                self.cb[key] = QCheckBox(key, self)

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

    def init_qss(self):
        self.btn_analy_kpi.setStyleSheet(
            '''QPushButton{background:#CCFFFF;border-radius:5px;}QPushButton:hover{background:green;}''')

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
        self.cb = OrderedDict()
        for key, value in utils.FUNCTION_SET.items():
            if value[1] == 'SenseFilter':
                self.cb[key] = QCheckBox(key, self)

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

    def init_qss(self):
        self.btn_analy_kpi.setStyleSheet(
            '''QPushButton{background:#CCFFFF;border-radius:5px;}QPushButton:hover{background:green;}''')

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
        self.cb = OrderedDict()
        for key, value in utils.FUNCTION_SET.items():
            if value[1] == 'OtherKPI':
                self.cb[key] = QCheckBox(key, self)

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

    def init_qss(self):
        self.btn_analy_kpi.setStyleSheet(
            '''QPushButton{background:#CCFFFF;border-radius:5px;}QPushButton:hover{background:green;}''')

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
        self.cb = OrderedDict()
        for key, value in utils.FUNCTION_SET.items():
            if value[1] == 'Draw':
                self.cb[key] = QCheckBox(key, self)

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

    def init_qss(self):
        self.btn_analy_kpi.setStyleSheet(
            '''QPushButton{background:#CCFFFF;border-radius:5px;}QPushButton:hover{background:green;}''')

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


# 仿真用例生成
@singleton
class TestCaseWindows(TemplateWindows):
    def __init__(self):
        TemplateWindows.__init__(self)

    def init_ui(self):
        self.setWindowTitle('测试用例生成')
        self.setGeometry(600, 400, 1080, 720)

    def init_element(self):
        self.btn_back = QPushButton('返回主页')
        self.btn_adas_panel = QPushButton('ADAS功能场景')
        self.btn_ad_panel = QPushButton("AD场景泛化")
        self.btn_scene_panel = QPushButton('七层场景泛化')

        self.form1 = CaseAdasWindows()
        self.form2 = CaseAdWindows()
        self.form3 = CaseSceneWindows()

    def init_controller(self):
        self.btn_back.clicked.connect(self.slot_show_main)
        self.btn_adas_panel.clicked.connect(self.btn_press1_clicked)
        self.btn_ad_panel.clicked.connect(self.btn_press2_clicked)
        self.btn_scene_panel.clicked.connect(self.btn_press3_clicked)

    def init_layout(self):
        # 局部水平布局
        h_box = QHBoxLayout()
        h_box.addWidget(self.btn_adas_panel)
        h_box.addWidget(self.btn_ad_panel)
        h_box.addWidget(self.btn_scene_panel)

        # 局部堆叠布局
        widget = QWidget()
        self.stacked_layout = QStackedLayout()
        widget.setLayout(self.stacked_layout)

        self.stacked_layout.addWidget(self.form1)
        self.stacked_layout.addWidget(self.form2)
        self.stacked_layout.addWidget(self.form3)

        # 全局垂直布局
        global_box = QVBoxLayout()
        global_box.addLayout(h_box)
        global_box.addWidget(widget)
        global_box.addWidget(self.btn_back)

        self.setLayout(global_box)

    def init_qss(self):
        self.btn_adas_panel.setStyleSheet("background-color:#0099FF;")
        self.btn_ad_panel.setStyleSheet("background-color:#FFFFCC;")
        self.btn_scene_panel.setStyleSheet("background-color:#666699;")

    def btn_press1_clicked(self):
        self.stacked_layout.setCurrentIndex(0)

    def btn_press2_clicked(self):
        self.stacked_layout.setCurrentIndex(1)

    def btn_press3_clicked(self):
        self.stacked_layout.setCurrentIndex(2)

    def slot_show_main(self):
        self.hide()
        self.mainwindows = MainWindows()
        self.mainwindows.show()


# ADAS功能测试用例
class CaseAdasWindows(TemplateWindows):
    def __init__(self):
        TemplateWindows.__init__(self)

    def init_ui(self):
        self.setGeometry(600, 400, 1080, 720)

    def init_element(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'simulation/cfgs/adas_case_config.json')
        self.scene_case = utils.get_json_data(path)
        self.assembly = OrderedDict()
        # 全局垂直布局
        global_box = QVBoxLayout()
        positions = [(i, j) for i in range(8) for j in range(1, 5)]

        for classify in self.scene_case.keys():
            g_box = QGridLayout()
            global_box.addLayout(g_box)
            self.assembly[classify] = (QLabel(classify), QCheckBox('全选'))
            g_box.addWidget(self.assembly[classify][0], 0, 0, -1, 1)
            g_box.addWidget(self.assembly[classify][1], 1, 0, -1, 1)
            self.assembly[classify][0].setStyleSheet("background-color:#CCCCCC;")
            self.assembly[classify][1].stateChanged.connect(self.change_cb1(classify))
            for terms, position in zip(self.scene_case[classify], positions):
                self.assembly[terms] = QCheckBox(terms)
                g_box.addWidget(self.assembly[terms], *position)
                self.assembly[terms].stateChanged.connect(self.change_cb2(classify))
        global_box.addStretch(1)
        self.setLayout(global_box)

    def change_cb1(self, classify):
        def wrapper():
            if self.assembly[classify][1].checkState() == Qt.Checked:
                for terms in self.scene_case[classify]:
                    self.assembly[terms].setCheckState(Qt.Checked)
            elif self.assembly[classify][1].checkState() == Qt.Unchecked:
                for terms in self.scene_case[classify]:
                    self.assembly[terms].setCheckState(Qt.Unchecked)

        return wrapper

    def change_cb2(self, classify):
        def wrapper():
            i = 0
            sum = len(self.scene_case[classify])
            for terms in self.scene_case[classify]:
                if self.assembly[terms].isChecked():
                    i += 1
            if i == sum:
                self.assembly[classify][1].setCheckState(Qt.Checked)
            elif i != 0:
                self.assembly[classify][1].setTristate()
                self.assembly[classify][1].setCheckState(Qt.PartiallyChecked)
            else:
                self.assembly[classify][1].setTristate(False)
                self.assembly[classify][1].setCheckState(Qt.Unchecked)

        return wrapper


# 积累场景泛化用例
class CaseAdWindows(TemplateWindows):
    def __init__(self):
        TemplateWindows.__init__(self)


# 七层场景泛化用例
class CaseSceneWindows(TemplateWindows):
    def __init__(self):
        TemplateWindows.__init__(self)

    def init_element(self):
        self.btn_dump_case = QPushButton('导出用例场景')
        self.btn_road_panel = QPushButton('1.道路信息')
        self.btn_traffic_panel = QPushButton('2.交通设施')
        self.btn_temporary_panel = QPushButton('3.临时作业')
        self.btn_vut_panel = QPushButton('4.自车行为')
        self.btn_gvt_panel = QPushButton('5.目标行为')
        self.btn_environment_panel = QPushButton('6.环境信息')
        self.btn_digital_panel = QPushButton('7.数字信息')

        path1 = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'simulation/cfgs/scene_road_structure_cfg.json')
        path2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'simulation/cfgs/scene_traffic_config.json')
        path3 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'simulation/cfgs/scene_temporary_config.json')
        path4 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'simulation/cfgs/scene_vut_config.json')
        path5 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'simulation/cfgs/scene_gvt_config.json')
        path6 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'simulation/cfgs/scene_env_config.json')
        path7 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'simulation/cfgs/scene_digital_config.json')

        self.form1 = SceneParamsWindows(path1)
        self.form2 = SceneParamsWindows(path2)
        self.form3 = SceneParamsWindows(path3)
        self.form4 = SceneParamsWindows(path4)
        self.form5 = SceneParamsWindows(path5)
        self.form6 = SceneParamsWindows(path6)
        self.form7 = SceneParamsWindows(path7)

        scene_dict = utils.get_json_data(path1)
        # scene_dict = {**scene_dict, **utils.get_json_data(path2)}
        # self.scene_dict = {**self.scene_dict, **utils.get_json_data(path3)}
        # self.scene_dict = {**self.scene_dict, **utils.get_json_data(path4)}
        # self.scene_dict = {**self.scene_dict, **utils.get_json_data(path5)}
        # self.scene_dict = {**self.scene_dict, **utils.get_json_data(path6)}
        # self.scene_dict = {**self.scene_dict, **utils.get_json_data(path7)}

        self.case_scene = {}
        for key, value in scene_dict.items():
            pass
            # self.case_scene = {**self.case_scene, **value}

    def init_controller(self):
        self.btn_dump_case.clicked.connect(self.case_sence_maker)
        self.btn_road_panel.clicked.connect(self.btn_press1_clicked)
        self.btn_traffic_panel.clicked.connect(self.btn_press2_clicked)
        self.btn_temporary_panel.clicked.connect(self.btn_press3_clicked)
        self.btn_vut_panel.clicked.connect(self.btn_press4_clicked)
        self.btn_gvt_panel.clicked.connect(self.btn_press5_clicked)
        self.btn_environment_panel.clicked.connect(self.btn_press6_clicked)
        self.btn_digital_panel.clicked.connect(self.btn_press7_clicked)

    def init_layout(self):
        # 局部垂直布局
        v_box = QVBoxLayout()
        v_box.addWidget(self.btn_road_panel)
        v_box.addWidget(self.btn_traffic_panel)
        v_box.addWidget(self.btn_temporary_panel)
        v_box.addWidget(self.btn_vut_panel)
        v_box.addWidget(self.btn_gvt_panel)
        v_box.addWidget(self.btn_environment_panel)
        v_box.addWidget(self.btn_digital_panel)
        v_box.addWidget(self.btn_dump_case)

        # 局部堆叠布局
        widget = QWidget()
        # widget.setStyleSheet("background-color:#CCFFCC;")
        self.stacked_layout = QStackedLayout()
        widget.setLayout(self.stacked_layout)

        self.stacked_layout.addWidget(self.form1)
        self.stacked_layout.addWidget(self.form2)
        self.stacked_layout.addWidget(self.form3)
        self.stacked_layout.addWidget(self.form4)
        self.stacked_layout.addWidget(self.form5)
        self.stacked_layout.addWidget(self.form6)
        self.stacked_layout.addWidget(self.form7)

        # 局部水平布局
        global_box = QHBoxLayout()
        global_box.addLayout(v_box)
        global_box.addWidget(widget)

        self.setLayout(global_box)

    def case_sence_maker(self):
        column_list1, condition_list1 = self.form1.dump_scene_condition()
        column_list2, condition_list2 = self.form2.dump_scene_condition()
        column_list3, condition_list3 = self.form3.dump_scene_condition()
        column_list4, condition_list4 = self.form4.dump_scene_condition()
        column_list5, condition_list5 = self.form5.dump_scene_condition()
        column_list6, condition_list6 = self.form6.dump_scene_condition()
        column_list7, condition_list7 = self.form7.dump_scene_condition()
        columns = column_list1 + column_list2 + column_list3 + column_list4 + column_list5 + column_list6 + column_list7
        conditions = condition_list1 + condition_list2 + condition_list3 + condition_list4 + condition_list5 + condition_list6 + condition_list7

        # columns = column_list1
        # conditions = condition_list1
        columns.insert(0, "NO")
        df = pd.DataFrame(columns=columns)
        for i, pairs in enumerate(AllPairs(conditions)):
            if self.is_valid_combination(pairs):
                df.loc[i] = [i] + pairs
                print(i, pairs)
        df.to_csv('1.csv', index=False)

    def is_valid_combination(self, conditions):
        excludes = []
        # for i in range(len(conditions)):
        #     if conditions[i] != '无': excludes.extend(self.case_scene[conditions[i]]['exclude'])
        # for i in range(len(conditions)):
        #     if conditions[i] != '无' and self.case_scene[conditions[i]]['id'] in excludes: return False
        return True

    def btn_press1_clicked(self):
        self.stacked_layout.setCurrentIndex(0)

    def btn_press2_clicked(self):
        self.stacked_layout.setCurrentIndex(1)

    def btn_press3_clicked(self):
        self.stacked_layout.setCurrentIndex(2)

    def btn_press4_clicked(self):
        self.stacked_layout.setCurrentIndex(3)

    def btn_press5_clicked(self):
        self.stacked_layout.setCurrentIndex(4)

    def btn_press6_clicked(self):
        self.stacked_layout.setCurrentIndex(5)

    def btn_press7_clicked(self):
        self.stacked_layout.setCurrentIndex(6)


# 用例场景生成
class SceneParamsWindows(TemplateWindows):
    def __init__(self, path):
        self.scene_case = utils.get_json_data(path)
        TemplateWindows.__init__(self)

    def init_ui(self):
        self.setGeometry(600, 400, 1080, 720)

    def init_element(self):
        # self.btn_export_case = QPushButton('导出场景用例')
        self.assembly = OrderedDict()
        # 全局垂直布局
        global_box = QVBoxLayout()
        positions = [(i, j) for i in range(8) for j in range(1, 5)]

        for classify in self.scene_case.keys():
            g_box = QGridLayout()
            global_box.addLayout(g_box)
            self.assembly[classify] = (QLabel(classify), QCheckBox('全选'))
            g_box.addWidget(self.assembly[classify][0], 0, 0, -1, 1)
            g_box.addWidget(self.assembly[classify][1], 1, 0, -1, 1)
            self.assembly[classify][0].setStyleSheet("background-color:#CCCCCC;")
            self.assembly[classify][1].stateChanged.connect(self.change_cb1(classify))
            i = 0
            for terms, position in zip(self.scene_case[classify], positions):
                i += 1
                self.assembly[terms] = QCheckBox(terms)
                g_box.addWidget(self.assembly[terms], *position)
                self.assembly[terms].stateChanged.connect(self.change_cb2(classify))

            while i < 4:
                i += 1
                g_box.addWidget(QLabel(''), 0, i)

        global_box.addStretch(1)
        self.setLayout(global_box)

    def dump_scene_condition(self):
        condition_list = []
        index_list = []
        for classify in self.scene_case.keys():
            classify_list = []
            for terms in self.scene_case[classify]:
                if self.assembly[terms].isChecked():
                    # if self.assembly[terms].isChecked() and self.scene_case[classify][terms]['invalid'] == 0:
                    classify_list.append(terms)

            if not classify_list:
                classify_list.append('default')
            index_list.append(classify)
            condition_list.append(classify_list)
        return index_list, condition_list

    def change_cb1(self, classify):
        def wrapper():
            if self.assembly[classify][1].checkState() == Qt.Checked:
                for terms in self.scene_case[classify]:
                    self.assembly[terms].setCheckState(Qt.Checked)
            elif self.assembly[classify][1].checkState() == Qt.Unchecked:
                for terms in self.scene_case[classify]:
                    self.assembly[terms].setCheckState(Qt.Unchecked)

        return wrapper

    def change_cb2(self, classify):
        def wrapper():
            i = 0
            sum = len(self.scene_case[classify])
            for terms in self.scene_case[classify]:
                if self.assembly[terms].isChecked():
                    i += 1
            if i == sum:
                self.assembly[classify][1].setCheckState(Qt.Checked)
            elif i != 0:
                self.assembly[classify][1].setTristate()
                self.assembly[classify][1].setCheckState(Qt.PartiallyChecked)
            else:
                self.assembly[classify][1].setTristate(False)
                self.assembly[classify][1].setCheckState(Qt.Unchecked)

        return wrapper


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
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'common/config/classify_problems_config.json')
        self.problems_type = utils.get_json_data(path)["classify"]
        self.row_dict = OrderedDict()

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
        grid.addWidget(QLabel('测试车辆'), 1, 3, 1, 1), grid.addWidget(self.line_vehicel, 1, 4, 1, 1)
        grid.addWidget(QLabel('整包版本'), 1, 5, 1, 1), grid.addWidget(self.line_driving_version, 1, 6, 1, 1)
        grid.addWidget(QLabel('天气'), 1, 7, 1, 1), grid.addWidget(self.line_weather, 1, 8, 1, 1)
        grid.addWidget(QLabel('测试路段'), 1, 9, 1, 1), grid.addWidget(self.line_road_level, 1, 10, 1, 1)
        grid.addWidget(QLabel('功能类别'), 1, 11, 1, 1), grid.addWidget(self.line_func, 1, 12, 1, 1)

        # 局部网络布局
        g_box = QGridLayout()
        g_box.SizeConstraint()
        positions = [(i, j) for i in range(8) for j in range(4)]
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

        combox_result.append('实车测试')
        combox_result.append('缺陷问题')
        combox_result.append(self.line_tester.text())

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
        self._problem_list.setHorizontalHeaderLabels(['NO', 'Date', 'Time', 'Problem', 'Summary'])

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
        df.iloc[df.shape[0] - 1, [5, 6, 7, 10, 11, 13, 15, 17, 19]] = self.get_combox_text()
        df.to_excel(note_vehicle_problems.FILE_NAME, index=False, engine='openpyxl')

    def slot_show_main(self):
        self.hide()
        self.mainwindows = MainWindows()
        self.mainwindows.show()


# 实车问题筛选界面
class FilterProblemWindows(TemplateWindows):
    def __init__(self):
        TemplateWindows.__init__(self)

    def init_ui(self):
        self.setWindowTitle('实车问题筛选')
        self.setGeometry(600, 400, 480, 240)

    def init_element(self):
        self.filter_problem = QPushButton('开始处理数据')
        self.file_label = DropArea('拖入数据目录')
        self.file_path = ''
        self.cb = OrderedDict()
        for key, value in utils.FUNCTION_SET.items():
            if value[1] == 'vehicle':
                self.cb[key] = QCheckBox(key, self)

    def init_controller(self):
        self.filter_problem.clicked.connect(self.filter_vehicle_problem)
        self.file_label.path_signal.connect(self.file_callback)

    def init_layout(self):
        # 局部水平布局
        h_box = QHBoxLayout()
        h_box.addWidget(self.filter_problem)

        # 局部网络布局
        g_box = QGridLayout()
        positions = [(i, j) for i in range(8) for j in range(3)]
        for temp, position in zip(self.cb.values(), positions):
            g_box.addWidget(temp, *position)

        # 全局垂直布局
        v_box = QVBoxLayout()
        v_box.addWidget(self.file_label)
        v_box.addLayout(g_box)
        v_box.addLayout(h_box)

        self.setLayout(v_box)

    def init_qss(self):
        self.filter_problem.setStyleSheet(
            '''QPushButton{background:#CCFFFF;border-radius:5px;}QPushButton:hover{background:green;}''')

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
                filter_vehicle_scene.get_vehicle_scene(self.file_path, func_list)


# 问题数据切片界面
class ExtractDataWindows(TemplateWindows):
    def __init__(self):
        TemplateWindows.__init__(self)

    def init_ui(self):
        self.setWindowTitle('问题数据切片')
        self.setGeometry(600, 400, 480, 200)

    def init_element(self):
        self.btn_extract = QPushButton('数据切片', self)
        self.excel_label = DropArea('拖入问题记录表')
        self.file_label = DropArea('拖入数据目录')

        self.excel_path = ''
        self.file_path = ''

    def init_controller(self):
        self.btn_extract.clicked.connect(self.extract_problem)
        self.excel_label.path_signal.connect(self.excel_callback)
        self.file_label.path_signal.connect(self.file_callback)

    def init_layout(self):
        # 局部水平布局
        h_box = QHBoxLayout()
        h_box.addWidget(self.btn_extract)

        # 局部水平布局
        h2_box = QHBoxLayout()
        h2_box.addWidget(self.excel_label)
        h2_box.addWidget(self.file_label)

        # 全局垂直布局
        global_box = QVBoxLayout()
        global_box.addLayout(h2_box)
        global_box.addLayout(h_box)

        self.setLayout(global_box)

    def init_qss(self):
        self.btn_extract.setStyleSheet(
            '''QPushButton{background:#CCFFFF;border-radius:5px;}QPushButton:hover{background:green;}''')

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
        if self.excel_path and self.file_path:
            try:
                note_vehicle_problems.ExtractModule(self.file_path, self.excel_path)()
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

    def init_element(self):
        self.btn_filter_panel = QPushButton('实车问题筛选')
        self.btn_extract_panel = QPushButton('问题数据切片')
        self.btn_problem_panel = QPushButton('实车问题记录')

    def init_controller(self):
        self.btn_filter_panel.clicked.connect(self.btn_press1_clicked)
        self.btn_extract_panel.clicked.connect(self.btn_press2_clicked)
        self.btn_problem_panel.clicked.connect(self.slot_show_problem)

        self.form1 = FilterProblemWindows()
        self.form2 = ExtractDataWindows()

    def init_layout(self):
        # 局部水平布局
        h_box = QHBoxLayout()
        h_box.addWidget(self.btn_filter_panel)
        h_box.addWidget(self.btn_extract_panel)
        h_box.addWidget(self.btn_problem_panel)

        # 局部堆叠布局
        widget = QWidget()
        self.stacked_layout = QStackedLayout()
        widget.setLayout(self.stacked_layout)
        widget.setStyleSheet("border: 2px solid black")

        self.stacked_layout.addWidget(self.form1)
        self.stacked_layout.addWidget(self.form2)

        # 全局垂直布局
        global_box = QVBoxLayout()
        global_box.addLayout(h_box)
        global_box.addWidget(widget)

        self.setLayout(global_box)

    def init_qss(self):
        self.btn_filter_panel.setStyleSheet("background-color: #CCFFFF")
        self.btn_extract_panel.setStyleSheet("background-color: #CCFFFF")
        self.btn_problem_panel.setStyleSheet("background-color: #CCFFFF")

    def btn_press1_clicked(self):
        self.stacked_layout.setCurrentIndex(0)

    def btn_press2_clicked(self):
        self.stacked_layout.setCurrentIndex(1)

    def slot_show_problem(self):
        self.mainwindows = MainWindows()
        self.mainwindows.hide()
        self.show_windows = RecordProblemWindows()
        self.show_windows.show()


# 仿真测试面板
class SimulationWindows(TemplateWindows):
    def __init__(self):
        TemplateWindows.__init__(self)

    def init_element(self):
        self.btn_case_pannel = QPushButton('仿真用例生成')
        self.btn_evaluate_pannel = QPushButton('仿真结果评测')

    def init_controller(self):
        self.btn_case_pannel.clicked.connect(self.slot_show_case)

    def init_layout(self):
        vSpacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)

        # 局部网络布局
        g_box = QGridLayout()
        g_box.addWidget(self.btn_case_pannel)
        g_box.addWidget(self.btn_evaluate_pannel)

        # 全局垂直布局
        global_box = QVBoxLayout()
        global_box.addLayout(g_box)
        global_box.addItem(vSpacer)

        self.setLayout(global_box)

    def init_qss(self):
        self.btn_case_pannel.setStyleSheet(
            '''QPushButton{background:#CCCCCC;border-radius:2px;}QPushButton:hover{background:green;}''')
        self.btn_evaluate_pannel.setStyleSheet(
            '''QPushButton{background:#CCCCCC;border-radius:2px;}QPushButton:hover{background:green;}''')

    def slot_show_case(self):
        self.mainwindows = MainWindows()
        self.mainwindows.hide()
        self.show_windows = TestCaseWindows()
        self.show_windows.show()


# 感知测试面板
class SenseWindows(TemplateWindows):
    def __init__(self):
        TemplateWindows.__init__(self)

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
        h_box.addStretch(1)

        # 局部堆叠布局
        widget = QWidget()
        self.stacked_layout = QStackedLayout()
        widget.setLayout(self.stacked_layout)
        widget.setStyleSheet("border: 2px solid black")

        self.stacked_layout.addWidget(self.form1)
        self.stacked_layout.addWidget(self.form2)
        self.stacked_layout.addWidget(self.form3)
        self.stacked_layout.addWidget(self.form4)

        # 全局垂直布局
        global_box = QVBoxLayout()
        global_box.addLayout(h_box)
        global_box.addWidget(widget)

        self.setLayout(global_box)

    def init_qss(self):
        self.btn_kpi_panel.setStyleSheet("background-color:#0099CC;")
        self.btn_problem_panel.setStyleSheet("background-color:#CCFF66;")
        self.btn_other_panel.setStyleSheet("background-color:#0099FF;")
        self.btn_draw_panel.setStyleSheet("background-color:#FFFFCC;")

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

    def init_qss(self):
        self.btn_img2avi.setStyleSheet("background-color:#CCCCCC;border-radius:2px;")
        self.btn_png2yuv.setStyleSheet("background-color:#CCCCCC;border-radius:2px;")
        self.btn_png2bmp.setStyleSheet("background-color:#CCCCCC;border-radius:2px;")
        self.btn_transform_3d.setStyleSheet("background-color:#CCCCCC;")

        self.file_label.setStyleSheet("border: 2px solid black")
        self.result_label.setStyleSheet("border: 2px solid black")

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

        self.label_icon = QLabel()
        self.label_icon.setFixedSize(152, 56)
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static/icon.png')
        self.label_icon.setPixmap(QPixmap(path))
        self.label_icon.setScaledContents(True)

        self.form1 = VehicleWindows()
        self.form2 = SimulationWindows()
        self.form3 = SenseWindows()
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

        v_box1.addWidget(self.label_icon)
        v_box1.addWidget(self.btn_first_panel)
        v_box1.addWidget(self.btn_second_panel)
        v_box1.addWidget(self.btn_third_panel)
        v_box1.addWidget(self.btn_fourth_panel)
        v_box1.addItem(vSpacer)

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

    def init_qss(self):
        self.label_icon.setStyleSheet("border: 2px solid red")
        self.btn_first_panel.setStyleSheet(
            '''QPushButton{background:#CCFF99;border-radius:5px;}QPushButton:hover{background:green;}''')
        self.btn_second_panel.setStyleSheet(
            '''QPushButton{background:#CCFF99;border-radius:5px;}QPushButton:hover{background:green;}''')
        self.btn_third_panel.setStyleSheet(
            '''QPushButton{background:#CCFF99;border-radius:5px;}QPushButton:hover{background:green;}''')
        self.btn_fourth_panel.setStyleSheet(
            '''QPushButton{background:#CCFF99;border-radius:5px;}QPushButton:hover{background:green;}''')

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
