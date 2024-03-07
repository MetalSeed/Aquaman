import cv2
import numpy as np
from sklearn.cluster import KMeans

def find_dominant_colors_and_ranges_in_hsv(img, region, k=3):
    # 裁剪图像到指定区域
    cropped_img = img[region[1]:region[3], region[0]:region[2]]
    # 转换到HSV颜色空间
    hsv_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2HSV)
    
    # 将图像数据转换为二维数组，每行一个像素，每列一个颜色通道
    pixels = hsv_img.reshape((-1, 3))
    
    # 使用K-means聚类算法找到最主要的k个颜色
    kmeans = KMeans(n_clusters=k, random_state=42)
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
    
    # 打印结果
    for color_hsv, ratio, color_range in zip(sorted_colors_hsv, sorted_ratios, sorted_color_ranges):
        print(f"Color (HSV): {color_hsv}, Ratio: {ratio:.2f}, Range: {color_range}")
    
    # 返回排序后的颜色、占比和颜色范围
    return sorted_colors_hsv, sorted_ratios, sorted_color_ranges

# 使用示例
img_path = 'path/to/your/image.jpg'  # 修改为你的图像路径
img = cv2.imread(img_path)

region = (100, 100, 500, 500)  # (left, top, right, bottom)
dominant_colors_hsv, color_ratios, color_ranges = find_dominant_colors_and_ranges_in_hsv(img, region, k=3)
