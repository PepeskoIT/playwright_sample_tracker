import base64
from datetime import datetime
from functools import wraps
from logging import getLogger
from os.path import join, abspath

import aiofiles
import cv2 as cv
import pytesseract
from PIL import Image
from aiofiles import os as aos
from playwright.async_api import Error

from shop.definition import SHOP_FOLDERS

logger = getLogger("buy-bot")
DATE_FORMAT = "%d%m%Y_%H%M%S"


def recognize_text(image):
    #  edge preserving filter denoising 
    blur = cv.pyrMeanShiftFiltering(image, sp=8, sr=60)
    cv.imshow('dst', blur)
    #  grayscale image 
    gray = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)
    #  binarization setting threshold    if the adaptive threshold is yellow. 4 it won't be able to extract it. 
    ret, binary = cv.threshold(gray, 185, 255, cv.THRESH_BINARY_INV)
    print(f' threshold set by binarization ：{ret}')
    cv.imshow('binary', binary)
    #  logical operation makes the background white    the font is black for easy recognition. 
    cv.bitwise_not(binary, binary)
    cv.imshow('bg_image', binary)
    #  identify 
    test_message = Image.fromarray(binary)
    text = pytesseract.image_to_string(test_message)
    print(f' recognition result ：{text}')
    return text


async def dump_captcha(self):
    pass

async def resolve_captcha():
    pass


def load_captcha_img(path):
    cap = cv.VideoCapture(path)
    ret, img = cap.read()
    cap.release()
    cv.imshow('input image', img)
    return img


def captcha(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        self = args[0]
        date = str(datetime.utcnow().strftime(DATE_FORMAT))
        prefix_path = join(SHOP_FOLDERS[type(self).__name__], f"captcha")
        await aos.makedirs(prefix_path, exist_ok=True)

        ret = await f(*args, **kwargs)
        
        if self.captcha_locator:
            captcha_locator = self.page.locator(self.captcha_locator, has_text=self.captcha_text)
            try:
                await captcha_locator.text_content(timeout=100)
            except Error:
                pass
            else:
                logger.warning("Captcha detected")
                captcha_img = self.page.locator(self.captcha_img_locator)
                src = await captcha_img.get_attribute("src")
                src = src.replace('data:image/png;base64,', '').replace(' ', '+')
                imgdata = base64.b64decode(src)
                # response = urlopen(src)  # TODO: change me to async
                rel_captcha_img_path = join(prefix_path, f"captcha.png")
                async with aiofiles.open(rel_captcha_img_path, 'wb') as s:
                    await s.write(imgdata)
                # resolve
                abs_captcha_img_path = abspath(rel_captcha_img_path)
                cap = cv.VideoCapture(abs_captcha_img_path)
                ret, img = cap.read()
                cap.release()
                cv.imshow('input image', img)
                recognize_text(src)
                # img = cv2.imread(image)
                # gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # gry = img
                # (h, w) = gry.shape[:2]
                # gry = cv2.resize(gry, (w * 2, h * 2))
                # thr = cv2.adaptiveThreshold(gry, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
                # plt.imshow(thr)
                # # plt.show()
                # decoded = image_to_string(thr)
                # print(decoded)
        return ret
    return decorated
