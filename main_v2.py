import os.path
import shutil
import zipfile
import re
from multiprocessing import Pool

from paddleocr import PaddleOCR
from tqdm import tqdm
import pandas as pd

# Paddleocr目前支持的多语言语种可以通过修改lang参数进行切换
# 例如`ch`, `en`, `fr`, `german`, `korean`, `japan`

END_STR = "在前"
PATTERN_STR = "于前"

ocr_util = PaddleOCR(use_angle_cls=True,
                     lang="ch")  # need to run only once to download and load model into memory


class OcrImage():
    def __init__(self):
        self.result_path = os.getcwd() + "\\" + "result"
        if not os.path.exists(self.result_path):
            os.mkdir(self.result_path)
        self.base_path = os.getcwd() + "\\" + "data"
        if not os.path.exists(self.base_path):
            os.mkdir(self.base_path)

    def ocr_img(self, img):
        ret = ""
        flag = 0
        result = ocr_util.ocr(img, cls=True)
        try:
            for line in result:
                t = re.search(END_STR, line[1][0])
                if t is not None or line[1][0].find("市") < 0:
                    flag = 0
                if flag == 1 or re.search(PATTERN_STR, line[1][0]) is not None:
                    flag = 1
                    regex = re.search(r"[:：](.*)", line[1][0])
                    if regex:
                        ret += regex.group(1)
                    else:
                        temp = line[1][0]
                        ind = temp.find("途经")
                        if ind > 0:
                            temp = temp[ind + 2:]
                        ret += temp
        except:
            print(img)
        return pd.DataFrame({
            "姓名": img.split("\\")[-1].split(".")[0].strip(),
            "行程": ret
        }, index=[0])

    def process(self, data_list, path):
        if os.path.exists(path):
            os.remove(path)
        results = list()
        with Pool(processes=7) as p:
            for r in tqdm(p.imap(self.ocr_img, data_list), total=len(data_list)):
                results.append(r)
                if len(results) % 10 == 0:
                    if not os.path.exists(path):
                        self.append_csv(pd.concat(results), True, path)
                    else:
                        self.append_csv(pd.concat(results), False, path)
                    results = list()

    def outer_process(self, zipfile_list):
        for file_path in zipfile_list:
            new_path, name = self.unzip(file_path)
            if name is not None:
                print("begin process")
                self.process([new_path + "\\" + file for file in os.listdir(new_path)], self.get_result_path(name))

    def append_csv(self, res: pd.DataFrame, header, path):
        res.to_csv(
            path, mode='a', index=False, header=header)

    def get_result_path(self, name):
        return self.result_path + "\\" + name + ".CSV"

    def judge_file(self, path):
        type = os.path.basename(path).split(".")[-1]
        if type.lower() in ["jar", "zip", "7z", "bz2", "gz", "tar", "xz"]:
            return True
        else:
            return False

    def unzip(self, file_path):
        if not self.judge_file(file_path):
            return None, None
        file_name = os.path.basename(file_path).split(".")[0]
        now_path = self.base_path + "\\" + file_name
        if os.path.exists(now_path):
            shutil.rmtree(now_path)
        if not os.path.exists(now_path):
            os.mkdir(now_path)
        if file_path is None:
            return None, None
        with zipfile.ZipFile(file_path) as zf:
            zf.extractall(path=now_path)
            zip_list = zf.filelist
            for files in zip_list:
                old_name = files.filename
                try:
                    new_name = old_name.encode("cp437").decode("gbk")
                except:
                    new_name = old_name.encode("utf-8").decode("utf-8")
                os.rename(now_path + "\\" + old_name, now_path + "\\" + new_name)
        return now_path, file_name


if __name__ == '__main__':
    file_list = ['D:\\Users\\v-jiawei.li\\PycharmProjects\\pythonProject\\行程码1.zip',
                 "D:\\Users\\v-jiawei.li\\PycharmProjects\\pythonProject\\行程码2.zip"]
    ocr = OcrImage()
    ocr.outer_process(file_list)
    # ocr1.outer_process(file_list_2)
