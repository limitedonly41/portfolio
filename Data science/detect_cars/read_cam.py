import os
import cv2

from ultralytics import YOLO


model = YOLO('best_kaggle_full.pt')



cap = cv2.VideoCapture('rtsp://tair:dk4nVbsict@91.245.73.84:8999/')
# rtsp://tair:dk4nVbsict@91.245.73.84:8999/

arr_num = []

num_cars_true = 0

while(True):

    # cv2.waitKey(200)

    # for i in range(10):
    #     cap.grab()
    
    # frame is a numpy array, that you can predict on 
    ret, frame = cap.read()
    
    num_cars = 0

    results = model(frame, verbose=False)[0]

    # print('done')


    for result in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result

        if score > 0.10:

            if y1 > 120:

                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(frame, str(round(score, 2)), (int(x1), int(y1 - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 2, cv2.LINE_AA)
                num_cars += 1


            # cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            # cv2.putText(frame, str(round(score, 2)), (int(x1), int(y1 - 10)),
            #             cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 2, cv2.LINE_AA)
            # num_cars += 1

    cv2.line(frame, (10,120), (1250,120), (50, 255, 0), 3)

    arr_num.append(num_cars)

    if len(arr_num) > 10:
        if arr_num.count(arr_num[0]) == len(arr_num):
            num_cars_true = arr_num[0]
            arr_num = []
        else:
            num_cars_true = max(arr_num)
            arr_num = []



    cv2.putText(frame, f'Number of cars:  {num_cars_true}', (int(15), int(30)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 2, cv2.LINE_AA)
    # 5) Display the resulting frame
    cv2.imshow('ml', frame)
   
    #Waits for a user input to quit the application
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()