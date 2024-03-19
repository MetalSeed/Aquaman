import cv2
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

###############################
#       添加项目根目录          #        
###############################
import os
import sys
# 获取当前脚本文件的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录（tools）
script_dir = os.path.dirname(script_path)
parent_dir = os.path.dirname(script_dir)
grandparent_dir = os.path.dirname(parent_dir)
# 降Aquaman子目录添加到sys.path
sys.path.append(grandparent_dir)
###############################
#       debug config          #
###############################
if_config = True



from loadconfig import filled_room_config, filled_room_rects, template_dir
from src.recognizer.nlth_table import Table
from src.tools.aqm_utils import get_file_full_name
from PIL import Image




class Test_recognizer(Table):
    def __init__(self):
        super().__init__()
        self.testimg = None

    def set_testimg(self, img):
        self.testimg = img
    #查询块的主要颜色和颜色范围，用来定hsv mask
    def find_dominant_colors_and_ranges_in_hsv(self, cropped_img, k=3):
        # 转换到HSV颜色空间
        hsv_img = cv2.cvtColor(np.array(cropped_img), cv2.COLOR_BGR2HSV)
        
        # 将图像数据转换为二维数组，每行一个像素，每列一个颜色通道
        pixels = hsv_img.reshape((-1, 3))
        
        # 使用K-means聚类算法找到最主要的k个颜色
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        # 获取每个聚类中心（主要颜色）在HSV空间的值
        dominant_colors_hsv = np.uint8(kmeans.cluster_centers_)
        
        # 初始化颜色范围列表
        color_ranges = []

        for i in range(k):
            cluster_pixels = pixels[kmeans.labels_ == i]
            min_vals = np.min(cluster_pixels, axis=0)
            max_vals = np.max(cluster_pixels, axis=0)
            color_ranges.append((min_vals, max_vals))
        
        # 计算每个聚类的大小，估计颜色占比
        _, counts = np.unique(kmeans.labels_, return_counts=True)
        total_count = np.sum(counts)
        
        # 计算每种颜色的占比
        color_ratios = counts / total_count
        sorted_indices = np.argsort(-color_ratios)
        sorted_colors_hsv = dominant_colors_hsv[sorted_indices]
        sorted_ratios = color_ratios[sorted_indices]
        sorted_color_ranges = [color_ranges[i] for i in sorted_indices]

        # 返回排序后的颜色、占比和颜色范围
        return sorted_colors_hsv, sorted_ratios, sorted_color_ranges
     
    def get_croped_img(self, region_name=None):
        img = self.testimg
        global region_global
        # Crop the image to the specified region
        if region_name is not None:
            if region_name == 'global':
                region = region_global # 全局替换
            else: region = filled_room_rects[region_name]
            cropped_img = img.crop((region[0], region[1], region[2], region[3]))
        else:
            cropped_img = img
        return cropped_img


    def get_color_ranges(self, region_name=None, k=3):
        if region_name is not None:
            print(f"# Region #: {region_name}")
        cropped_img = self.get_croped_img(region_name)
        # 获取主要颜色、颜色占比和颜色范围        
        sorted_colors_hsv, sorted_ratios, sorted_color_ranges = self.find_dominant_colors_and_ranges_in_hsv(cropped_img, k)
        # 打印结果
        for color_hsv, ratio, color_range in zip(sorted_colors_hsv, sorted_ratios, sorted_color_ranges):
            print(f"Color (HSV): {color_hsv}, Ratio: {ratio:.2f}, Range: {color_range}")
        return
    
    def get_color_match(self, color_ranges, threshold_color_match, region_name=None):
        cropped_img = self.get_croped_img(region_name)
        color_name = self.prr.color_matching(cropped_img, color_ranges, threshold_color_match)
        print(f"color name: {color_name}")
        return color_name

    def get_number(self, region_name=None):
        img = self.get_croped_img(region_name)
        number = self.prr.recognize_digits(img)
        print(f"{region_name}: {number}")
        return number

    # Board1, Hero_card1
    def get_card(self, card_name):
        rank_name = card_name + '_rank'
        img_rank = self.get_croped_img(rank_name)
        suit_name = card_name + '_suit'
        img_suit = self.get_croped_img(suit_name)
        card = self.prr.recognize_poker_card(img_rank, img_suit)
        print(f"{card_name}: {card}")
        return card
    
    def crop_save(self, region_name):
        cropped_img = self.get_croped_img(region_name)
        save_path = get_file_full_name(f"{region_name}.png", 'data', 'test')
        cropped_img.save(save_path)

    def get_global_region_color(self, save_flag = False, k=3):
        cropped_img = self.get_croped_img('global')
        if save_flag:
            save_path = get_file_full_name(f"global.png", 'data', 'test')
            cropped_img.save(save_path)
        self.get_color_ranges('global', k)
        return

def main(file_path):
    global region_global
    windowshot = Image.open(file_path)

    TR = Test_recognizer()
    TR.set_testimg(windowshot)

    # 测试内容 如果是windowshot，要输入矩形标题，如果是croped_img文件，不用输入标题
    # TR.get_color_ranges('Total_Pot', 3)
    # TR.get_color_match(TR.prr.color_ranges_pocker, TR.prr.threshold_color_match_poker, 'hero_card1_rank')
    # TR.get_number('pot_total')
    # TR.get_card('board2')

    # 裁剪保存对应的矩形区域
    # TR.crop_save('hero_card1_rank')

    TR.get_global_region_color(True)


#pb
rect1 = [288, 191, 312, 212]
rect2 = [505, 281, 528, 303]
rect3 = [505, 445, 528, 466]
rect4 = [15, 447, 36, 467]
rect5 = [254, 186, 273, 212] # 无效背面

current_rectangle = (118, 790, 166, 836)

region_global = current_rectangle

# 使用示例
if __name__ == '__main__':
    icon_path = os.path.join(template_dir, 'is_hero_turn.png')
    wshot_path = get_file_full_name('100.png', 'data', 'test')
    
    file_path = wshot_path
    main(file_path)

# 修改成鼠标画框识别OCR