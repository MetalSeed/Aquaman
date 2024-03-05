# 抠图 之后给到image recognition
#
# 根据预定进行截图
# pk平台设置 4色牌 牌背色 桌布色 
# Various routines, such as taking screen shots, cropping etc

from Aquaman.src.recognizer.image_recognizer_OCR import BasicOCR


class ScreenScraper:
    def __init__(self, platform_dict, max_players):
        self.table_dict = platform_dict[max_players]


    def take_windowshot(self):
        # 截取屏幕
        pass

    def it_is_my_turn(self):
        # 识别是否轮到我行动
        pass

    def get_my_cards(self):
        # 识别我的手牌
        self.my_cards = []
        # scraper to recoginze my cards
        pass



# 定义不同平台的识别和路径
# 调用nn or OCR, and screenutils

class RoomRecognizer:
    def __init__(self, platform, max_players):
        pass

    def is_it_my_turn(self):
        pass

    def is_the_game_over(self):
        pass

    def is_hero_lost_all(self):
        pass

    def is_hero_short_funds(self):
        pass



class WePokerRecognizer(RoomRecognizer, BasicOCR):
    def __init__(self, platform, max_players):
        super().__init__(platform, max_players)
        self.screenshot = ScreenScraper(platform, max_players)

    def is_it_my_turn(self):
        return self.screenshot.it_is_my_turn()

    def get_my_cards(self):
        return self.screenshot.get_my_cards()

    def is_the_game_over(self):
        pass

    def is_short_funds(self):
        pass