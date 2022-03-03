# -*- coding: utf-8 -*-

import os, sys, json, time
import numpy as np
import pandas as pd
import qtawesome as qta
from PyQt5 import QtCore, QtGui, QtWidgets
from eliot import start_action, to_file
from functools import partial
from itertools import product, islice

# TIME_NOW = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
# LOG_NAME = "./log/" + TIME_NOW + ".log"
# if not os.path.exists(LOG_NAME):
#     if not os.path.exists("./log/"):
#         os.mkdir("./log")
#     os.mknod(LOG_NAME)
# to_file(open(LOG_NAME, 'w'))

LAYER_PARAMS_DICT = dict()
SELECTED_LAYER = list()

MAIN_WINDOW_STYLE = '''
QWidget{
    color: black;
    background: Azure;
}
QLineEdit{
    border: 1px solid gray;
    border-radius: 5px;
    padding: 2px 4px;
    background: pink;
}
QCheckBox::indicator{
    width: 13px;
    height:13px;
    padding: 2px 2px;
}
QLabel{
    border: 4px groove PeachPuff;
    font-size: 16px;
    font-weight: 500;
    background: PapayaWhip;
}
QPushButton{
    background: LightGoldenRodYellow;
    border-radius: 4px;
    border: 4px inset LemonChiffon;
}
QPushButton:hover{
    background:LightYellow;
}
QPushButton:pressed{
    border-style: outset;
    padding-left: 2px;
    padding-top: 2px;
    background: LightYellow;
}
'''

STACKED_WINDOW_STYLE = '''
QWidget{
    color: black;
    background: Azure;
}
QLabel{
    border: 3px outset Aqua;
    font-size: 16px;
    font-weight: 500;
    background:transparent;
}
'''


class ParamsDisplayWindow(QtWidgets.QDialog):
    def __init__(self, file_name):
        super(ParamsDisplayWindow, self).__init__()
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.SetupUI(file_name)
        self.setStyleSheet(
            "QLabel {background: FloralWhite;grborder: 2px oove #242424; border-color: GhostWhite;border-radius: 5px; color: Black;},QCheckBoxdd::checked {color: Red}"
        )

    def SetupUI(self, file_name):
        self.setWindowTitle("参数确认")
        self.resize(800, 400)
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        window_size = self.geometry()
        self.move((screen.width() - window_size.width()) / 2,
                  (screen.height() - window_size.height()) / 2)
        self.widget_layout_ = QtWidgets.QVBoxLayout(self)
        self.layer_stacked_layout_ = QtWidgets.QStackedLayout()
        self.genetate_default_params_checkbox_ = QtWidgets.QCheckBox(
            "是否生成默认参数")
        push_button_layout = QtWidgets.QHBoxLayout()
        return_button = QtWidgets.QPushButton("返回")
        return_button.clicked.connect(self.reject)
        generate_button = QtWidgets.QPushButton("生成场景库文件")
        generate_button.clicked.connect(
            partial(self.GenerateSceneLibrary, file_name))
        push_button_layout.addWidget(return_button)
        push_button_layout.addWidget(generate_button)
        for layer in sorted(SELECTED_LAYER):
            stacked_widget = QtWidgets.QWidget()
            layer_param_layout = QtWidgets.QGridLayout(stacked_widget)
            grid_layout_idx = 0
            default_param_dict = LAYER_PARAMS_DICT[layer]["default"]
            user_param_dict = LAYER_PARAMS_DICT[layer]["user"]
            user_layer_label = QtWidgets.QLabel(layer + u"（用户）")
            user_layer_label.setFixedHeight(40)
            default_layer_label = QtWidgets.QLabel(layer + u"（默认）")
            default_layer_label.setFixedHeight(40)
            layer_param_layout.addWidget(user_layer_label, grid_layout_idx, 1)
            layer_param_layout.addWidget(default_layer_label, grid_layout_idx,
                                         2)
            grid_layout_idx += 1
            for param in sorted(default_param_dict.keys()):
                param_label = QtWidgets.QLabel(param)
                param_label.setFixedWidth(150)
                param_label.setFixedHeight(30)
                layer_param_layout.addWidget(param_label, grid_layout_idx, 0)
                if isinstance(default_param_dict[param][0], basestring):
                    user_param_text = self.GenerateNonNumericParamStr(
                        user_param_dict[param]
                    ) if user_param_dict[param] else '-'
                    default_param_text = self.GenerateNonNumericParamStr(
                        default_param_dict[param])
                else:
                    user_param_text = self.GenerateNumericParamStr(
                        user_param_dict[param]
                    ) if user_param_dict[param] else '-'
                    default_param_text = self.GenerateNumericParamStr(
                        default_param_dict[param])
                user_param_label = QtWidgets.QLabel(user_param_text)
                user_param_label.setFixedHeight(30)
                default_param_label = QtWidgets.QLabel(default_param_text)
                default_param_label.setFixedHeight(30)
                layer_param_layout.addWidget(user_param_label, grid_layout_idx,
                                             1)
                layer_param_layout.addWidget(default_param_label,
                                             grid_layout_idx, 2)
                grid_layout_idx += 1
            self.layer_stacked_layout_.addWidget(stacked_widget)
        layer_switch_layout = QtWidgets.QHBoxLayout()
        previous_button = QtWidgets.QPushButton("前一层")
        previous_button.clicked.connect(self.PreviousLayer)
        next_button = QtWidgets.QPushButton("后一层")
        next_button.clicked.connect(self.NextLayer)
        layer_switch_layout.addWidget(previous_button)
        layer_switch_layout.addLayout(self.layer_stacked_layout_)
        layer_switch_layout.addWidget(next_button)
        self.widget_layout_.addWidget(self.genetate_default_params_checkbox_)
        self.widget_layout_.addLayout(layer_switch_layout)
        self.widget_layout_.addLayout(push_button_layout)

    def GenerateNonNumericParamStr(self, param_list):
        ret_str = ""
        for val in param_list:
            ret_str += val + u"、"
        return ret_str[:-1]

    def GenerateNumericParamStr(self, param_list):
        min_val_str = "最小值：{} ".format(str(param_list[0]))
        max_val_str = "最大值：{} ".format(str(param_list[1]))
        step_val_str = "步长：{}".format(str(param_list[2]))
        return min_val_str + max_val_str + step_val_str

    def PreviousLayer(self):
        layer_num = self.layer_stacked_layout_.count()
        layer_idx = self.layer_stacked_layout_.currentIndex() - 1
        if layer_idx < 0:
            layer_idx = layer_num - 1
        self.layer_stacked_layout_.setCurrentIndex(layer_idx)

    def NextLayer(self):
        layer_num = self.layer_stacked_layout_.count()
        layer_idx = self.layer_stacked_layout_.currentIndex() + 1
        if layer_idx >= layer_num:
            layer_idx = 0
        self.layer_stacked_layout_.setCurrentIndex(layer_idx)

    def GenerateSceneLibrary(self, file_name):
        genetate_default_params = True if self.genetate_default_params_checkbox_.isChecked(
        ) else False
        header_list = list()
        combination_list = list()
        for layer in sorted(SELECTED_LAYER):
            default_param_dict = LAYER_PARAMS_DICT[layer]["default"]
            user_param_dict = LAYER_PARAMS_DICT[layer]["user"]
            for param in sorted(default_param_dict.keys()):
                if not (user_param_dict[param] or genetate_default_params):
                    continue
                curr_param_str = layer + '.' + param
                param_list = user_param_dict[param] if user_param_dict[
                    param] else default_param_dict[param]
                if not isinstance(default_param_dict[param][0], basestring):
                    param_list = np.arange(param_list[0], param_list[1],
                                           param_list[2])
                if len(param_list):
                    header_list.append(curr_param_str)
                    combination_list.append(param_list)
        combination_list = list(islice(product(*combination_list), 5000000))
        params_to_generate_dict = dict()
        for idx, header in enumerate(header_list):
            param_list = [param[idx] for param in combination_list]
            params_to_generate_dict[header] = param_list
        table_datafeame = pd.DataFrame(params_to_generate_dict)
        print(table_datafeame)
        table_datafeame.to_csv(file_name, encoding='utf-8')
        self.accept()


class LayerStackedWindow(QtWidgets.QDialog):
    def __init__(self, file_name):
        super(LayerStackedWindow, self).__init__()
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.SetupUI(file_name)
        self.setStyleSheet(STACKED_WINDOW_STYLE)

    def SetupUI(self, file_name):
        self.setWindowTitle("配置结构层参数")
        self.resize(600, 400)
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        window_size = self.geometry()
        self.move((screen.width() - window_size.width()) / 2,
                  (screen.height() - window_size.height()) / 2)
        self.widget_layout_ = QtWidgets.QVBoxLayout(self)
        self.layer_stacked_layout_ = QtWidgets.QStackedLayout()
        self.layer_button_layout_ = QtWidgets.QHBoxLayout()
        self.functional_button_layout_ = QtWidgets.QHBoxLayout()
        return_button = QtWidgets.QPushButton("返回")
        return_button.clicked.connect(self.reject)
        next_button = QtWidgets.QPushButton("下一步")
        next_button.clicked.connect(partial(self.ParamsConfirmation,
                                            file_name))
        self.functional_button_layout_.addWidget(return_button)
        self.functional_button_layout_.addWidget(next_button)
        for layer in sorted(SELECTED_LAYER):
            stacked_widget = QtWidgets.QWidget()
            param_dict = LAYER_PARAMS_DICT[layer]
            layer_grid_layout = QtWidgets.QGridLayout(stacked_widget)
            layer_grid_layout.setColumnStretch(0, 1)
            layer_grid_layout.setColumnStretch(1, 4)
            grid_layout_idx = 0
            for param in sorted(param_dict["default"].keys()):
                param_label = QtWidgets.QLabel(param)
                param_label.setAlignment(QtCore.Qt.AlignCenter)
                layer_grid_layout.addWidget(param_label, grid_layout_idx, 0)
                val_horizontal_layout = QtWidgets.QHBoxLayout()
                if isinstance(param_dict["default"][param][0], basestring):
                    for val in param_dict["default"][param]:
                        val_button = QtWidgets.QCheckBox(val)
                        if val in param_dict["user"][param]:
                            val_button.setChecked(True)
                        val_horizontal_layout.addWidget(val_button)
                        val_button.clicked.connect(
                            partial(self.NonNumericParamChanged, layer, param,
                                    val, val_button))
                else:
                    min_val_label = QtWidgets.QLabel("最小值")
                    min_val_text = QtWidgets.QLineEdit()
                    min_val_text.setText(str(
                        param_dict["user"][param][0])) if param_dict["user"][
                        param] else min_val_text.setPlaceholderText(
                        str(param_dict["default"][param][0]))
                    max_val_label = QtWidgets.QLabel("最大值")
                    max_val_text = QtWidgets.QLineEdit()
                    max_val_text.setText(str(
                        param_dict["user"][param][1])) if param_dict["user"][
                        param] else max_val_text.setPlaceholderText(
                        str(param_dict["default"][param][1]))
                    step_label = QtWidgets.QLabel("步长")
                    step_text = QtWidgets.QLineEdit()
                    step_text.setText(str(
                        param_dict["user"][param][2])) if param_dict["user"][
                        param] else step_text.setPlaceholderText(
                        str(param_dict["default"][param][2]))
                    val_horizontal_layout.addWidget(max_val_label)
                    val_horizontal_layout.addWidget(max_val_text)
                    val_horizontal_layout.addWidget(min_val_label)
                    val_horizontal_layout.addWidget(min_val_text)
                    val_horizontal_layout.addWidget(step_label)
                    val_horizontal_layout.addWidget(step_text)
                    min_val_text.textChanged.connect(
                        partial(self.MinValParamChanged, layer, param,
                                min_val_text))
                    max_val_text.textChanged.connect(
                        partial(self.MaxValParamChanged, layer, param,
                                max_val_text))
                    step_text.textChanged.connect(
                        partial(self.StepValParamChanged, layer, param,
                                step_text))
                layer_grid_layout.addLayout(val_horizontal_layout,
                                            grid_layout_idx, 1)
                grid_layout_idx += 1
            self.layer_stacked_layout_.addWidget(stacked_widget)
            layer_button = QtWidgets.QPushButton(layer)
            layer_button.clicked.connect(
                partial(self.LayerChanged, stacked_widget))
            self.layer_button_layout_.addWidget(layer_button)
        self.widget_layout_.addLayout(self.layer_button_layout_)
        self.widget_layout_.addLayout(self.layer_stacked_layout_)
        self.widget_layout_.addLayout(self.functional_button_layout_)

    def LayerChanged(self, widget):
        self.layer_stacked_layout_.setCurrentWidget(widget)

    def NonNumericParamChanged(self, layer, param, val, val_button):
        user_param_list = LAYER_PARAMS_DICT[layer]["user"][param]
        if (val_button.isChecked()) and (val not in user_param_list):
            user_param_list.append(val)
        elif (not val_button.isChecked()) and (val in user_param_list):
            user_param_list.remove(val)
        else:
            pass

    def MinValParamChanged(self, layer, param, line_edit):
        default_param_list = LAYER_PARAMS_DICT[layer]["default"][param]
        user_param_list = LAYER_PARAMS_DICT[layer]["user"][param]
        try:
            min_val = float(line_edit.text())
            max_val = user_param_list[
                1] if user_param_list else default_param_list[1]
            step_val = user_param_list[
                2] if user_param_list else default_param_list[2]
            if not len(np.arange(min_val, max_val, step_val)):
                QtWidgets.QMessageBox.warning(self, "Warning", "请填写合适的最小值！")
                return
            LAYER_PARAMS_DICT[layer]["user"][param] = [
                min_val, max_val, step_val
            ]
        except:
            if not line_edit.text() and user_param_list:
                if user_param_list[1] == default_param_list[
                    1] and user_param_list[2] == default_param_list[2]:
                    user_param_list.clear()
                else:
                    user_param_list[0] = default_param_list[0]
            else:
                return

    def MaxValParamChanged(self, layer, param, line_edit):
        default_param_list = LAYER_PARAMS_DICT[layer]["default"][param]
        user_param_list = LAYER_PARAMS_DICT[layer]["user"][param]
        try:
            max_val = float(line_edit.text())
            min_val = user_param_list[
                0] if user_param_list else default_param_list[0]
            step_val = user_param_list[
                2] if user_param_list else default_param_list[2]
            if not len(np.arange(min_val, max_val, step_val)):
                QtWidgets.QMessageBox.warning(self, "Warning", "请填写合适的最大值！")
                return
            LAYER_PARAMS_DICT[layer]["user"][param] = [
                min_val, max_val, step_val
            ]
        except:
            if not line_edit.text() and user_param_list:
                if user_param_list[0] == default_param_list[
                    0] and user_param_list[2] == default_param_list[2]:
                    user_param_list.clear()
                else:
                    user_param_list[1] = default_param_list[1]
            else:
                return

    def StepValParamChanged(self, layer, param, line_edit):
        default_param_list = LAYER_PARAMS_DICT[layer]["default"][param]
        user_param_list = LAYER_PARAMS_DICT[layer]["user"][param]
        try:
            step_val = float(line_edit.text())
            min_val = user_param_list[
                0] if user_param_list else default_param_list[0]
            max_val = user_param_list[
                1] if user_param_list else default_param_list[1]
            if not len(np.arange(min_val, max_val, step_val)):
                QtWidgets.QMessageBox.warning(self, "Warning", "请填写合适的步长！")
                return
            LAYER_PARAMS_DICT[layer]["user"][param] = [
                min_val, max_val, step_val
            ]
        except:
            if not line_edit.text() and user_param_list:
                if user_param_list[0] == default_param_list[
                    0] and user_param_list[1] == default_param_list[1]:
                    user_param_list.clear()
                else:
                    user_param_list[2] = default_param_list[2]
            else:
                return

    def ParamsConfirmation(self, file_name):
        params_display_window = ParamsDisplayWindow(file_name)
        if params_display_window.exec_() == QtWidgets.QDialog.Accepted:
            self.close()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.js_configs_ = self.LoadJsonConfigs()
        self.InitLayerParamsDict()
        self.SetupUI()
        self.SetupLayout()
        self.main_widget_.setStyleSheet(MAIN_WINDOW_STYLE)

    def LoadJsonConfigs(self):
        with open("./cfgs.json", 'r') as fd:
            return json.load(fd)

    def SetupUI(self):
        self.setWindowTitle("选择需要配置的结构层")
        self.resize(400, 400)
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        window_size = self.geometry()
        self.move((screen.width() - window_size.width()) / 2,
                  (screen.height() - window_size.height()) / 2)
        self.main_widget_ = QtWidgets.QWidget(self)
        self.setCentralWidget(self.main_widget_)
        self.scene_combo_box_ = QtWidgets.QComboBox()
        self.scene_combo_box_.addItems(["事故场景", "功能场景", "法规场景"])
        self.scene_combo_box_.setFont(qta.font('fa', 16))
        self.scene_label_ = QtWidgets.QLabel("场景: ")
        self.scene_label_.setFont(qta.font('fa', 20))
        self.scene_label_.setStyleSheet("border: none; background: none;")
        self.scene_line_edit_ = QtWidgets.QLineEdit()
        self.scene_line_edit_.editingFinished.connect(self.SceneChanged)
        self.reset_button_ = QtWidgets.QPushButton("重置参数")
        self.reset_button_.setFixedSize(70, 25)
        self.reset_button_.clicked.connect(self.ResetParams)
        self.next_button_ = QtWidgets.QPushButton("下一步")
        self.next_button_.setFixedSize(70, 25)
        self.next_button_.clicked.connect(self.ParamsConfiguration)

    def SetupLayout(self):
        self.widget_layout_ = QtWidgets.QVBoxLayout(self.main_widget_)
        split_line = QtWidgets.QFrame()
        split_line.setFrameShape(QtWidgets.QFrame.VLine)
        split_line.setFrameShadow(QtWidgets.QFrame.Sunken)
        scene_horizontal_layout = QtWidgets.QHBoxLayout()
        scene_horizontal_layout.addWidget(self.scene_combo_box_)
        scene_horizontal_layout.addWidget(split_line)
        scene_horizontal_layout.addWidget(self.scene_label_)
        scene_horizontal_layout.addWidget(self.scene_line_edit_)
        self.widget_layout_.addLayout(scene_horizontal_layout)
        structual_layer_grid_layout = QtWidgets.QGridLayout()
        structual_layer_grid_layout.setColumnStretch(0, 1)
        structual_layer_grid_layout.setColumnStretch(1, 4)
        grid_layout_index = 0
        self.structual_layer_checkbox_dict_ = dict()
        for layer in self.js_configs_["StructualLayers"]:
            layer_checkbox = QtWidgets.QCheckBox()
            self.structual_layer_checkbox_dict_[layer] = layer_checkbox
            structual_layer_grid_layout.addWidget(layer_checkbox,
                                                  grid_layout_index, 0,
                                                  QtCore.Qt.AlignHCenter)
            layer_label = QtWidgets.QLabel(layer)
            layer_label.setAlignment(QtCore.Qt.AlignCenter)
            layer_label.setFixedWidth(300)
            structual_layer_grid_layout.addWidget(layer_label,
                                                  grid_layout_index, 1,
                                                  QtCore.Qt.AlignHCenter)
            grid_layout_index += 1
        self.widget_layout_.addLayout(structual_layer_grid_layout)
        push_button_layout = QtWidgets.QHBoxLayout()
        push_button_layout.addWidget(self.reset_button_)
        push_button_layout.addWidget(self.next_button_)
        self.widget_layout_.addLayout(push_button_layout)

    def SceneChanged(self):
        if not self.scene_line_edit_.hasFocus():
            return
        if self.scene_line_edit_.text():
            self.scene_ = self.scene_line_edit_.text()
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "请填写要生成的场景！")

    def ResetParams(self):
        for layer in LAYER_PARAMS_DICT.keys():
            user_param_dict = LAYER_PARAMS_DICT[layer]["user"]
            for param in user_param_dict.keys():
                del user_param_dict[param][:]

    def ParamsConfiguration(self):
        global SELECTED_LAYER
        scene = self.scene_combo_box_.currentText()
        file_name = self.scene_line_edit_.text()
        if not file_name:
            QtWidgets.QMessageBox.warning(self, "Warning", "请填写具体场景！！")
            return
        file_name += '.csv'
        if not os.path.exists("./Scene"):
            os.mkdir("./Scene")
        scene_folder = os.path.join("./Scene", scene)
        if not os.path.exists(scene_folder):
            os.mkdir(scene_folder)
        SELECTED_LAYER = [
            layer for layer in self.structual_layer_checkbox_dict_.keys()
            if self.structual_layer_checkbox_dict_[layer].isChecked()
        ]
        if not len(SELECTED_LAYER):
            return
        layer_satcked_window = LayerStackedWindow(
            os.path.join(scene_folder, file_name))
        layer_satcked_window.exec_()

    def InitLayerParamsDict(self):
        layer_params_dict = self.js_configs_["LayerParams"]
        for layer in layer_params_dict.keys():
            LAYER_PARAMS_DICT[layer] = dict()
            LAYER_PARAMS_DICT[layer]["default"] = dict()
            LAYER_PARAMS_DICT[layer]["user"] = dict()
            for param in layer_params_dict[layer].keys():
                LAYER_PARAMS_DICT[layer]["default"][param] = layer_params_dict[
                    layer][param]
                LAYER_PARAMS_DICT[layer]["user"][param] = []


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = MainWindow()
    gui.show()
    app.exec_()
