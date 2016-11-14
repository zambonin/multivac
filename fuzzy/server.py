import socket
import numpy as np
import skfuzzy as fuzz
import time
import re
import matplotlib.pyplot as plt
import math

HOST = '127.0.0.1'
PORT = 4321

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
server = s.makefile()

# while True:
# 	s.send("r\r\n")
# 	strg = server.readline()
# 	move = 0.2 + (it/10)
# 	s.send(str(move) + '\n')


# def adjust_levels(min, max, mid_offset_percent, clip_max=False):
# 	if clip_max:
# 		max = max*0.6
# 	mid_min = (max+min)/2 - max * mid_offset_percent
# 	mid_max = (max+min)/2 + max * mid_offset_percent
# 	lo = [min, min, mid_min]
# 	md = [min, mid_min, mid_max]
# 	hi = [mid_min, mid_max, max]
#
# 	return [lo, md, hi]

while True:

	"""
	Rules:
	1. IF l_dist_sensor IS small THEN l_motor_power IS small
	2. IF l_dist_sensor IS medium THEN l_motor_power IS medium
	3. IF l_dist_sensor IS high THEN l_motor_power IS high
	4. IF r_dist_sensor IS small THEN r_motor_power IS small
	5. IF r_dist_sensor IS medium THEN r_motor_power IS medium
	6. IF r_dist_sensor IS high THEN r_motor_power IS high
	"""

	# Input
	s.send("r\r\n")
	dist_sensor_str = server.readline()
	coord = re.split(r'\t+', dist_sensor_str.rstrip('\t'))
	x = float(coord[0])
	y = float(coord[1])
	angle = float(coord[2])
	rot = math.floor(((angle + 90)%360.0) - 180.0);
	if (rot > 30):
		rot = 30
	if (rot < -30):
		rot = -30
	print(x)
	print(y)
	print("Angle: ", angle)
	print(rot)
	#
	# if l_dist_sensor_str == 'Infinity\n':
	# 	l_dist_sensor = -1.5
	# elif 'Infinity' in l_dist_sensor_str:
	# 	l_dist_sensor = -1.5
	# else:
	# 	l_dist_sensor = float(l_dist_sensor_str)
	#
	# if r_dist_sensor_str == 'Infinity\n':
	# 	r_dist_sensor = -1.5
	# if 'Infinity' in r_dist_sensor_str:
	# 	r_dist_sensor = -1.5
	# else:
	# 	r_dist_sensor = float(r_dist_sensor_str)

	# Generate universe variables
	x_dist = np.arange(0, 1.1, 0.1)
	y_dist = np.arange(0, 1.1, 0.1)
	rot_dist = np.arange(-31, 31, 1)

	intensity = np.arange(-1, 1, 0.1)
	# r_power = np.arange(-1, 1, 0.25)

	# Generate fuzzy membership functions
	# levels = adjust_levels(-2, 2, 0.5)
	# l_dist_lo = fuzz.trimf(r_dist, levels[2])

	# levels = adjust_levels(-2, 3, 0.25, True)
	# l_power_lo = fuzz.trimf(l_power, levels[0])
	# l_power_md = fuzz.trimf(l_power, levels[1])
	# l_power_hi = fuzz.trimf(l_power, levels[2])
	#
	# r_power_lo = fuzz.trimf(r_power, levels[0])
	# r_power_md = fuzz.trimf(r_power, levels[1])
	# r_power_hi = fuzz.trimf(r_power, levels[2])

	x_lo = fuzz.trimf(x_dist, [0, 0, 0.3])
	x_md = fuzz.trimf(x_dist, [0.2, 0.5, 0.8])
	x_hi = fuzz.trimf(x_dist, [0.6, 1, 1])

	y_lo = fuzz.trimf(y_dist, [0, 0, 0.5])
	y_hi = fuzz.trimf(y_dist, [0.2, 0.5, 0.8])
	

	rot_straight = fuzz.trimf(rot_dist, [-5, 0, 5])
	rot_left = fuzz.trimf(rot_dist, [-20, -10, 0])
	rot_right = fuzz.trimf(rot_dist, [0, 10, 20])
	rot_veryRight = fuzz.trimf(rot_dist, [10, 30, 30])
	rot_veryLeft = fuzz.trimf(rot_dist, [-30, -30, -10])

	intensity_lower = fuzz.trimf(intensity, [-1, -1, -0.5])
	intensity_low = fuzz.trimf(intensity, [-0.8, -0.3, 0])
	intensity_medium = fuzz.trimf(intensity, [-0.5, 0, 0.5])
	intensity_none = fuzz.trimf(intensity, [-0.1, 0, 0.1])
	intensity_high = fuzz.trimf(intensity, [0, 0.3, 0.8])
	intensity_higher = fuzz.trimf(intensity, [0.5, 1, 1])


	# plot
	fig, (ax0, ax1, ax2, ax3) = plt.subplots(nrows=4, figsize=(8, 9))

	ax0.plot(x_dist, x_lo, 'b', linewidth=1.5, label='Left')
	ax0.plot(x_dist, x_md, 'g', linewidth=1.5, label='Center')
	ax0.plot(x_dist, x_hi, 'r', linewidth=1.5, label='Right')
	ax0.set_title('X Distance')
	ax0.legend()

	ax1.plot(y_dist, y_lo, 'b', linewidth=1.5, label='Far')
	# ax1.plot(y_dist, y_md, 'g', linewidth=1.5, label='Center')
	ax1.plot(y_dist, y_hi, 'r', linewidth=1.5, label='Near')
	ax1.set_title('Y Distance')
	ax1.legend()

	ax2.plot(rot_dist, rot_veryLeft, 'b', linewidth=1.5, label='veryLeft')
	ax2.plot(rot_dist, rot_left, 'g', linewidth=1.5, label='left')
	ax2.plot(rot_dist, rot_straight, 'r', linewidth=1.5, label='straight')
	ax2.plot(rot_dist, rot_right, 'k', linewidth=1.5, label='right')
	ax2.plot(rot_dist, rot_veryRight, 'y', linewidth=1.5, label='veryRight')
	ax2.set_title('Rotation Power')
	ax2.legend()

	ax3.plot(intensity, intensity_lower, 'g', linewidth=1.5, label='Lower')
	ax3.plot(intensity, intensity_low, 'b', linewidth=1.5, label='Low')
	ax3.plot(intensity, intensity_medium, 'r', linewidth=1.5, label='Medium')
	ax3.plot(intensity, intensity_high, 'k', linewidth=1.5, label='High')
	ax3.plot(intensity, intensity_higher, 'y', linewidth=1.5, label='Higher')
	ax3.set_title('Turn Power')
	ax3.legend()

	# Turn off top/right axes
	for ax in (ax0, ax1, ax2, ax3):
	    ax.spines['top'].set_visible(False)
	    ax.spines['right'].set_visible(False)
	    ax.get_xaxis().tick_bottom()
	    ax.get_yaxis().tick_left()

	plt.tight_layout()
	# plt.show();

	x_level_lo = fuzz.interp_membership(x_dist, x_lo, x)
	x_level_md = fuzz.interp_membership(x_dist, x_md, x)
	x_level_hi = fuzz.interp_membership(x_dist, x_hi, x)

	y_level_lo = fuzz.interp_membership(y_dist, y_lo, y)
	# y_level_md = fuzz.interp_membership(y_dist, y_md, y)
	y_level_hi = fuzz.interp_membership(y_dist, y_hi, y)

	rot_level_veryL = fuzz.interp_membership(rot_dist, rot_veryLeft, rot)
	rot_level_left = fuzz.interp_membership(rot_dist, rot_left, rot)
	rot_level_strg = fuzz.interp_membership(rot_dist, rot_straight, rot)
	rot_level_right = fuzz.interp_membership(rot_dist, rot_right, rot)
	rot_level_veryR = fuzz.interp_membership(rot_dist, rot_veryRight, rot)


	# Rule 1
	# Car is at left, far away with rotation angle turned to left.
	active_rule1 = np.fmin(np.fmin(x_level_lo, y_level_lo), rot_level_left)
	# Car turn to very right.
	intensity_activation1 = np.fmin(active_rule1, intensity_higher)

	# Rule 2
	# Car is at left, far away with rotation angle turned to right.
	active_rule2 = np.fmin(np.fmin(x_level_lo, y_level_lo), rot_level_right)
	# Car turn the minimum possible.
	intensity_activation2 = np.fmin(active_rule2, intensity_higher)

	# Rule 3
	# Car is at left, far away with angle straight.
	active_rule3 = np.fmin(np.fmin(x_level_lo, y_level_lo), rot_level_strg)
	# Car turn to very right(intensity higher)
	intensity_activation3 = np.fmin(active_rule3, intensity_higher)

	# Rule 4
	# Car is at right, far away with angle turned to left.
	active_rule4 = np.fmin(np.fmin(x_level_hi, y_level_lo), rot_level_left)
	# Car turn the minimum possible.
	intensity_activation4 = np.fmin(active_rule4, intensity_none)

	# Rule 5
	# Car is at right, far away with angle turned to right.
	active_rule5 = np.fmin(np.fmin(x_level_hi, y_level_lo), rot_level_right)
	# Car turn very left(intensity lower).
	intensity_activation5 = np.fmin(active_rule5, intensity_lower)

	# Rule 6
	# Car is at right, far away with angle straight.
	active_rule6 = np.fmin(np.fmin(x_level_hi, y_level_lo), rot_level_strg)
	# Car turn to very_left(intensity_lower)
	intensity_activation6 = np.fmin(active_rule6, intensity_lower)

	# Rule 7
	# Car is in the center, far away with left angle.
	active_rule7 = np.fmin(np.fmin(x_level_md, y_level_lo), rot_level_left)
	# Car turn right.
	intensity_activation7 = np.fmin(active_rule7, intensity_high)

	# Rule 8
	# Car is in the center, far away with angle right.
	active_rule8 = np.fmin(np.fmin(x_level_md, y_level_lo), rot_level_right)
	# Car turn left.
	intensity_activation8 = np.fmin(active_rule8, intensity_low)

	# Rule 9
	# Car is in the center and straight.
	active_rule9 = np.fmin(x_level_md, rot_level_strg)
	# Car turn the minimum possible.
	intensity_activation9 = np.fmin(active_rule9, intensity_none)

	# Rule 10
	# Car is left, near and with left angle.
	active_rule10 = np.fmin(np.fmin(x_level_lo, y_level_hi), rot_level_left)
	# Car turn right.
	intensity_activation10 = np.fmin(active_rule10, intensity_high)

	# Rule 11
	# Car is left, near and with right angle.
	active_rule11 = np.fmin(np.fmin(x_level_lo, y_level_hi), rot_level_right)
	# Car turn right.
	intensity_activation11 = np.fmin(active_rule11, intensity_high)

	# Rule 12
	# Car is left, near and with straight angle.
	active_rule12 = np.fmin(np.fmin(x_level_lo, y_level_hi), rot_level_strg)
	# Car turn right.
	intensity_activation12 = np.fmin(active_rule12, intensity_high)

	# Rule 13
	# Car is right, near and with left angle.
	active_rule13 = np.fmin(np.fmin(x_level_hi, y_level_hi), rot_level_left)
	# Car turn left.
	intensity_activation13 = np.fmin(active_rule13, intensity_low)

	# Rule 14
	# Car is right, near and with right angle.
	active_rule14 = np.fmin(np.fmin(x_level_hi, y_level_hi), rot_level_right)
	# Car turn left.
	intensity_activation14 = np.fmin(active_rule14, intensity_low)

	# Rule 15
	# Car is right, near and with straight angle.
	active_rule15 = np.fmin(np.fmin(x_level_hi, y_level_hi), rot_level_strg)
	# Car turn left.
	intensity_activation15 = np.fmin(active_rule15, intensity_low)

	# Rule 16
	# Car is right, near and with left angle.
	active_rule16 = np.fmin(np.fmin(x_level_hi, y_level_hi), rot_level_left)
	# Car turn right.
	intensity_activation16 = np.fmin(active_rule16, intensity_high)

	# Rule 17
	# Car is right, near and with right angle.
	active_rule17 = np.fmin(np.fmin(x_level_hi, y_level_hi), rot_level_right)
	# Car turn left.
	intensity_activation17 = np.fmin(active_rule17, intensity_low)

	# Rule 18
	# Car is left and with very left angle.
	active_rule18 = np.fmin(x_level_lo, rot_level_veryL)
	# Car turn very right.
	intensity_activation18 = np.fmin(active_rule18, intensity_higher)

	# Rule 19
	# Car is left and with very right angle.
	active_rule19 = np.fmin(x_level_lo, rot_level_veryR)
	# Car turn right.
	intensity_activation19 = np.fmin(active_rule19, intensity_higher)

	# Rule 20
	# Car is center and with very right angle.
	active_rule20 = np.fmin(x_level_md, rot_level_veryR)
	# Car turn very_left.
	intensity_activation20 = np.fmin(active_rule20, intensity_lower)

	# Rule 21
	# Car is center and with very left angle.
	active_rule21 = np.fmin(x_level_md, rot_level_veryL)
	# Car turn very_right.
	intensity_activation21 = np.fmin(active_rule21, intensity_higher)

	# Rule 22
	# Car is center and with right angle.
	active_rule22 = np.fmin(x_level_md, rot_level_right)
	# Car turn left.
	intensity_activation22 = np.fmin(active_rule22, intensity_medium)

	# Rule 23
	# Car is right and with very left angle.
	active_rule23 = np.fmin(x_level_hi, rot_level_veryL)
	# Car turn very_left.
	intensity_activation23 = np.fmin(active_rule23, intensity_higher)

	# Rule 24
	# Car is right and with very right angle.
	active_rule24 = np.fmin(x_level_hi, rot_level_veryR)
	# Car turn the very_left.
	intensity_activation24 = np.fmin(active_rule24, intensity_lower)

	# Rule 25
	# Car is center and with left angle.
	active_rule25 = np.fmin(x_level_hi, rot_level_left)
	# Car turn the very right.
	intensity_activation25 = np.fmin(active_rule25, intensity_medium)


	intensity0 = np.zeros_like(intensity)

	aggregated = np.fmax(intensity_activation1,
	                     np.fmax(intensity_activation2,
						 np.fmax(intensity_activation3,
						 np.fmax(intensity_activation4,
						 np.fmax(intensity_activation5,
						 np.fmax(intensity_activation6,
						 np.fmax(intensity_activation7,
						 np.fmax(intensity_activation8,
						 np.fmax(intensity_activation9,
						 np.fmax(intensity_activation10,
						 np.fmax(intensity_activation11,
						 np.fmax(intensity_activation12,
						 np.fmax(intensity_activation13,
						 np.fmax(intensity_activation14,
						 np.fmax(intensity_activation15,
						 np.fmax(intensity_activation16,
						 np.fmax(intensity_activation17,
						 np.fmax(intensity_activation18,
						 np.fmax(intensity_activation19,
						 np.fmax(intensity_activation20,
						 np.fmax(intensity_activation21,
						 np.fmax(intensity_activation22,
						 np.fmax(intensity_activation23,
						 np.fmax(intensity_activation24, intensity_activation25)
						)))))))))))))))))))))))

	intensity_res = fuzz.defuzz(intensity, aggregated, 'centroid')
	print(intensity_res)
		# # Aggregate all three output membership functions together
		# aggregated_l = np.fmax(l_dist_activation_lo, np.fmax(l_dist_activation_md, l_dist_activation_hi))
		# aggregated_r = np.fmax(r_dist_activation_lo, np.fmax(r_dist_activation_md, r_dist_activation_hi))
		#
		#
		# # Calculate defuzzified result
		# l_motor_power = fuzz.defuzz(l_power, aggregated_l, 'centroid')
		# r_motor_power = fuzz.defuzz(r_power, aggregated_r, 'centroid')
		#
		#
		# print('Sensor', l_dist_sensor, r_dist_sensor)
		# print('Motor', l_motor_power, r_motor_power)
		#
	s.sendall((str(intensity_res)+'\r\n').encode())
		# s.sendall((str(r_motor_power)+'\n').encode())

s.close()
