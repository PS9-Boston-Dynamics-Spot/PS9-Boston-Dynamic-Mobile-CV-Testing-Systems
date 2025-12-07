'''
Copyright (c) 2017 Intel Corporation.
Licensed under the MIT license. See LICENSE file in the project root for full license information.
'''

import cv2
import numpy as np
#import paho.mqtt.client as mqtt
import time

def avg_circles(circles, b):
    avg_x=0
    avg_y=0
    avg_r=0
    for i in range(b): 
        #optional - average for multiple circles (can happen when a gauge is at a slight angle)
        avg_x = avg_x + circles[0][i][0]
        avg_y = avg_y + circles[0][i][1]
        avg_r = avg_r + circles[0][i][2]
    avg_x = int(avg_x/(b))
    avg_y = int(avg_y/(b))
    avg_r = int(avg_r/(b))
    return avg_x, avg_y, avg_r

def dist_2_pts(x1, y1, x2, y2):
    #print(np.sqrt((x2-x1)^2+(y2-y1)^2))
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
import cv2

def find_gauge_center(gray):
    # 1. Glätten
    blur = cv2.GaussianBlur(gray, (7, 7), 2)

    # 2. Kanten
    edges = cv2.Canny(blur, 40, 120)

    # 3. Konturen
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    # 4. Größte Kontur
    cnt = max(contours, key=cv2.contourArea)
    if len(cnt) < 5:
        return None

    # 5. Ellipse fitten
    ellipse = cv2.fitEllipse(cnt)
    (MA, ma) = ellipse[1]

    # 6. Mittelpunkt via Moments
    M = cv2.moments(cnt)
    if M['m00'] == 0:
        return None
    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00'])

    # 7. Radius bestimmen
    # a) Mittelwert der Ellipsenachsen
    radius_ellipse = (MA + ma) / 4

    # b) minEnclosingCircle als Alternative
    (x_circle, y_circle), radius_circle = cv2.minEnclosingCircle(cnt)

    # Wir kombinieren beide Schätzungen (optional: Mittelwert)
    radius = int((radius_ellipse + radius_circle) / 2)

    return cx, cy, radius, ellipse





def calibrate_gauge(gauge_number, file_type):

    img = cv2.imread(f"gauge-{gauge_number}.{file_type}")
    if img is None:
        raise ValueError("Bild konnte nicht geladen werden")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    result = find_gauge_center(gray)
    if result is None:
        raise ValueError("Mittelpunkt konnte nicht bestimmt werden")

    x, y, r, ellipse = result

    # Kreis einzeichnen
    cv2.circle(img, (x, y), r, (0, 0, 255), 3, cv2.LINE_AA)
    cv2.circle(img, (x, y), 3, (0, 255, 0), -1, cv2.LINE_AA)

    # Kalibrier-Linien zeichnen
    separation = 3.0
    angles = np.arange(0, 360, separation)
    rad = np.deg2rad(angles)

    p1 = np.column_stack((x + 0.9*r*np.cos(rad),
                          y + 0.9*r*np.sin(rad)))

    p2 = np.column_stack((x + 1.0*r*np.cos(rad),
                          y + 1.0*r*np.sin(rad)))

    label_rad = np.deg2rad(angles + 90)
    p_text = np.column_stack((x + 1.2*r*np.cos(label_rad),
                              y + 1.2*r*np.sin(label_rad)))

    for i, angle in enumerate(angles):
        cv2.line(img,
                 (int(p1[i,0]), int(p1[i,1])),
                 (int(p2[i,0]), int(p2[i,1])),
                 (0,255,0), 2)
        cv2.putText(img, str(int(angle)),
                    (int(p_text[i,0]), int(p_text[i,1])),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.35, (0,0,0), 1, cv2.LINE_AA)

    # Speichern
    cv2.imwrite(f"gauge-{gauge_number}-calibration.{file_type}", img)

    # Debug: feste Werte
    min_angle = 45
    max_angle = 310
    min_value = 0
    max_value = 10
    units = "bar"

    return min_angle, max_angle, min_value, max_value, units, x, y, r


def get_current_value(img, min_angle, max_angle, min_value, max_value, x, y, r, gauge_number, file_type):

    import cv2
    import numpy as np

    def dist_2_pts(x1, y1, x2, y2):
        return np.hypot(x2-x1, y2-y1)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5,5), 0)

    edges = cv2.Canny(gray, 50, 150)
    cv2.imwrite(f'gauge-{gauge_number}-edges.{file_type}', edges)

    # Hough Lines
    lines = cv2.HoughLinesP(edges, rho=2, theta=np.pi/180*2, threshold=90,
                            minLineLength=5, maxLineGap=10)

    if lines is None:
        print("No lines detected")
        return 0

    # Linien nach Abstand filtern
    final_lines = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        d1 = dist_2_pts(x, y, x1, y1)
        d2 = dist_2_pts(x, y, x2, y2)
        if d1 > d2:
            d1, d2 = d2, d1
        if 0.05*r < d1 < 0.3*r and 0.5*r < d2 < 1.05*r:
            final_lines.append([x1, y1, x2, y2])

    if len(final_lines) == 0:
        print("Keine Linien im Radiusbereich gefunden")
        return 0

    # Längste Linie auswählen
    best_line = max(final_lines, key=lambda l: dist_2_pts(l[0], l[1], l[2], l[3]))
    # Spitze der Linie wählen
    if dist_2_pts(x, y, best_line[0], best_line[1]) > dist_2_pts(x, y, best_line[2], best_line[3]):
        tip = (best_line[0], best_line[1])
    else:
        tip = (best_line[2], best_line[3])

    # Winkel vom Zentrum zur Spitze
    dx = tip[0] - x
    dy = tip[1] - y
    angle_rad = np.arctan2(dy, dx)
    gauge_angle = (np.rad2deg(angle_rad) - 90) % 360
    print(f"Debug: gauge_angle = {gauge_angle:.2f}°")

    # Linie einzeichnen
    cv2.line(img, (x, y), tip, (0, 255, 0), 2)
    cv2.circle(img, tip, 3, (0,0,255), -1)
    cv2.imwrite(f'gauge-{gauge_number}-lines-final-debug.{file_type}', img)

    # Wert berechnen
    old_range = float(max_angle) - float(min_angle)
    new_range = float(max_value) - float(min_value)

    if gauge_angle < float(min_angle):
        gauge_angle += 360

    new_value = ((gauge_angle - float(min_angle)) / old_range) * new_range + float(min_value)
    print(f"Debug: gauge_value = {new_value:.2f}")
    return new_value



def main():
    gauge_number = 5
    file_type='jpg'
    # name the calibration image of your gauge 'gauge-#.jpg', for example 'gauge-5.jpg'.  It's written this way so you can easily try multiple images
    min_angle, max_angle, min_value, max_value, units, x, y, r = calibrate_gauge(gauge_number, file_type)

    #feed an image (or frame) to get the current value, based on the calibration, by default uses same image as calibration
    img = cv2.imread('gauge-%s.%s' % (gauge_number, file_type))
    val = get_current_value(img, min_angle, max_angle, min_value, max_value, x, y, r, gauge_number, file_type)
    print("Current reading: %s %s" %(val, units))

if __name__=='__main__':
    main()