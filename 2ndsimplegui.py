import cv2
import numpy as np
import PySimpleGUI as sg
import vehicles
import time
from PyQt5.QtGui import QImage, QPixmap

# Background color
sg.theme('LightGreen')

#Define layout
layout = [
    [sg.Text('Please input the UI calibration for your video')],
    [sg.Text('Line up:', size=(15, 1)), sg.InputText()],
    [sg.Text('Line down:', size=(15, 1)), sg.InputText()],
    [sg.Text('Up limit:', size=(15, 1)), sg.InputText()],
    [sg.Text('Down limit:', size=(15, 1)), sg.InputText()],
    [sg.T("")],
    [sg.Text("Choose a video file:", size=(15, 1)), sg.Input(), sg.FileBrowse(key='file'),
     sg.Button('Confirm', size=(5, 1))],
    [sg.Image(filename='', key='image')],
    [sg.Button('Exit', size=(10, 2)), sg.Button('Complete', size=(10, 2))]
]

# Window Design
window = sg.Window('OpenCV real-time image processing',
                   layout,
                   no_titlebar=False,
                   finalize=True)

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == 'Exit' or event == 'Complete':
        break
# print(event + "/n")
# for i in range(4):
#     print(values[i] + ", ")

    #Get width and height of video

    cnt_up=0
    cnt_down=0

    cap = cv2.VideoCapture(values['file'])

    w=cap.get(3)
    h=cap.get(4)
    print(w)
    print(h)
    frameArea=h*w
    areaTH=frameArea/400

    #Lines
    # line_up=int(2*(h/5))
    # line_down=int(3*(h/5))
    #
    # up_limit=int(1*(h/5))
    # down_limit=int(4*(h/5))

    #Testing change position
    line_up=int(3*(h/5))
    line_down=int(2*(h/5))

    print(line_up)
    print(line_down)
    up_limit=int(1*(h/5))
    down_limit=int(4*(h/5))

    print("Red line y:",str(line_down))
    print("Blue line y:",str(line_up))
    line_down_color=(255,0,0)
    line_up_color=(225,0,255)
    pt1 =  [0, line_down]
    pt2 =  [w, line_down]
    pts_L1 = np.array([pt1,pt2], np.int32)
    pts_L1 = pts_L1.reshape((-1,1,2))
    pt3 =  [0, line_up*1.12]
    pt4 =  [w, line_up*1.12]


    pts_L2 = np.array([pt3,pt4], np.int32)
    pts_L2 = pts_L2.reshape((-1,1,2))


    pt5 =  [ 0, down_limit]
    pt6 =  [ w, down_limit]
    pts_L3 = np.array([pt5,pt6], np.int32)
    pts_L3 = pts_L3.reshape((-1,1,2))
    pt7 =  [0, up_limit]
    pt8 =  [w, up_limit]
    pts_L4 = np.array([pt7,pt8], np.int32)
    pts_L4 = pts_L4.reshape((-1,1,2))

    #Background Subtractor
    fgbg=cv2.createBackgroundSubtractorMOG2(detectShadows=True)

    #Kernals
    kernalOp = np.ones((3,3),np.uint8)
    kernalOp2 = np.ones((5,5),np.uint8)
    kernalCl =  np.ones((11,11),np.uint8)


    font = cv2.FONT_HERSHEY_SIMPLEX
    cars = []
    max_p_age = 5
    pid = 1

    cur_frame = 0
    while cap.isOpened():
        event, values = window.read(timeout=0)
        if event == sg.WINDOW_CLOSED or event == 'Exit' or event == 'Complete':
            break
        ret, frame = cap.read()
        if not ret:
            break

        for i in cars:
            i.age_one()
        fgmask=fgbg.apply(frame)
        fgmask2=fgbg.apply(frame)

        if ret==True:

            #Binarization
            ret,imBin=cv2.threshold(fgmask,200,255,cv2.THRESH_BINARY)
            ret,imBin2=cv2.threshold(fgmask2,200,255,cv2.THRESH_BINARY)
            #OPening i.e First Erode the dilate
            mask=cv2.morphologyEx(imBin,cv2.MORPH_OPEN,kernalOp)
            mask2=cv2.morphologyEx(imBin2,cv2.MORPH_CLOSE,kernalOp)

            #Closing i.e First Dilate then Erode
            mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,kernalCl)
            mask2=cv2.morphologyEx(mask2,cv2.MORPH_CLOSE,kernalCl)


            #Find Contours
            countours0,hierarchy=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
            for cnt in countours0:
                area=cv2.contourArea(cnt)
                print( "this is area:" + str(area))
                if area>areaTH:
                    ####Tracking######
                    m=cv2.moments(cnt)
                    cx=int(m['m10']/m['m00'])
                    cy=int(m['m01']/m['m00'])
                    x,y,w,h=cv2.boundingRect(cnt)

                    new=True
                    if cy in range(up_limit,down_limit):
                        for i in cars:
                            if abs(x - i.getX()) <= w and abs(y - i.getY()) <= h:
                                new = False
                                i.updateCoords(cx, cy)

                                if i.going_UP(line_down,line_up)==True:
                                    cnt_up+=1
                                    print("ID:",i.getId(),'crossed going up at', time.strftime("%c"))
                                elif i.going_DOWN(line_down,line_up)==True:
                                    cnt_down+=1
                                    print("ID:", i.getId(), 'crossed going up at', time.strftime("%c"))
                                break
                            if i.getState()=='1':
                                if i.getDir()=='down'and i.getY()>down_limit:
                                    i.setDone()
                                elif i.getDir()=='up'and i.getY()<up_limit:
                                    i.setDone()
                            if i.timedOut():
                                index=cars.index(i)
                                cars.pop(index)
                                del i

                        if new==True: #If nothing is detected,create new
                            p=vehicles.Car(pid,cx,cy,max_p_age)
                            cars.append(p)
                            pid+=1

                    cv2.circle(frame,(cx,cy),5,(0,0,255),-1)
                    img=cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)

            for i in cars:
                cv2.putText(frame, str(i.getId()), (i.getX(), i.getY()), font, 0.3, i.getRGB(), 1, cv2.LINE_AA)




            str_up='UP: '+str(cnt_up)
            str_down='DOWN: '+str(cnt_down)
            frame=cv2.polylines(frame,[pts_L1],False,line_down_color,thickness=2)
            frame=cv2.polylines(frame,[pts_L2],False,line_up_color,thickness=2)
            frame=cv2.polylines(frame,[pts_L3],False,(255,255,255),thickness=1)
            frame=cv2.polylines(frame,[pts_L4],False,(255,255,255),thickness=1)
            cv2.putText(frame, str_up, (10, 40), font, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, str_up, (10, 40), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, str_down, (10, 90), font, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, str_down, (10, 90), font, 0.5, (255, 0, 0), 1, cv2.LINE_AA)
            cv2.imshow('frame',frame)