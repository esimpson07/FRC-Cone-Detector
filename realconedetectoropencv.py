import cv2
import numpy as np
cap = cv2.VideoCapture(0)
cv2.namedWindow('OpenCV Detection')
cv2.startWindowThread()

while True:
    _, img = cap.read()
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    img_HSV = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
    img_thresh = cv2.inRange(img_HSV, np.array([17, 100, 100]), np.array(([255, 255, 255])))

    kernel = np.ones((2, 2))
    img_thresh_opened = cv2.morphologyEx(img_thresh, cv2.MORPH_OPEN, kernel)
    img_thresh_blurred = cv2.medianBlur(img_thresh_opened, 5)
    img_edges = cv2.Canny(img_thresh_blurred, 80, 160)
    contours, _ = cv2.findContours(np.array(img_edges), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    img_contours = np.zeros_like(img_edges)
    cv2.drawContours(img_contours, contours, -1, (255,255,255), 2)
    approx_contours = []

    for c in contours:
        approx = cv2.approxPolyDP(c, 10, closed = True)
        approx_contours.append(approx)
    img_approx_contours = np.zeros_like(img_edges)
    cv2.drawContours(img_approx_contours, approx_contours, -1, (255,255,255), 1)
    all_convex_hulls = []
    for ac in approx_contours:
        all_convex_hulls.append(cv2.convexHull(ac))
    img_all_convex_hulls = np.zeros_like(img_edges)
    cv2.drawContours(img_all_convex_hulls, all_convex_hulls, -1, (255,255,255), 2)
    convex_hulls_3to10 = []
    for ch in all_convex_hulls:
        if 3 <= len(ch) <= 10:
            convex_hulls_3to10.append(cv2.convexHull(ch))
    img_convex_hulls_3to10 = np.zeros_like(img_edges)
    cv2.drawContours(img_convex_hulls_3to10, convex_hulls_3to10, -1, (255,255,255), 2)

    def convex_hull_pointing_up(ch):
            
        points_above_center, points_below_center = [], []
        
        x, y, w, h = cv2.boundingRect(ch)
        aspect_ratio = w / h
        
        if aspect_ratio < 0.8:
            vertical_center = y + h / 2

            for point in ch:
                if point[0][1] < vertical_center:
                    points_above_center.append(point)
                elif point[0][1] >= vertical_center:
                    points_below_center.append(point)

            left_x = points_below_center[0][0][0]
            right_x = points_below_center[0][0][0]
            for point in points_below_center:
                if point[0][0] < left_x:
                    left_x = point[0][0]
                if point[0][0] > right_x:
                    right_x = point[0][0]

            for point in points_above_center:
                if (point[0][0] < left_x) or (point[0][0] > right_x):
                    return False
        else:
            return False
            
        return True
    cones = []
    bounding_rects = []
    for ch in convex_hulls_3to10:
        if convex_hull_pointing_up(ch):
            cones.append(ch)
            rect = cv2.boundingRect(ch)
            bounding_rects.append(rect)
    img_cones = np.zeros_like(img_edges)
    img_res = img.copy()

    for rect in bounding_rects:
        cv2.rectangle(img_res, (rect[0], rect[1]), (rect[0]+rect[2], rect[1]+rect[3]), (1, 255, 1), 3)

    if cv2.waitKey(1) == 27: 
        break
    
    cv2.imshow('OpenCV Detection', img_res)

