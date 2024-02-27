#

# 1. 模板匹配
import cv2
import numpy as np

def match_template(image, template):
    res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.9
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        cv2.rectangle(image, pt, (pt[0] + w, pt[1] + h), (0,255,255), 2)
    cv2.imshow('Detected',image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 加载图像和模板
image = cv2.imread('poker_screen.png')
template = cv2.imread('card_template.png')
w, h = template.shape[:-1]

match_template(image, template)
