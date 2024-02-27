import cv2


def find_template_in_region(main_image, template_image, region):
    """
    在主图片的指定矩形区域内查找模板图片。
    :param main_image: 主图片,          cv2.imread(image_path)
    :param template_image: 模板图片。    cv2.imread(image_path)
    :param region: 指定查找的矩形区域，格式为(x, y, width, height)。
    :return: True or False
    """
    # 裁剪主图片中的指定区域
    x, y, width, height = region
    cropped_main_image = main_image[y:y+height, x:x+width]
    
    # 进行模板匹配
    result = cv2.matchTemplate(cropped_main_image, template_image, cv2.TM_CCOEFF_NORMED)

    # 设置阈值
    threshold = 0.9
    locations = np.where(result >= threshold)
    locations = list(zip(*locations[::-1]))

    if locations:
        print("模板图片在指定区域内找到。")
        return True
    else:
        print("模板图片在指定区域内未找到。")
        return False


main_image_path = 'path/to/your/main_image.jpg'
template_image_path = 'path/to/your/template_image.jpg'

main_image = cv2.imread(main_image_path)
template_image = cv2.imread(template_image_path)
region = (100, 100, 300, 300)  # 示例区域，根据需要调整

find_template_in_region(main_image, template_image, region)
