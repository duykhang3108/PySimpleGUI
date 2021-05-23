import PySimpleGUI as sg
import numpy as np
import cv2
import vehicles
import time


def greeting():

    headings = ['Names', 'Student ID']
    header = [[sg.Text('  ')] + [sg.Text(h, size=(14, 1)) for h in headings]]

    input_rows = [[sg.Text("Tran Duy Khang", size=(15, 1)), sg.Text('  '),sg.Text("s3753740", size=(15, 1))]]
    input_rows2 = [[sg.Text("Luu Duy Toan", size=(15, 1)), sg.Text('  '), sg.Text("s3753740", size=(15, 1))]]
    input_rows3 = [[sg.Text("Le Thanh Nguyen", size=(15, 1)), sg.Text('  '), sg.Text("s3753740", size=(15, 1))]]
    input_rows4 = [[sg.Text("Chan Phong", size=(15, 1)), sg.Text('  '), sg.Text("s3753740", size=(15, 1))]]

    layout = [
        [sg.Text("Welcome to our project!", size=(25, 2))],
        header + input_rows + input_rows2 + input_rows3 + input_rows4,
        [sg.Button("Proceed!", size=(20, 2))]
    ]

    window = sg.Window('Table Simulation', layout, font='Courier 12')
    event, values = window.read()

    if event == "Proceed!":
        window.close()


def get_video():
    layout = [
        [sg.T("")],
        [sg.Text("Choose a video file:", size=(15, 1)), sg.Input(), sg.FileBrowse(key='file')],
        [sg.Button('Confirm', size=(10, 1)), sg.Button('Cancel', size=(10, 1))]
    ]

    window = sg.Window("Pop up testing", layout)
    event, values = window.read()

    if event == 'Confirm':
        window.close()

    print(values['file'])
    return values['file']


def get_calibration(filepath):
    layout = [
        [sg.Text('Please input the UI calibration for your video')],
        [sg.Text('Line up:', size=(15, 1)), sg.InputText()],
        [sg.Text('Line down:', size=(15, 1)), sg.InputText()],
        [sg.Text('Up limit:', size=(15, 1)), sg.InputText()],
        [sg.Text('Down limit:', size=(15, 1)), sg.InputText()],
        [sg.Text('Demo image for video:')],
        [sg.Image(filename='', key='image')],
        [sg.Button('Confirm', size=(10, 1))]
    ]
    cal_list = []
    cap = cv2.VideoCapture(filepath)

    window = sg.Window('Get calibration', layout, location=(0, 0))
    img_element = window['image']

    close = False
    cur_frame = 0
    while not close:
        event, values = window.read(timeout=0)
        while cap.isOpened():

            ret, frame = cap.read()
            if not ret:
                break
            if cur_frame == 1:
                break
            imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
            img_element.update(data=imgbytes)
            cur_frame += 1
        if event == 'Confirm':
            for i in range(4):
                cal_list.append(values[i])
            close = True
            window.close()
    print(cal_list)
    return cal_list


def play_video(filepath, cal_list):
    cap = cv2.VideoCapture(filepath)
    num_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    cnt_up = 0
    cnt_down = 0
    cnt_list = []

    layout = [
        [sg.Text("Start playing video...")],
        [sg.Image(filename='', key='image')],
        [sg.Slider(range=(0, num_frames),
                   size=(60, 10), orientation='h', key='slider')],
        [sg.Button('Finish', size=(10, 1))]
    ]

    window = sg.Window("Playing video...", layout, finalize=True, location=(0, 0))
    img_element = window['image']
    slider_element = window['slider']

    #Start declaring variables for the video

    # Get width and height of video

    w = cap.get(3)
    h = cap.get(4)
    print(w)
    print(h)
    frameArea = h * w
    areaTH = frameArea / 400

    # Lines
    # line_up=int(2*(h/5))
    # line_down=int(3*(h/5))
    #
    # up_limit=int(1*(h/5))
    # down_limit=int(4*(h/5))

    # Testing change position
    line_up = int(3 * (h / 5))
    line_down = int(2 * (h / 5))

    print(line_up)
    print(line_down)
    up_limit = int(1 * (h / 5))
    down_limit = int(4 * (h / 5))

    print("Red line y:", str(line_down))
    print("Blue line y:", str(line_up))
    line_down_color = (255, 0, 0)
    line_up_color = (225, 0, 255)
    pt1 = [0, line_down]
    pt2 = [w, line_down]
    pts_L1 = np.array([pt1, pt2], np.int32)
    pts_L1 = pts_L1.reshape((-1, 1, 2))
    pt3 = [0, line_up * 1.12]
    pt4 = [w, line_up * 1.12]

    pts_L2 = np.array([pt3, pt4], np.int32)
    pts_L2 = pts_L2.reshape((-1, 1, 2))

    pt5 = [0, down_limit]
    pt6 = [w, down_limit]
    pts_L3 = np.array([pt5, pt6], np.int32)
    pts_L3 = pts_L3.reshape((-1, 1, 2))
    pt7 = [0, up_limit]
    pt8 = [w, up_limit]
    pts_L4 = np.array([pt7, pt8], np.int32)
    pts_L4 = pts_L4.reshape((-1, 1, 2))

    # Background Subtractor
    fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=True)

    # Kernals
    kernalOp = np.ones((3, 3), np.uint8)
    kernalOp2 = np.ones((5, 5), np.uint8)
    kernalCl = np.ones((11, 11), np.uint8)

    font = cv2.FONT_HERSHEY_SIMPLEX
    cars = []
    max_p_age = 5
    pid = 1

    close = False
    cur_frame = 0
    while not close:
        while cap.isOpened():
            event, values = window.read(timeout=0, close=False)
            ret, frame = cap.read()
            if event == 'Finish':
                close = True
                cap.release()
                cv2.destroyAllWindows()
                window.close()
            if not ret:
                break
            # Adjust the frame slider
            if int(values['slider']) != cur_frame - 1:
                cur_frame = int(values['slider'])
                cap.set(cv2.CAP_PROP_POS_FRAMES, cur_frame)
            slider_element.update(cur_frame)

            # Print images onto GUI
            # imgbytes = cv.imencode('.png', frame)[1].tobytes()  # ditto
            # img_element.update(data=imgbytes)
            cur_frame += 1

            for i in cars:
                i.age_one()
            fgmask = fgbg.apply(frame)
            fgmask2 = fgbg.apply(frame)

            if ret == True:

                # Binarization
                ret, imBin = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
                ret, imBin2 = cv2.threshold(fgmask2, 200, 255, cv2.THRESH_BINARY)
                # OPening i.e First Erode the dilate
                mask = cv2.morphologyEx(imBin, cv2.MORPH_OPEN, kernalOp)
                mask2 = cv2.morphologyEx(imBin2, cv2.MORPH_CLOSE, kernalOp)

                # Closing i.e First Dilate then Erode
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernalCl)
                mask2 = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, kernalCl)

                # Find Contours
                countours0, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                for cnt in countours0:
                    area = cv2.contourArea(cnt)
                    print("this is area:" + str(area))
                    if area > areaTH:
                        ####Tracking######
                        m = cv2.moments(cnt)
                        cx = int(m['m10'] / m['m00'])
                        cy = int(m['m01'] / m['m00'])
                        x, y, w, h = cv2.boundingRect(cnt)

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

                        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                        img = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                for i in cars:
                    cv2.putText(frame, str(i.getId()), (i.getX(), i.getY()), font, 0.3, i.getRGB(), 1, cv2.LINE_AA)

                str_up = 'UP: ' + str(cnt_up)
                str_down = 'DOWN: ' + str(cnt_down)
                frame = cv2.polylines(frame, [pts_L1], False, line_down_color, thickness=2)
                frame = cv2.polylines(frame, [pts_L2], False, line_up_color, thickness=2)
                frame = cv2.polylines(frame, [pts_L3], False, (255, 255, 255), thickness=1)
                frame = cv2.polylines(frame, [pts_L4], False, (255, 255, 255), thickness=1)
                cv2.putText(frame, str_up, (10, 40), font, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(frame, str_up, (10, 40), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                cv2.putText(frame, str_down, (10, 90), font, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(frame, str_down, (10, 90), font, 0.5, (255, 0, 0), 1, cv2.LINE_AA)
                cv2.imshow('Frame', frame)
    print(filepath)
    print(cal_list)

    cnt_list.append(cnt_up)
    cnt_list.append(cnt_down)
    return cnt_list


def finalization(cnt_list):
    layout = [
        [sg.Text('Number of cars moving up:'), sg.Text(cnt_list[0])],
        [sg.Text('Number of car moving down:'), sg.Text(cnt_list[1])],
        [sg.Text('Number of car violated traffic rules:'), sg.Text('0')],
        [sg.Button('Exit', size=(10, 1))]
    ]
    window = sg.Window("Finalization", layout)
    event, values = window.read()

    if event == 'Exit':
        window.close()


sg.theme("LightGreen")
greeting()
filepath = get_video()
cal_list = get_calibration(filepath)
cnt_list = play_video(filepath, cal_list)
finalization(cnt_list)
