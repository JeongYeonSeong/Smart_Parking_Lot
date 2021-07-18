import cv2
import numpy as np
import time as t
from configs.sockets import Clients as Clients
from configs.cars import Car as Car
from configs.cars import Car_List as Car_List
import configs.config as cf
import requests

########################       
# settings
########################    
print('start system')
# 허용 오차 범위
permitted_xy = 80

# set cam port
cam_port = 0

main_cars = Car_List(0)

# set_servers_ip
nav_ip = cf.SOC_IP
nav_port = cf.NAV_PORT
dsp_ip = cf.SOC_IP
dsp_port = cf.DISP_PORT
########################
# init car Objects
response = requests.get('http://34.204.54.60/api/initParking')

datas = response.json()['parkingList']

for i in datas:
    init = {'id':i['car_number_plate'], 'position':i['car_parking_id']}
    main_cars.cars.append(Car(inits=init))


########################
# Yolo 로드
YOLO_net = cv2.dnn.readNet("configs/detection/yolov4.weights", "configs/detection/yolov4.cfg")
YOLO_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
YOLO_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
classes = []
with open("configs/detection/coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = YOLO_net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in YOLO_net.getUnconnectedOutLayers()]
colors = np.random.uniform(0, 255, size=(len(classes), 3))

video = cv2.VideoCapture(cam_port)
cars = []
print('yolo, cam load')
# count_frame
count_frame = 0

# check time
start_time = t.time()

print('start tracking')
while video.isOpened():
    count_frame += 1

    ret, frame = video.read()
    frame = cv2.resize(frame, (1920, 1440))

    if not ret:
        break

    h, w, c = frame.shape

    ########################       
    # Detecting start
    ########################  
    # YOLO 입력                                   이 값으로 정확도/속도 조절 가능
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (608, 608), (0, 0, 0),
    True, crop=False)
    YOLO_net.setInput(blob)
    outs = YOLO_net.forward(output_layers)

    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        # check now cars
        now_car_target = 0
        for detection in out:

            scores = detection[5:]
            class_id = np.argmax(scores)

            confidence = scores[class_id]
            # 검출 신뢰도
            if confidence > 0.1:
                #detect only cars
                if class_id == 2 or class_id == 5 or class_id == 7 or class_id == 65 or class_id == 68:
                    class_id = 2
                else:
                    continue

                # Object detected
                # 검출기의 경계상자 좌표는 0 ~ 1로 정규화되어있으므로 다시 전처리  
                center_x = int(detection[0] * w)
                center_y = int(detection[1] * h)
                dw = int(detection[2] * w)
                dh = int(detection[3] * h)

                # Rectangle coordinate
                x = int(center_x - dw / 2)
                y = int(center_y - dh / 2)
                boxes.append([x, y, dw, dh])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    ########################       
    # Detecting finished
    ########################
    tk = 0
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.45, 0.4)

    for i in range(len(boxes)):
        if i in indexes:
            now_car_target += 1
        
            x, y, w, h = boxes[i]

            center_x = int(x + w / 2)
            center_y = int(y + h / 2)

            if cf.PARK_Y_POS[2] <= center_y <= cf.PARK_Y_POS[3]:
                for Y_POS in range(cf.PARK_Y_POS[2], cf.PARK_Y_POS[3], 5):
                    if cf.PARK_X_POS[0]['start'] - (cf.PARK_X_POS[0]['start'] - cf.PARK_X_POS[0]['end']) / 1440 * Y_POS \
                            <= center_x <= \
                            cf.PARK_X_POS[1]['start'] - (
                            cf.PARK_X_POS[1]['start'] - cf.PARK_X_POS[1]['end']) / 1440 * Y_POS:

                        client = Clients(nav_ip, nav_port)
                        data = client.send_message('2')
                        if data[0] == 'no Data':
                            break
                        else:
                            print('got datas :', data)
                            car_num = data[0]
                            route = data[1:]
                            print(data)
                            client.end_client()

                            main_cars.cars.append(Car(car_num, center_x, center_y, route, main_cars))
                        break

            label = ''
            trk_cars = main_cars.cars[0:]

            ###############################
            # 객체 트래킹 시작
            ###############################
            for index, k in enumerate(trk_cars):
                if k.pos_x - permitted_xy <= center_x <= k.pos_x + permitted_xy and \
                    k.pos_y - permitted_xy <= center_y <= k.pos_y + permitted_xy:
                    check = k.set_position(center_x, center_y, main_cars)

                    if check == False:
                        client = Clients(nav_ip, nav_port)
                        data = 0

                        if k.position == 'outsider':
                            trk_cars.pop(index)

                        if k.route_stop and k.position != k.prev_pos and type(k.position) == type(1):
                            data = client.send_message('4/' + str(k.position) + '/' + str(k.prev_pos) + '/' + str(k.id))
                        else:
                            data = client.send_message('3/' + str(k.position) + '/' + str(k.prev_pos) + '/' + str(k.id))
                            k.set_route(data[1:])
                            print(k.route)
                        client.end_client()

                    # k.detected.append(count_frame)
                    label += k.id + ' - ' + str(k.position) + str(k.route)
                    break

            score = confidences[i]

            # 경계상자와 클래스 정보 투영
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame, label, (x, y + 13), cv2.FONT_ITALIC, 1, (0, 0, 255), 1)
            cv2.circle(frame, (center_x, center_y), 3, (0, 0, 255), 5)

            tk = len(trk_cars)

    # fps 출력
    finish_time = t.time()
    times = finish_time - start_time
    label = ""
    label += "FPS : " + str(int((count_frame)/ times * 10) / 10)
    cv2.putText(frame, label, (10, 50), cv2.FONT_ITALIC, 2, (255, 255, 0), 2)

    frame = cv2.resize(frame, (int(1920 / 1.5), int(1440 / 1.5)))

    cv2.imshow("Tracking", frame)

    input_key = cv2.waitKey(10) & 0xFF 
 

    if input_key == ord('s'):
        cv2.imwrite('screenshots/screen.jpg', frame)
    elif input_key == ord('q'):
        cv2.destroyAllWindows()
        exit()