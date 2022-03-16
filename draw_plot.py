# -*- coding: utf-8 -*-

import rosbag
import matplotlib.pyplot as plt


def draw_fcw_plot(bag_path, save_path):
    plt.figure(figsize=(13, 13))

    ax1 = plt.subplot(334)
    ax1.set_title('fcw_warn1_request')
    ax2 = plt.subplot(337)
    ax2.set_title('fcw_warn2_request')
    ax3 = plt.subplot(331)
    ax3.set_title('fcw_status')
    ax4 = plt.subplot(333)
    ax4.set_title('fcw_switch')
    ax5 = plt.subplot(336)
    ax5.set_title('fcw_sensitivity_level')
    ax6 = plt.subplot(338)
    ax6.set_title('position.x')
    ax7 = plt.subplot(335)
    ax7.set_title('abs_velocity.x')
    ax8 = plt.subplot(332)
    ax8.set_title('linear_velocity')

    ploys_x1, ploys_y1 = [], []
    ploys_x2, ploys_y2 = [], []
    ploys_x3, ploys_y3 = [], []
    ploys_x4, ploys_y4 = [], []
    ploys_x5, ploys_y5 = [], []
    ploys_x6, ploys_y6 = [], []
    ploys_x7, ploys_y7 = [], []
    ploys_x8, ploys_y8 = [], []

    bag_data = rosbag.Bag(bag_path)
    topic_list = ['/fcw/fcw_command', '/fcw/fcw_set', '/fcw/fused_obstacle_frame', '/sensing/ego_car_state']
    start_time = bag_data.get_start_time()
    for topic, msg, t in bag_data.read_messages(topic_list):
        ploy_x = float(t.to_sec() - start_time)

        if topic == '/fcw/fcw_command':
            ploys_x1.append(ploy_x)
            ploys_y1.append(msg.fcw_warn1_request)

            ploys_x2.append(ploy_x)
            ploys_y2.append(msg.fcw_warn2_request)

            ploys_x3.append(ploy_x)
            ploys_y3.append(msg.fcw_status)

        if topic == '/fcw/fcw_set':
            ploys_x4.append(ploy_x)
            ploys_y4.append(msg.fcw_switch)

            ploys_x5.append(ploy_x)
            ploys_y5.append(msg.fcw_sensitivity_level)

        if topic == '/fcw/fused_obstacle_frame':
            ploys_x6.append(ploy_x)
            ploys_y6.append(msg.position.x)

            ploys_x7.append(ploy_x)
            ploys_y7.append(msg.abs_velocity.x)

        if topic == '/sensing/ego_car_state':
            ploys_x8.append(ploy_x)
            ploys_y8.append(msg.linear_velocity)

    ax1.plot(ploys_x1, ploys_y1, color="r")
    ax2.plot(ploys_x2, ploys_y2, color="r")
    ax3.plot(ploys_x3, ploys_y3, color="r")
    ax4.plot(ploys_x4, ploys_y4, color="r")
    ax5.plot(ploys_x5, ploys_y5, color="r")
    ax6.plot(ploys_x6, ploys_y6, color="r")
    ax7.plot(ploys_x7, ploys_y7, color="r")
    ax8.plot(ploys_x8, ploys_y8, color="r")

    save_path = save_path.replace('.csv', '.png')
    plt.savefig(save_path, dpi=200, format='png')

