#!/usr/bin/env python
# -*-coding: utf-8-*-
from utils.ImageUploader import ImageUploader
from handlers.BaseHandler import BaseHandler
import locale


locale.setlocale(locale.LC_COLLATE, 'zh_CN.UTF-8')


class ImageBatchHandler(BaseHandler):
    def initialize(self, conf):
        super(ImageBatchHandler, self).initialize(conf)

    def get(self):
        self.render_with_user('upload_image.html', image_back_list=[],
                              image_back_strings='', image_urls='')

    def post(self):
        uploader = ImageUploader("baijingting")
        image_objs = self.get_argument('image_objs', '').strip("for_split")
        image_urls = self.get_argument('image_urls', '').strip().strip(',').strip('\n')
        image_obj_list = []
        image_url_list = []
        image_back_list = []
        image_back_strings = ""
        if image_urls:
            if "," in image_urls:
                image_url_list = image_urls.split(",")
            elif "\n" in image_urls:
                image_url_list = image_urls.split("\n")
            else:
                image_url_list.append(image_urls)
            for image_url in image_url_list:
                try:
                    back_image_url = uploader.trans_img(image_url.strip().strip("\r"))
                    image_back_list.append(back_image_url)
                except Exception:
                    image_back_list.append("error")
        elif image_objs:
            if "for_split" in image_objs:
                image_obj_list = image_objs.split("for_split")
            else:
                image_obj_list.append(image_objs)
            for image_obj in image_obj_list:
                single_image_obj = image_obj.split("img_width")[0]
                img_width = image_obj.split("img_width")[1].split("img_height")[0]
                img_height = image_obj.split("img_height")[1]
                try:
                    single_image_url = uploader.trans_img_local(single_image_obj, img_width, img_height)
                    image_back_list.append(single_image_url)
                except Exception:
                    image_back_list.append("error")
        if len(image_back_list) > 0:
            image_back_strings = "\n".join(image_back_list)
        self.render_with_user('upload_image.html', image_urls=image_urls,
                              image_back_list=image_back_list,
                              image_back_strings=image_back_strings)
