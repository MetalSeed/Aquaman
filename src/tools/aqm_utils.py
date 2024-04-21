# 通用函数工具
import datetime
import logging
from logging import handlers
import os
import sys
import cv2

prjroot = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
# print(f"prjroot: {prjroot}")

def get_dir(*paths):
    if paths[0] == 'prjroot':
        return prjroot

# 示例
# file_full_name = get_file_full_name('1.jpg', 'data', 'output', 'table_setup')
def get_file_full_name(file_name, *subfolders):

    file_full_name = os.path.join(get_dir('prjroot'), *subfolders, file_name)
    return file_full_name

# 画框工具
def draw_multiple_rectangles_and_save(image_path, rectangles, save_path):
    # 读取图片
    img = cv2.imread(image_path)
    
    # 遍历矩形框列表，画每个矩形框
    # 每个rectangle参数是(x, y, width, height)，其中(x, y)是矩形框左上角的坐标
    for rectangle in rectangles:
        x1, y1, x2, y2 = rectangle
        # 画矩形框，参数依次为图片、左上角坐标、右下角坐标、颜色(BGR格式)、线条粗细
        # 使用红色(0, 0, 255)作为矩形框的颜色
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
    
    # 保存图片
    cv2.imwrite(save_path, img)
    print(f"保存修改后的图片到 {save_path}")


def init_logger(screenlevel, filename=None, logdir=None, modulename=''):
    """
    Initialize Logger.

    Args:
        screenlevel (logging): logging.INFO or logging.DEBUG
        filename (str): filename (without .log)
        logdir (str): directory name for log
        modulename (str): project name default

    """
    # for all other modules just use log = logging.getLogger(__name__)
    try:
        if not os.path.exists(logdir):
            os.makedirs(logdir)
    except OSError:
        print(f"Creation of the directory '{logdir}' failed")
        exit(1)
    else:
        print(f"Successfully created the directory '{logdir}' ")

    pics_path = "log/pics"
    try:
        if not os.path.exists(pics_path):
            os.makedirs(pics_path)
    except OSError:
        print(f"Creation of the directory '{pics_path}' failed")
        exit(1)
    else:
        print(f"Successfully created the directory '{pics_path}' ")

    root = logging.getLogger()
    [root.removeHandler(rh) for rh in root.handlers]  # pylint: disable=W0106
    [root.removeFilter(rf) for rf in root.filters]  # pylint: disable=W0106

    root = logging.getLogger('')
    root.setLevel(logging.WARNING)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(screenlevel)
    if filename and not filename == 'None':
        filename = filename.replace(
            "{date}", datetime.date.today().strftime("%Y%m%d"))
        all_logs_filename = os.path.join(logdir, filename + '.log')
        error_filename = os.path.join(logdir, filename + '_errors.log')
        info_filename = os.path.join(logdir, filename + '_info.log')

        print("Saving log file to: {}".format(all_logs_filename))
        print("Saving info file to: {}".format(info_filename))
        print("Saving error only file to: {}".format(error_filename))

        file_handler2 = handlers.RotatingFileHandler(
            all_logs_filename, maxBytes=300000, backupCount=20)
        file_handler2.setLevel(logging.DEBUG)

        error_handler = handlers.RotatingFileHandler(
            error_filename, maxBytes=300000, backupCount=20)
        error_handler.setLevel(logging.WARNING)

        info_handler = handlers.RotatingFileHandler(
            info_filename, maxBytes=30000000, backupCount=100)
        info_handler.setLevel(logging.INFO)

        # formatter when using --log command line and writing log to a file
        file_handler2.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s'))
        error_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s'))
        info_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s'))

        # root.addHandler(fh)
        root.addHandler(file_handler2)
        root.addHandler(error_handler)
        root.addHandler(info_handler)

    # screen output formatter
    stream_handler.setFormatter(
        logging.Formatter('%(levelname)s - %(message)s'))
    root.addHandler(stream_handler)

    mainlogger = logging.getLogger(modulename)
    mainlogger.setLevel(logging.DEBUG)

    # pd.set_option('display.height', 1000)  # pd.set_option('display.max_rows', 500)  # pd.set_option('display.max_columns', 500)  # pd.set_option('display.width', 1000)


# def exception_hook(*exc_info):
#     """Catches all unhandled exceptions."""
#     # Print the error and traceback
#     print("--- exception hook ----")
#     text = "".join(traceback.format_exception(
#         *exc_info))  # pylint: disable=E1120
#     log.error("Unhandled exception: %s", text)