import PySimpleGUI as sg
import numpy as np
import cv2 as cv


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
    cap = cv.VideoCapture(filepath)

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
            imgbytes = cv.imencode('.png', frame)[1].tobytes()  # ditto
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
    cap = cv.VideoCapture(filepath)
    num_frames = cap.get(cv.CAP_PROP_FRAME_COUNT)

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

    close = False
    cur_frame = 0
    while not close:
        while cap.isOpened():
            event, values = window.read(timeout=0, close=False)
            ret, frame = cap.read()
            if event == 'Finish':
                close = True
                window.close()
            if not ret:
                break
            # Adjust the frame slider
            if int(values['slider']) != cur_frame - 1:
                cur_frame = int(values['slider'])
                cap.set(cv.CAP_PROP_POS_FRAMES, cur_frame)
            slider_element.update(cur_frame)

            # Print images onto GUI
            imgbytes = cv.imencode('.png', frame)[1].tobytes()  # ditto
            img_element.update(data=imgbytes)
            cur_frame += 1
    print(filepath)
    print(cal_list)


sg.theme("LightGreen")
greeting()
filepath = get_video()
cal_list = get_calibration(filepath)
play_video(filepath, cal_list)
