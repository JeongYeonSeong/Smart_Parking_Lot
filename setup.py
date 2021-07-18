import cv2
import configs.config as cf

video = cv2.VideoCapture(0)

x_pos = cf.PARK_X_POS
y_pos = cf.PARK_Y_POS
print('start setup')
while 1:
    ret, frame = video.read()
    if not ret:
        break

    frame = cv2.resize(frame, (1920, 1440))
    shapes = frame.shape
    for i in x_pos:
        cv2.line(frame,(i['start'], 0), (i['end'], shapes[0]), (255,0,0), 5)

    for k in y_pos:
        cv2.line(frame,(0, k), (shapes[1], k), (255,0,0), 5)

    frame = cv2.resize(frame, (int(1920 / 1.5), int(1440 / 1.5)))
    cv2.imshow("Tracking", frame)

    input_key = cv2.waitKey(1) & 0xFF 
 
    if input_key == ord('s'):
        cv2.imwrite('screenshots/line.jpg',frame)

    elif input_key == ord('q'):
        cv2.destroyAllWindows()
        exit()