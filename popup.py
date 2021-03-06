import PySimpleGUI as sg
import numpy as np
import cv2
import vehicles
import time
import os

lineDrawn = []

# specifying output folder for exports
path = 'output'
os.makedirs(path, exist_ok=True)



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
        [sg.Button("Proceed!", size=(10, 1)), sg.Button("Guide", size=(10, 1)), sg.Button("Exit", size=(10, 1))]
    ]

    window = sg.Window('Greetings', layout, font='Courier 12')
    event, values = window.read()

    if event == "Proceed!":
        window.close()
        return 0
    if event == "Guide":
        window.close()
        return 1
    if event == "Exit" or event == sg.WINDOW_CLOSED:
        window.close()
        exit()


def manual_guide():
    layout = [
        [sg.Text("Step 1: Greetings", font=('Arial', 12, 'underline italic'))],
        [sg.Text("Click on the Continue button to continue to import a video.")],
        [sg.Text("Step 2: Import video", font=('Arial', 12, 'underline italic'))],
        [sg.Text("Tap on the browse button to choose a video file from your computer. Click Confirm to proceed to the "
                 "Calibration phase.")],
        [sg.Text("Step 3: Calibration", font=('Arial', 12, 'underline italic'))],
        [sg.Text("An overview image of your video will be shown on the screen. You can choose to make calibration "
                 "accordingly. Otherwise, the system will proceed with default values.")],
        [sg.Text("Step 4: Playing video", font=('Arial', 12, 'underline italic'))],
        [sg.Text("The video will start playing with the previous step's coordinate values. There is also a slider "
                 "that you can use to adjust the video back and forth. Clicking on the Finish button will move you to "
                 "the Finalization phase.")],
        [sg.Text("Step 5: Finalization", font=('Arial', 12, 'underline italic'))],
        [sg.Text("Any data collected from your video will be shown here. Click Exit to close the application.")],
        [sg.Button("Continue", size=(10, 1))]
    ]

    window = sg.Window("User Manual Guide", layout)
    event, values = window.read()
    if event == "Continue":
        window.close()
    elif event == sg.WINDOW_CLOSED:
        window.close()
        exit()


def get_video():
    layout = [
        [sg.T("")],
        [sg.Text("Choose a video file:", size=(15, 1)), sg.Input(), sg.FileBrowse(key='file')],
        [sg.Button('Confirm', size=(10, 1)), sg.Button('Cancel', size=(10, 1))]
    ]

    window = sg.Window("Choose a video to play", layout)
    event, values = window.read()

    if event == 'Confirm':
        window.close()
    elif event == 'Cancel' or event == sg.WINDOW_CLOSED:
        window.close()
        exit()

    print(values['file'])
    return values['file']


# def get_calibration(filepath):
#     layout = [
#         [sg.Text('Please input the UI calibration for your video')],
#         [sg.Text('Line up:', size=(15, 1)), sg.InputText()],
#         [sg.Text('Line down:', size=(15, 1)), sg.InputText()],
#         [sg.Text('Up limit:', size=(15, 1)), sg.InputText()],
#         [sg.Text('Down limit:', size=(15, 1)), sg.InputText()],
#         [sg.Text('Demo image for video:')],
#         [sg.Image(filename='', key='image')],
#         [sg.Button('Confirm', size=(10, 1))]
#     ]
#     cal_list = []
#     cap = cv2.VideoCapture(filepath)
#
#     window = sg.Window('Get calibration', layout, location=(0, 0))
#     img_element = window['image']
#
#     close = False
#     cur_frame = 0
#     while not close:
#         event, values = window.read(timeout=0)
#         while cap.isOpened():
#             ret, frame = cap.read()
#             if not ret:
#                 break
#             if cur_frame == 1:
#                 break
#             imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
#             img_element.update(data=imgbytes)
#             cur_frame += 1
#         if event == 'Confirm':
#             for i in range(4):
#                 cal_list.append(values[i])
#             close = True
#             window.close()
#         elif event == sg.WINDOW_CLOSED:
#             close = True
#             window.close()
#             exit()
#     print(cal_list)
#     return cal_list


def play_video(filepath):
    def mouse_handler(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # there can only be two coords, a starting and
            # an end point to form a line
            # TODO: ability to draw multiple lines separately
            if len(lineDrawn) > 2:
                lineDrawn.clear()

            cv2.circle(img, (x, y), 3, (0, 0, 255), 3, cv2.FILLED)
            lineDrawn.append((x, y))
        if event == cv2.EVENT_RBUTTONDOWN:
            lineDrawn.clear()
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

    width = cap.get(3)
    height = cap.get(4)
    print(width)
    print(height)
    frameArea = width * height
    areaTH = frameArea / 400

    # Testing

    # Background Subtractor
    fgbg = cv2.bgsegm.createBackgroundSubtractorGSOC(noiseRemovalThresholdFacBG=0.01, noiseRemovalThresholdFacFG=0.0001)

    # Kernals
    kernalOp = np.ones((3, 3), np.uint8)
    kernalOp2 = np.ones((5, 5), np.uint8)
    kernalCl = np.ones((11, 11), np.uint8)

    font = cv2.FONT_HERSHEY_SIMPLEX
    cars = []

    max_p_age = 5
    pid = 1

    img_num = 0

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
            elif event == sg.WINDOW_CLOSED:
                close = True
                cap.release()
                cv2.destroyAllWindows()
                window.close()
                exit()
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

            line_up = int(2 * (height / 5))
            line_down = int(3 * (height / 5))

            up_limit = int(1.9 * (height / 5))
            down_limit = int(3.1 * (height / 5))

            # print("Red line y:", str(line_down))
            # print("Blue line y:", str(line_up))

            line_down_color = (255, 0, 0)
            line_up_color = (225, 0, 255)
            pt1 = [0, line_down]
            pt2 = [width, line_down]
            pts_L1 = np.array([pt1, pt2], np.int32)
            pt3 = [0, line_up]
            pt4 = [width, line_up]

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

            if len(lineDrawn) > 0:
                pts_L1 = np.array([lineDrawn[0], lineDrawn[0]], np.int32)
                pts_L1 = pts_L1.reshape((-1, 1, 2))

            else:
                pts_L1 = np.array([(0, 0), (0, 0)], np.int32)
                pts_L1 = pts_L1.reshape((-1, 1, 2))

            if ret == True:

                # Binarization
                ret, imBin = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
                # OPening i.e First Erode the dilate
                mask = cv2.morphologyEx(imBin, cv2.MORPH_OPEN, kernalOp)

                # Closing i.e First Dilate then Erode
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernalCl)

                # Find Contours
                countours0, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                for cnt in countours0:
                    area = cv2.contourArea(cnt)
                    if area > areaTH:
                        # extracting centroids here
                        m = cv2.moments(cnt)
                        cx = int(m['m10'] / m['m00'])
                        cy = int(m['m01'] / m['m00'])

                        # assigning rectangle/bounding box coords
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

                                        # outputting and cropping captured vehicles
                                        roi = frame[y:y + h, x:x + w]
                                        img_num += 1
                                        file_name = "test" + str(img_num) + ".png"
                                        cv2.imwrite(os.path.join(path, file_name), roi)
                                        # if img_num > 30:
                                        #     exit()
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

                            # If nothing is detected,create new
                            if new:
                                p = vehicles.Car(pid, cx, cy, max_p_age)
                                cars.append(p)
                                pid += 1

                        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                        img = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                for i in cars:
                    cv2.putText(frame, 'ID: ' + str(i.getId()), (i.getX(), i.getY()), font, 0.3, i.getRGB(), 1,
                                cv2.LINE_AA)

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
                cv2.putText(frame, str(width), (10, 60), font, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                # grabbing coords stored in array if present
                # then start drawing over latter frames
                if len(lineDrawn) == 2:
                    cv2.circle(frame, lineDrawn[0], 3, (0, 0, 255), 3, cv2.FILLED)
                    cv2.circle(frame, lineDrawn[1], 3, (0, 0, 255), 3, cv2.FILLED)
                    cv2.line(frame, lineDrawn[0], lineDrawn[1], (255, 0, 0), 2, cv2.LINE_AA)

                cv2.imshow('Frame', frame)
                cv2.setMouseCallback('Frame', mouse_handler)
    print(filepath)
    # print(cal_list)

    cnt_list.append(cnt_up)
    cnt_list.append(cnt_down)
    return cnt_list


def finalization(cnt_list, path):
    print(path)
    layout = [
        [sg.Text('Number of cars moving up:'), sg.Text(cnt_list[0])],
        [sg.Text('Number of car moving down:'), sg.Text(cnt_list[1])],
        [sg.Text('Number of car violated traffic rules:'), sg.Text('0')],
        [sg.Button('Exit', size=(10, 1)), sg.Button('Images', size=(10, 1))]
    ]
    window = sg.Window("Finalization", layout)
    event, values = window.read()

    if event == 'Exit':
        window.close()
    elif event == 'Images':
        os.startfile(path)
        window.close()


sg.theme("LightGreen")
get_cmd = greeting()

if get_cmd == 0:
    filepath = get_video()
    # cal_list = get_calibration(filepath)
    cnt_list = play_video(filepath)
    finalization(cnt_list, path)
else:
    if get_cmd == 1:
        manual_guide()
        filepath = get_video()
        # cal_list = get_calibration(filepath)
        cnt_list = play_video(filepath)
        finalization(cnt_list, path)
