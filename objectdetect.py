import numpy as np
import streamlit as st
import cv2 as cv
import tempfile
import os
from streamlit_player import st_player
import vehicles
import time

dir_name = 'E:\GUI\image'

# Set params
number = st.text_input("Input your student number:")

"Wanna use a folder to save image?"

col1, col2 = st.beta_columns(2)
button1 = col1.button('Yes', help='This will check if the folder is available for use')
button2 = col2.button('No', help='Skip this step')

if button1:
    if os.path.exists(dir_name) and os.path.isdir(dir_name):
        if not os.listdir(dir_name):
            "Directory is empty"
        else:
            "Directory is not empty"
    else:
        "Given directory does not exist"
if button2:
    "Folder ignored successfully"

"Got a hosted video source, such as Youtube?"

video_name = st.text_input('Pass the link here')

if video_name:
    st_player(video_name)

f = st.file_uploader("Upload file here:")

if f != None:

    # if number:
    #     st.write(number)
    # "Your number is:", number
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(f.read())

    cnt_up = 0
    cnt_down = 0

    vf = cv.VideoCapture(tfile.name)

    #Get width and height of the video
    width = vf.get(3)
    height = vf.get(4)
    st.write("Width:", width)
    st.write("Height:", height)
    frame_area = width * height
    area_TH = frame_area / 400

    #Testing change position
    line_up = int(3 * (height / 5))
    line_down = int(2 * (height / 5))
    st.write("Line up:", line_up)
    st.write("Line down:", line_down)

    up_limit = int(1 * (height / 5))
    down_limit = int(4 * (height / 5))
    st.write("Up limit:", up_limit)
    st.write("Down limit:", down_limit)
    line_down_color = (255, 0, 0)
    line_up_color = (225, 0, 225)
    pt1 = [0, line_down]
    pt2 = [width, line_up]
    pts_L1 = np.array([pt1, pt2], np.int32)
    pts_L1 = pts_L1.reshape((-1, 1, 2))
    pt3 = [0, line_up * 1.12]
    pt4 = [width, line_up * 1.12]

    pts_L2 = np.array([pt3, pt4], np.int32)
    pts_L2 = pts_L2.reshape((-1, 1, 2))

    pt5 = [0, down_limit]
    pt6 = [width, down_limit]
    pts_L3 = np.array([pt5, pt6], np.int32)
    pts_L3 = pts_L3.reshape((-1, 1, 2))
    pt7 = [0, up_limit]
    pt8 = [width, up_limit]
    pts_L4 = np.array([pt7, pt8], np.int32)
    pts_L4 = pts_L4.reshape((-1, 1, 2))

    # Background Subtractor
    fgbg = cv.createBackgroundSubtractorMOG2(detectShadows=True)

    # Kernals
    kernalOp = np.ones((3, 3), np.uint8)
    kernalOp2 = np.ones((5, 5), np.uint8)
    kernalCl = np.ones((11, 11), np.uint8)

    font = cv.FONT_HERSHEY_SIMPLEX
    cars = []
    max_p_age = 5
    pid = 1

    stframe = st.empty()

    while vf.isOpened():
        ret, frame = vf.read()
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        #gray = cv.cvtColor(frame,  cv.COLOR_BGR2RGBA)
        stframe.image(frame, channels='BGR')

        for i in cars:
            i.age_one()
        fgmask = fgbg.apply(frame)
        fgmask2 = fgbg.apply(frame)

        if ret == True:

            # Binarization
            ret, imBin = cv.threshold(fgmask, 200, 255, cv.THRESH_BINARY)
            ret, imBin2 = cv.threshold(fgmask2, 200, 255, cv.THRESH_BINARY)
            # OPening i.e First Erode the dilate
            mask = cv.morphologyEx(imBin, cv.MORPH_OPEN, kernalOp)
            mask2 = cv.morphologyEx(imBin2, cv.MORPH_CLOSE, kernalOp)

            # Closing i.e First Dilate then Erode
            mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernalCl)
            mask2 = cv.morphologyEx(mask2, cv.MORPH_CLOSE, kernalCl)

            # Find Contours
            countours0, hierarchy = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
            for cnt in countours0:
                area = cv.contourArea(cnt)
                print("this is area:" + str(area))
                if area > area_TH:
                    ####Tracking######
                    m = cv.moments(cnt)
                    cx = int(m['m10'] / m['m00'])
                    cy = int(m['m01'] / m['m00'])
                    x, y, w, h = cv.boundingRect(cnt)

                    new = True
                    if cy in range(up_limit, down_limit):
                        for i in cars:
                            if abs(x - i.getX()) <= w and abs(y - i.getY()) <= h:
                                new = False
                                i.updateCoords(cx, cy)

                                if i.going_UP(line_down, line_up) == True:
                                    cnt_up += 1
                                    print("ID:", i.getId(), 'crossed going up at', time.strftime("%c"))
                                elif i.going_DOWN(line_down, line_up) == True:
                                    cnt_down += 1
                                    print("ID:", i.getId(), 'crossed going up at', time.strftime("%c"))
                                break
                            if i.getState() == '1':
                                if i.getDir() == 'down' and i.getY() > down_limit:
                                    i.setDone()
                                elif i.getDir() == 'up' and i.getY() < up_limit:
                                    i.setDone()
                            if i.timedOut():
                                index = cars.index(i)
                                cars.pop(index)
                                del i

                        if new == True:  # If nothing is detected,create new
                            p = vehicles.Car(pid, cx, cy, max_p_age)
                            cars.append(p)
                            pid += 1

                    cv.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                    img = cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            for i in cars:
                cv.putText(frame, str(i.getId()), (i.getX(), i.getY()), font, 0.3, i.getRGB(), 1, cv.LINE_AA)

            str_up = 'UP: ' + str(cnt_up)
            str_down = 'DOWN: ' + str(cnt_down)
            frame = cv.polylines(frame, [pts_L1], False, line_down_color, thickness=2)
            frame = cv.polylines(frame, [pts_L2], False, line_up_color, thickness=2)
            frame = cv.polylines(frame, [pts_L3], False, (255, 255, 255), thickness=1)
            frame = cv.polylines(frame, [pts_L4], False, (255, 255, 255), thickness=1)
            cv.putText(frame, str_up, (10, 40), font, 0.5, (255, 255, 255), 2, cv.LINE_AA)
            cv.putText(frame, str_up, (10, 40), font, 0.5, (0, 0, 255), 1, cv.LINE_AA)
            cv.putText(frame, str_down, (10, 90), font, 0.5, (255, 255, 255), 2, cv.LINE_AA)
            cv.putText(frame, str_down, (10, 90), font, 0.5, (255, 0, 0), 1, cv.LINE_AA)
            cv.imshow('Frame', frame)