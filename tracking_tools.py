import cv2
def select_ROI(filename):
    cap         = cv2.VideoCapture(filename)   #create feed object
    flag, frame = cap.read()                   # read first frame
    bbox        = cv2.selectROI("Select Object to Track", frame, fromCenter=True, showCrosshair=True)
    cap.release()
    cv2.destroyAllWindows()
    for i in range(5):
        cv2.waitKey(1)
    return bbox
