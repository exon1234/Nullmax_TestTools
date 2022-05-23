# -*- coding: utf-8 -*-
# 实车问题筛选
import os
import sys
import time
import pandas as pd
from scripts.common import utils


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def get_vehicle_scene(filesPath, funcList):
    # basePath = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    basePath = os.path.dirname(os.path.abspath(sys.argv[0]))
    fileName = os.path.join(basePath, 'data', "SceneFilter" + '.xlsx')
    if not os.path.exists(fileName):
        df = pd.DataFrame(columns=['NO', 'Date', 'Time', 'Problem'], index=None)
        df.to_excel(fileName, index=False, engine='openpyxl')

    for bagData, bagPath in utils.get_bag_data(filesPath):
        for func in funcList:
            cls = func(fileName)
            cls(bagData, bagPath)


@utils.register('AEB触发场景', 'vehicle')
@singleton
class AEBFilter(object):
    """
    AEB触发场景数据筛选
    """

    def __init__(self, fileName):
        self.fileName = fileName
        self.is_active = False
        self.topicsList = ['/aeb/aebs_monitor']
        self.accelerate_list = []

    def __call__(self, bagData, bagPath):
        for topic, msg, t in bagData.read_messages(topics=self.topicsList):
            if topic == '/aeb/aebs_monitor':
                try:
                    aeb_active = msg.aeb_command.aeb_status
                    is_dbw = msg.ego_car_state.drive_mode
                    obstacle_distance = msg.aeb_obstacle_in_path.position.x
                    linear_velocity = msg.ego_car_state.linear_velocity
                    TTC = msg.aeb_obstacle_in_path.ttc
                    accelerate_x = msg.ego_car_state.linear_acceleration
                except Exception as E:
                    utils.logger.error(E)
                    break

                if aeb_active == 4 and self.is_active is False:
                    self.is_active = True
                    self.accelerate_list.append(accelerate_x)
                    data = pd.read_excel(self.fileName)
                    num = data.shape[0]
                    data_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t.to_sec()))
                    data.loc[num, 'NO'] = num + 1
                    data.loc[num, 'Date'] = data_time.split(' ')[0]
                    data.loc[num, 'Time'] = data_time.split(' ')[1]
                    data.loc[num, 'BagPath'] = bagPath
                    data.loc[num, 'Problem'] = '触发AEB'
                    data.loc[num, 'Distance'] = obstacle_distance
                    data.loc[num, 'Velocity'] = int(linear_velocity * 3.6)
                    data.loc[num, 'TTC'] = round(TTC, 2)
                    data.loc[num, 'Drive_Mode'] = is_dbw
                    data.to_excel(self.fileName, index=False, engine='openpyxl')

                if aeb_active == 2 and self.is_active is True:
                    data = pd.read_excel(self.fileName)
                    num = data.shape[0]
                    data.loc[num, 'acceleration'] = max(self.accelerate_list)
                    self.accelerate_list = []
                    self.is_active = False


@utils.register('MEB触发场景', 'vehicle')
@singleton
class MEBFilter(object):
    """
    MEB触发场景数据筛选
    """

    def __init__(self, fileName):
        self.fileName = fileName
        self.is_active = False
        self.topicsList = ['/aeb/aebs_monitor']
        self.accelerate_list = []

    def __call__(self, bagData, bagPath):
        for topic, msg, t in bagData.read_messages(topics=self.topicsList):
            if topic == '/aeb/aebs_monitor':
                try:
                    is_dbw = msg.ego_car_state.drive_mode
                    meb_active = msg.meb_command.meb_status
                    obstacle_distance = msg.aeb_obstacle_in_path.position.x
                    TTC = msg.aeb_obstacle_in_path.ttc
                    linear_velocity = msg.ego_car_state.linear_velocity
                    accelerate_x = msg.ego_car_state.linear_acceleration
                except Exception as E:
                    utils.logger.error(E)
                    break

                if meb_active == 4 and self.is_active is False:
                    self.is_active = True
                    self.accelerate_list.append(accelerate_x)
                    data = pd.read_excel(self.fileName)
                    num = data.shape[0]
                    data_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t.to_sec()))
                    data.loc[num, 'NO'] = num + 1
                    data.loc[num, 'Date'] = data_time.split(' ')[0]
                    data.loc[num, 'Time'] = data_time.split(' ')[1]
                    data.loc[num, 'BagPath'] = bagPath
                    data.loc[num, 'Problem'] = '触发MEB'
                    data.loc[num, 'Distance'] = obstacle_distance
                    data.loc[num, 'Velocity'] = int(linear_velocity * 3.6)
                    data.loc[num, 'TTC'] = round(TTC, 2)
                    data.loc[num, 'Drive_Mode'] = is_dbw
                    data.to_excel(self.fileName, index=False, engine='openpyxl')

                if meb_active == 2 and self.is_active is True:
                    data = pd.read_excel(self.fileName)
                    num = data.shape[0]
                    data.loc[num, 'acceleration'] = max(self.accelerate_list)
                    self.accelerate_list = []
                    self.is_active = False


@utils.register('TSR触发场景', 'vehicle')
@singleton
class TSRFilter(object):
    """
    交通标志场景数据筛选
    """

    def __init__(self, fileName):
        self.fileName = fileName
        self.topicsList = ['/perception/traffic_signs']
        self.last_time = 0

    def __call__(self, bagData, bagPath):
        for topic, msg, t in bagData.read_messages(topics=self.topicsList):
            if topic == '/perception/traffic_signs':
                try:
                    traffic_signs = msg.traffic_signs
                    now_time = t.to_sec()
                except Exception as E:
                    utils.logger.error(E)
                    break

                if now_time - self.last_time < 120:
                    continue

                if len(traffic_signs) > 0:
                    self.last_time = now_time
                    data = pd.read_excel(self.fileName)
                    data_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t.to_sec()))
                    num = data.shape[0]
                    data.loc[num, 'NO'] = num + 1
                    data.loc[num, 'Date'] = data_time.split(' ')[0]
                    data.loc[num, 'BagPath'] = bagPath
                    data.loc[num, 'Time'] = data_time.split(' ')[1]
                    data.loc[num, 'Problem'] = '交通标志牌'
                    data.to_excel(self.fileName, index=False, engine='openpyxl')


@utils.register('TLI触发场景', 'vehicle')
@singleton
class TLIFilter(object):
    """
    交通灯场景数据筛选
    """

    def __init__(self, fileName):
        self.fileName = fileName
        self.topicsList = ['/perception/traffic_lights']
        self.last_time = 0

    def __call__(self, bagData, bagPath):
        for topic, msg, t in bagData.read_messages(topics=self.topicsList):
            if topic == '/perception/traffic_signs':
                try:
                    traffic_signs = msg.traffic_signals
                    now_time = t.to_sec()
                except Exception as E:
                    utils.logger.error(E)
                    break

                if now_time - self.last_time < 120:
                    continue

                if len(traffic_signs) > 0:
                    self.last_time = now_time
                    data = pd.read_excel(self.fileName)
                    data_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t.to_sec()))
                    num = data.shape[0]
                    data.loc[num, 'NO'] = num + 1
                    data.loc[num, 'Date'] = data_time.split(' ')[0]
                    data.loc[num, 'BagPath'] = bagPath
                    data.loc[num, 'Time'] = data_time.split(' ')[1]
                    data.loc[num, 'Problem'] = '交通灯'
                    data.to_excel(self.fileName, index=False, engine='openpyxl')


@utils.register('感知错测类别', 'vehicle')
@singleton
class IncorrectSenseFilter(object):
    """
    感知检测目标类型跳变场景筛选
    """

    def __init__(self, fileName):
        self.fileName = fileName
        self.topicsList = ['/planning/vehicle_monitor']
        self.last_obstacle_in_path_id = None
        self.last_obstacle_in_path_type = None
        self.last_time = 0

    def __call__(self, bagData, bagPath):
        for topic, msg, t in bagData.read_messages(topics=self.topicsList):
            if topic == '/planning/vehicle_monitor':
                try:
                    new_obstacle_in_path_id = msg.obstacle_state.obstacle_in_path.id
                    new_obstacle_in_path_type = msg.obstacle_state.obstacle_in_path.type
                    obstacle_in_path_x = msg.obstacle_state.obstacle_in_path.position.x
                    now_time = t.to_sec()
                except Exception as E:
                    utils.logger.error(E)
                    break

                if self.last_obstacle_in_path_id != new_obstacle_in_path_id and (
                        self.last_obstacle_in_path_type != new_obstacle_in_path_type):
                    self.last_obstacle_in_path_id = new_obstacle_in_path_id
                    self.last_obstacle_in_path_type = new_obstacle_in_path_type

                if self.last_obstacle_in_path_id == new_obstacle_in_path_id and (
                        self.last_obstacle_in_path_type != new_obstacle_in_path_type):
                    if new_obstacle_in_path_type == 0:
                        continue
                    self.last_obstacle_in_path_type = new_obstacle_in_path_type
                    if now_time - self.last_time < 60 or obstacle_in_path_x > 80:
                        continue

                    self.last_time = now_time
                    data = pd.read_excel(self.fileName)
                    data_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t.to_sec()))
                    num = data.shape[0]
                    data.loc[num, 'NO'] = num + 1
                    data.loc[num, 'Date'] = data_time.split(' ')[0]
                    data.loc[num, 'Time'] = data_time.split(' ')[1]
                    data.loc[num, 'BagPath'] = bagPath
                    data.loc[num, 'Problem'] = '检测类别跳变'
                    data.loc[num, 'Distance'] = obstacle_in_path_x
                    data.to_excel(self.fileName, index=False, engine='openpyxl')


@utils.register('感知漏检目标', 'vehicle')
@singleton
class OmissionSenseFilter(object):
    """
    感知漏检障碍物目标场景筛选
    """

    def __init__(self, fileName):
        self.fileName = fileName
        self.topicsList = ['/input/perception/obstacle_list', '/perception/obstacle_list']
        self.last_cipv_id = None
        self.previous_last_cipv_id = None
        self.last_cipv_time = 0
        self.last_time = 0
        self.before_tracks = []

    def __call__(self, bagData, bagPath):
        for topic, msg, t in bagData.read_messages(topics=self.topicsList):
            if topic == '/input/perception/obstacle_list' or topic == '/perception/obstacle_list':
                new_cipv_id = msg.cipv_id
                tracks = msg.tracks
                now_time = t.to_sec()
                if self.last_cipv_id != new_cipv_id:
                    if (now_time - self.last_cipv_time) <= 1 and self.previous_last_cipv_id == new_cipv_id and (
                            new_cipv_id not in self.before_tracks) and new_cipv_id != 0 and (
                            now_time - self.last_time) > 120:
                        for i in range(len(tracks)):
                            if tracks[i].id == new_cipv_id:
                                self.last_time = now_time
                                cipv_x = tracks[i].position.x
                                data = pd.read_excel(self.fileName)
                                data_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t.to_sec()))
                                num = data.shape[0]
                                data.loc[num, 'NO'] = num + 1
                                data.loc[num, 'Date'] = data_time.split(' ')[0]
                                data.loc[num, 'BagPath'] = bagPath
                                data.loc[num, 'Time'] = data_time.split(' ')[1]
                                data.loc[num, 'Problem'] = '检测目标漏检'
                                data.loc[num, 'Obstracel_X'] = cipv_x
                                data.to_excel(self.fileName, index=False, engine='openpyxl')
                                break
                    self.previous_last_cipv_id = self.last_cipv_id
                    self.last_cipv_id = new_cipv_id
                    self.last_cipv_time = now_time
                tracks_id_list = []
                if len(tracks) > 0:
                    [tracks_id_list.append(tracks[i].id) for i in range(len(tracks))]
                self.before_tracks = tracks_id_list


@utils.register('cutin场景', 'vehicle')
@singleton
class CutInFilter(object):
    """
    cutin场景数据筛选
    """

    def __init__(self, fileName):
        self.fileName = fileName
        self.topicsList = ['/planning/vehicle_monitor']
        self.is_active = False
        self.last_time = 0

    def __call__(self, bagData, bagPath):
        for topic, msg, t in bagData.read_messages(topics=self.topicsList):
            if topic == '/planning/vehicle_monitor':
                try:
                    obstacle_in_path = msg.obstacle_state.obstacle_in_path.position.x
                    drive_mode = msg.ego_car_state.drive_mode
                    cut_in_and_out = msg.obstacle_state.obstacle_in_path.cut_in_and_out
                    linear_velocity = msg.ego_car_state.linear_velocity
                    # TTC = msg.obstacle_state.obstacle_in_path.ttc
                    now_time = t.to_sec()
                except Exception as E:
                    utils.logger.error(E)
                    break
                if cut_in_and_out == 2 and drive_mode != 0 and self.is_active is False:
                    self.is_active = True
                    if now_time - self.last_time > 60:
                        self.last_time = now_time
                        data = pd.read_excel(self.fileName)
                        data_time = time.strftime("%Y%m%d %H:%M:%S", time.localtime(t.to_sec()))
                        num = data.shape[0]
                        data.loc[num, 'NO'] = num + 1
                        data.loc[num, 'Date'] = data_time.split(' ')[0]
                        data.loc[num, 'Time'] = data_time.split(' ')[1]
                        data.loc[num, 'BagPath'] = bagPath
                        data.loc[num, 'Problem'] = 'CUTIN场景'
                        data.loc[num, 'Distance'] = obstacle_in_path
                        data.loc[num, 'Velocity'] = int(linear_velocity * 3.6)
                        # data.loc[num, 'TTC'] = round(TTC, 2)
                        data.to_excel(self.fileName, index=False, engine='openpyxl')
                if cut_in_and_out == 0 and self.is_active is True:
                    self.is_active = False


@utils.register('车道线质量差', 'vehicle')
@singleton
class AcceleratedFilter(object):
    """
    车道线质量较差场景筛选
    """

    def __init__(self, fileName):
        self.fileName = fileName
        self.topicsList = ['/planning/vehicle_monitor']
        self.is_active = False
        self.last_time = 0

    def __call__(self, bagData, bagPath):
        for topic, msg, t in bagData.read_messages(topics=self.topicsList):
            if topic == '/planning/vehicle_monitor':
                try:
                    lane_quality = msg.lane_state.fused_lane_array.left_lane.quality
                    now_time = t.to_sec()
                except Exception as E:
                    utils.logger.error(E)
                    break

                if lane_quality < 3 and self.is_active is False:
                    self.is_active = True

                    if now_time - self.last_time > 120:
                        self.last_time = now_time
                        data = pd.read_excel(self.fileName)
                        data_time = time.strftime("%Y%m%d %H:%M:%S", time.localtime(t.to_sec()))
                        num = data.shape[0]
                        data.loc[num, 'NO'] = num + 1
                        data.loc[num, 'Date'] = data_time.split(' ')[0]
                        data.loc[num, 'Time'] = data_time.split(' ')[1]
                        data.loc[num, 'BagPath'] = bagPath
                        data.loc[num, 'Problem'] = '车道线质量差'
                        data.to_excel(self.fileName, index=False, engine='openpyxl')

                if lane_quality >= 3 and self.is_active is True:
                    self.is_active = False


@utils.register('重加速场景', 'vehicle')
@singleton
class AcceleratedFilter(object):
    """
    重加速场景筛选
    """

    def __init__(self, fileName):
        self.fileName = fileName
        self.topicsList = ['/planning/vehicle_monitor']
        self.is_active = False
        self.last_time = 0

    def __call__(self, bagData, bagPath):
        for topic, msg, t in bagData.read_messages(topics=self.topicsList):
            if topic == '/planning/vehicle_monitor':
                try:
                    linear_acceleration = msg.ego_car_state.linear_acceleration
                    drive_mode = msg.ego_car_state.drive_mode
                    obstacle_distance = msg.obstacle_state.obstacle_in_path.position.x
                    linear_velocity = msg.ego_car_state.linear_velocity
                    TTC = msg.obstacle_state.obstacle_in_path.ttc
                    now_time = t.to_sec()
                except Exception as E:
                    utils.logger.error(E)
                    break

                if abs(linear_acceleration) > 3 and self.is_active is False and drive_mode != 0:
                    self.is_active = True
                    if now_time - self.last_time >= 60:
                        self.last_time = now_time
                        data = pd.read_excel(self.fileName)
                        data_time = time.strftime("%Y%m%d %H:%M:%S", time.localtime(t.to_sec()))
                        num = data.shape[0]
                        data.loc[num, 'NO'] = num + 1
                        data.loc[num, 'Date'] = data_time.split(' ')[0]
                        data.loc[num, 'Time'] = data_time.split(' ')[1]
                        data.loc[num, 'BagPath'] = bagPath
                        data.loc[num, 'Problem'] = '重加速度'
                        data.loc[num, 'Distance'] = obstacle_distance
                        data.loc[num, 'Velocity'] = int(linear_velocity * 3.6)
                        data.loc[num, 'TTC'] = round(TTC, 2)
                        data.to_excel(self.fileName, index=False, engine='openpyxl')

                if abs(linear_acceleration) <= 1 and self.is_active is True:
                    self.is_active = False


@utils.register('大曲率弯道', 'vehicle')
@singleton
class AcceleratedFilter(object):
    """
    弯道场景筛选
    """

    def __init__(self, fileName):
        self.fileName = fileName
        self.topicsList = ['/planning/vehicle_monitor']
        self.is_active = False
        self.last_time = 0

    def __call__(self, bagData, bagPath):
        for topic, msg, t in bagData.read_messages(topics=self.topicsList):
            if topic == '/planning/vehicle_monitor':
                try:
                    lane_quality = msg.lane_state.fused_lane_array.left_lane.quality
                    lane_curv = msg.lane_state.fused_lane_array.left_lane.curvature_parameter_c2
                    now_time = t.to_sec()
                except Exception as E:
                    utils.logger.error(E)
                    break
                if lane_quality >= 2 and abs(lane_curv) > 0.015 and self.is_active is False:
                    self.is_active = True
                    if now_time - self.last_time > 120:
                        self.last_time = now_time
                        data = pd.read_excel(self.fileName)
                        data_time = time.strftime("%Y%m%d %H:%M:%S", time.localtime(t.to_sec()))
                        num = data.shape[0]
                        data.loc[num, 'NO'] = num + 1
                        data.loc[num, 'Date'] = data_time.split(' ')[0]
                        data.loc[num, 'Time'] = data_time.split(' ')[1]
                        data.loc[num, 'BagPath'] = bagPath
                        data.loc[num, 'Problem'] = '急弯'
                        data.to_excel(self.fileName, index=False, engine='openpyxl')

                if lane_curv < 0.001 and self.is_active is True:
                    self.is_active = False


@utils.register('距离前车过近', 'vehicle')
@singleton
class DangerDistanceFilter(object):
    '''
    危险驾驶，距离前车过近
    '''

    def __init__(self, fileName):
        self.fileName = fileName
        self.topicsList = ['/planning/vehicle_monitor']
        self.is_active = False
        self.last_time = 0

    def __call__(self, bagData, bagPath):
        for topic, msg, t in bagData.read_messages(topics=self.topicsList):
            if topic == '/planning/vehicle_monitor':
                try:
                    obstacle_in_path = msg.obstacle_state.obstacle_in_path.position.x
                    drive_mode = msg.ego_car_state.drive_mode
                    cut_in_and_out = msg.obstacle_state.obstacle_in_path.cut_in_and_out
                    linear_velocity = msg.ego_car_state.linear_velocity
                    TTC = msg.obstacle_state.obstacle_in_path.ttc
                    now_time = t.to_sec()
                except Exception as E:
                    utils.logger.error(E)
                    break

                if cut_in_and_out == 0 and drive_mode != 0 and self.is_active is False and obstacle_in_path <= 10:
                    self.is_active = True
                    if now_time - self.last_time > 60:
                        self.last_time = now_time
                        data = pd.read_excel(self.fileName)
                        data_time = time.strftime("%Y%m%d %H:%M:%S", time.localtime(t.to_sec()))
                        num = data.shape[0]
                        data.loc[num, 'NO'] = num + 1
                        data.loc[num, 'Date'] = data_time.split(' ')[0]
                        data.loc[num, 'Time'] = data_time.split(' ')[1]
                        data.loc[num, 'BagPath'] = bagPath
                        data.loc[num, 'Problem'] = '距前车过近'
                        data.loc[num, 'Distance'] = obstacle_in_path
                        data.loc[num, 'Velocity'] = int(linear_velocity * 3.6)
                        data.loc[num, 'TTC'] = round(TTC, 2)
                        data.to_excel(self.fileName, index=False, engine='openpyxl')

                if obstacle_in_path >= 20 and self.is_active is True:
                    self.is_active = False


@utils.register('车道保持不居中', 'vehicle')
@singleton
class LaneDeviateFilter(object):
    '''
    车道保持不居中
    '''

    def __init__(self, fileName):
        self.fileName = fileName
        self.topicsList = ['/planning/vehicle_monitor']
        self.is_active = False
        self.last_time = 0

    def __call__(self, bagData, bagPath):

        for topic, msg, t in bagData.read_messages(topics=self.topicsList):
            if topic == '/planning/vehicle_monitor':
                try:
                    lane_quality = msg.lane_state.fused_lane_array.left_lane.quality
                    drive_mode = msg.ego_car_state.drive_mode
                    lane_position = msg.lane_state.fused_lane_array.center_lane.position_parameter_c0
                    now_time = t.to_sec()

                except Exception as E:
                    utils.logger.error(E)
                    break

                if lane_quality >= 3 and drive_mode != 0 and self.is_active is False and abs(lane_position) > 0.5:
                    self.is_active = True

                    if now_time - self.last_time > 120:
                        self.last_time = now_time
                        data = pd.read_excel(self.fileName)
                        data_time = time.strftime("%Y%m%d %H:%M:%S", time.localtime(t.to_sec()))
                        num = data.shape[0]
                        data.loc[num, 'NO'] = num + 1
                        data.loc[num, 'Date'] = data_time.split(' ')[0]
                        data.loc[num, 'Time'] = data_time.split(' ')[1]
                        data.loc[num, 'BagPath'] = bagPath
                        data.loc[num, 'type'] = '车道保持不居中'
                        data.to_excel(self.fileName, index=False, engine='openpyxl')

                if lane_position <= 0.1 and self.is_active is True:
                    self.is_active = False

# @utils.register('测距误差统计', 'vehicle')
# def cipv_distance_front(file_path, fileName):
#     CIPV_DISTANCE_TOLERANCE = {'result': {20: [], 40: [], 60: [], 80: [], 100: [], 120: [], 200: []}}
#     topicsList = ['/fusion/radar_process/processed_radar_tracks',
#                   '/fusion/tracked_obstacles', '/input/perception/obstacle_list', '/perception/obstacle_list']
#     cipv_id = 0
#     radar_distance = None
#     for topic, msg, t, bagPath, bag_count in utils.get_bag_msg(file_path, topicsList):
#         if topic == '/input/perception/obstacle_list' or topic == '/perception/obstacle_list':
#             cipv_id = msg.cipv_id
#             perception_tracks = msg.tracks
#             for i in range(len(perception_tracks)):
#                 if perception_tracks[i].id == cipv_id:
#                     perception_distance = perception_tracks[i].position.x
#         if topic == '/fusion/radar_process/processed_radar_tracks':
#             radar_tracks = msg.tracks
#             if radar_tracks:
#                 radar_distance = {}
#                 for i in range(len(radar_tracks)):
#                     radar_distance[radar_tracks[i].id] = radar_tracks[i].position.x
#         if topic == '/fusion/tracked_obstacles':
#             fusion_tracks = msg.tracks
#             if fusion_tracks and cipv_id != 0 and radar_distance:
#                 for i in range(len(fusion_tracks)):
#                     if cipv_id == fusion_tracks[i].associate_infos[0].id:
#                         try:
#                             cipv_radar_distance = radar_distance[
#                                 fusion_tracks[i].associate_infos[1].id]
#                             gaper = (cipv_radar_distance - perception_distance - 2.07) / (
#                                     cipv_radar_distance - 2.07)
#                             print(gaper, cipv_radar_distance - 2.07, perception_distance)
#                             if cipv_radar_distance - 2.07 < 20:
#                                 CIPV_DISTANCE_TOLERANCE['result'][20].append(abs(gaper))
#                             elif cipv_radar_distance - 2.07 < 40:
#                                 CIPV_DISTANCE_TOLERANCE['result'][40].append(abs(gaper))
#                             elif cipv_radar_distance - 2.07 < 60:
#                                 CIPV_DISTANCE_TOLERANCE['result'][60].append(abs(gaper))
#                             elif cipv_radar_distance - 2.07 < 80:
#                                 CIPV_DISTANCE_TOLERANCE['result'][80].append(abs(gaper))
#                             elif cipv_radar_distance - 2.07 < 100:
#                                 CIPV_DISTANCE_TOLERANCE['result'][100].append(abs(gaper))
#                             elif cipv_radar_distance - 2.07 < 120:
#                                 CIPV_DISTANCE_TOLERANCE['result'][120].append(abs(gaper))
#                             else:
#                                 CIPV_DISTANCE_TOLERANCE['result'][200].append(abs(gaper))
#                         except:
#                             continue
#     try:
#         print('20:{}'.format(sum(CIPV_DISTANCE_TOLERANCE['result'][20]) / len(CIPV_DISTANCE_TOLERANCE['result'][20])))
#         print('40:{}'.format(sum(CIPV_DISTANCE_TOLERANCE['result'][40]) / len(CIPV_DISTANCE_TOLERANCE['result'][40])))
#         print('60:{}'.format(sum(CIPV_DISTANCE_TOLERANCE['result'][60]) / len(CIPV_DISTANCE_TOLERANCE['result'][60])))
#         print('80:{}'.format(sum(CIPV_DISTANCE_TOLERANCE['result'][80]) / len(CIPV_DISTANCE_TOLERANCE['result'][80])))
#         print(
#             '100:{}'.format(sum(CIPV_DISTANCE_TOLERANCE['result'][100]) / len(CIPV_DISTANCE_TOLERANCE['result'][100])))
#         print(
#             '120:{}'.format(sum(CIPV_DISTANCE_TOLERANCE['result'][120]) / len(CIPV_DISTANCE_TOLERANCE['result'][120])))
#         print(
#             '200:{}'.format(sum(CIPV_DISTANCE_TOLERANCE['result'][200]) / len(CIPV_DISTANCE_TOLERANCE['result'][200])))
#     except:
#         pass
#
#
# @utils.register('测速误差统计', 'vehicle')
# def cipv_velocity(file_path, fileName):
#     CIPV_VELOCITY_TOLERANCE = {'result': {20: [], 40: [], 60: [], 80: [], 100: [], 120: [], 200: []}}
#     topicsList = ['/fusion/radar_process/processed_radar_tracks',
#                   '/fusion/tracked_obstacles', '/input/perception/obstacle_list', '/perception/obstacle_list']
#     radar_velocity = None
#     cipv_id = 0
#     for topic, msg, t, bagPath, bag_count in utils.get_bag_msg(file_path, topicsList):
#         if topic == '/input/perception/obstacle_list' or topic == '/perception/obstacle_list':
#             cipv_id = msg.cipv_id
#             perception_tracks = msg.tracks
#             for i in range(len(perception_tracks)):
#                 if perception_tracks[i].id == cipv_id:
#                     perce_velocity = perception_tracks[i].velocity.x
#         if topic == '/fusion/radar_process/processed_radar_tracks':
#             radar_tracks = msg.tracks
#             if radar_tracks:
#                 radar_velocity = {}
#                 radar_distance = {}
#                 for i in range(len(radar_tracks)):
#                     radar_velocity[radar_tracks[i].id] = radar_tracks[i].velocity.x
#                     radar_distance[radar_tracks[i].id] = radar_tracks[i].position.x
#         if topic == '/fusion/tracked_obstacles':
#             fusion_tracks = msg.tracks
#             if fusion_tracks and cipv_id != 0 and radar_velocity:
#                 for i in range(len(fusion_tracks)):
#                     if cipv_id == fusion_tracks[i].associate_infos[0].id:
#
#                         try:
#                             cipv_radar_velocity = radar_velocity[
#                                 fusion_tracks[i].associate_infos[1].id]
#                             cipv_radar_distance = radar_distance[
#                                 fusion_tracks[i].associate_infos[1].id]
#                             gaper = (cipv_radar_velocity - perce_velocity)
#                             if cipv_radar_distance - 2.07 < 20:
#                                 CIPV_VELOCITY_TOLERANCE['result'][20].append(abs(gaper))
#                             elif cipv_radar_distance - 2.07 < 40:
#                                 CIPV_VELOCITY_TOLERANCE['result'][40].append(abs(gaper))
#                             elif cipv_radar_distance - 2.07 < 60:
#                                 CIPV_VELOCITY_TOLERANCE['result'][60].append(abs(gaper))
#                             elif cipv_radar_distance - 2.07 < 80:
#                                 CIPV_VELOCITY_TOLERANCE['result'][80].append(abs(gaper))
#                             elif cipv_radar_distance - 2.07 < 100:
#                                 CIPV_VELOCITY_TOLERANCE['result'][100].append(abs(gaper))
#                             elif cipv_radar_distance - 2.07 < 120:
#                                 CIPV_VELOCITY_TOLERANCE['result'][120].append(abs(gaper))
#                             else:
#                                 CIPV_VELOCITY_TOLERANCE['result'][200].append(abs(gaper))
#                         except:
#                             continue
#     try:
#         print('20:{}'.format(sum(CIPV_VELOCITY_TOLERANCE['result'][20]) / len(CIPV_VELOCITY_TOLERANCE['result'][20])))
#         print('40:{}'.format(sum(CIPV_VELOCITY_TOLERANCE['result'][40]) / len(CIPV_VELOCITY_TOLERANCE['result'][40])))
#         print('60:{}'.format(sum(CIPV_VELOCITY_TOLERANCE['result'][60]) / len(CIPV_VELOCITY_TOLERANCE['result'][60])))
#         print('80:{}'.format(sum(CIPV_VELOCITY_TOLERANCE['result'][80]) / len(CIPV_VELOCITY_TOLERANCE['result'][80])))
#         print(
#             '100:{}'.format(sum(CIPV_VELOCITY_TOLERANCE['result'][100]) / len(CIPV_VELOCITY_TOLERANCE['result'][100])))
#         print(
#             '120:{}'.format(sum(CIPV_VELOCITY_TOLERANCE['result'][120]) / len(CIPV_VELOCITY_TOLERANCE['result'][120])))
#         print(
#             '200:{}'.format(sum(CIPV_VELOCITY_TOLERANCE['result'][200]) / len(CIPV_VELOCITY_TOLERANCE['result'][200])))
#     except:
#         pass
#
#

#
