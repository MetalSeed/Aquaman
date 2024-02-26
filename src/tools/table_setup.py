import os
import cv2


# 全局变量
rectangles = []  # 存储矩形框的坐标
drawing = False  # 标记是否开始画图
current_rectangle = (-1, -1, -1, -1)  # 当前矩形的坐标
rect_names = ["Rect1", "Rect2", "Rect3", "Rect4", "Rect5", "Rect6", "Rect7", "Rect8"]  # 矩形框的名字

def draw_rectangle(event, x, y, flags, param):
    global rectangles, drawing, current_rectangle

    # 鼠标左键按下开始绘制
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        current_rectangle = (x, y, x, y)
    
    # 鼠标移动更新矩形的宽和高
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            current_rectangle = (current_rectangle[0], current_rectangle[1], x, y)
    
    # 鼠标左键释放结束绘制
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        rectangles.append(current_rectangle)
        current_rectangle = (-1, -1, -1, -1)


def get_file_full_name(subf1, subf2, subf3, file_name):
    # 获取当前脚本的绝对路径
    script_dir = os.path.dirname(__file__)

    # 获取当前脚本的父目录的父目录
    grandparent_dir = os.path.dirname(os.path.dirname(script_dir))

    # 构建目标文件的绝对路径，包括子文件夹路径
    file_full_name = os.path.join(grandparent_dir, subf1, subf2, subf3, file_name)
    return file_full_name

def main(image_name):
    global rectangles
    image_path = get_file_full_name('data', 'input', 'table_setup', image_name)
    img = cv2.imread(image_path)
    cv2.namedWindow('table_setup')
    cv2.setMouseCallback('table_setup', draw_rectangle)

    while True:
        img_copy = img.copy()
        for idx, rect in enumerate(rectangles):
            cv2.rectangle(img_copy, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 0), 2)
            text_position = (img.shape[1] - 200, 30 * (idx+1))  # 在图像右侧显示文本
            cv2.putText(img_copy, f"{rect_names[idx]}: {rect}", text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        if current_rectangle != (-1, -1, -1, -1):
            cv2.rectangle(img_copy, (current_rectangle[0], current_rectangle[1]), (current_rectangle[2], current_rectangle[3]), (0, 0, 255), 2)
        cv2.imshow('table_setup', img_copy)

        # 按 'q' 退出循环
        if cv2.waitKey(1) & 0xFF == ord('q') or len(rectangles) >= len(rect_names):
            break

    cv2.destroyAllWindows()
    for idx, rect in enumerate(rectangles):
        print(f"{rect_names[idx]}: {rect}")



if __name__ == '__main__':
    iamge_name = '1.png'  # 更改为你的图片路径
    main(iamge_name)
