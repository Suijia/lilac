#!/usr/bin/env python
# -*-coding: utf-8-*-
import requests
import base64
from qiniu import Auth
import tornado.log
import hashlib
from PIL import Image
from io import BytesIO
import yaml


class ImageUploader:
    IMG_HOST = 'http://ohpskaj7l.bkt.clouddn.com/'
    # IMG_HOST = 'http://img.baijingting.top/'
    QINIU_HOST = 'http://up-z0.qiniu.com/'

    def __init__(self, bucket_name):
        conf = yaml.load(open('conf/service.yaml', 'r'))
        access_key = conf.get("qiniu_access", "")
        secret_key = conf.get("qiniu_secret", "")
        self.bucket_name = bucket_name
        self.token = ImageUploader.__generate_token_via_qiniu(bucket_name, access_key, secret_key)

    def trans_img(self, img_url):
        try:
            img_obj = requests.get(img_url, timeout=60)
            img = Image.open(BytesIO(img_obj.content))
            img_width = img.size[0]
            img_height = img.size[1]
        except Exception as e:
            tornado.log.app_log.warn("fetch img_url error: {0}".format(e))
            img_obj = requests.get(img_url, timeout=60)
            img = Image.open(BytesIO(img_obj.content))
            img_width = img.size[0]
            img_height = img.size[1]
        if img_obj and img_width and img_height:
            img_obj_rb = img_obj.content
            qi_niu_key = self.__generate_image_info_key(self.bucket_name, img_obj_rb, img_width, img_height)
            qi_niu_url = ImageUploader.QINIU_HOST
            qi_niu_data = {"Content-Type": "multipart/form-data", "token": self.token, "key": qi_niu_key}
            files = {"file": img_obj_rb}
            resp_qi_niu = requests.post(qi_niu_url, data=qi_niu_data, files=files)
            if resp_qi_niu.status_code == 200:
                resp_image_url = ImageUploader.IMG_HOST + qi_niu_key
                return resp_image_url
            else:
                return None
        else:
            return None

    def trans_img_local(self, img_obj_data, img_width, img_height):
        if img_obj_data.find(','):
            img_obj = img_obj_data.split(',')[1].encode('utf-8')
            img_obj_rb = base64.b64decode(img_obj)
            qi_niu_key = self.__generate_image_info_key(self.bucket_name, img_obj_rb, img_width, img_height)
            qi_niu_url = ImageUploader.QINIU_HOST
            qi_niu_data = {"Content-Type": "multipart/form-data", "token": self.token, "key": qi_niu_key}
            files = {"file": img_obj_rb}
            resp_qi_niu = requests.post(qi_niu_url, data=qi_niu_data, files=files)
            if resp_qi_niu.status_code == 200:
                resp_image_url = ImageUploader.IMG_HOST + qi_niu_key
                return resp_image_url
        else:
            return None

    @staticmethod
    def __generate_token_via_qiniu(bucket_name, access_key, secret_key):
        """Generate avatar info for given key"""
        q = Auth(access_key, secret_key)
        token = q.upload_token(bucket_name)
        return token

    @staticmethod
    def __generate_image_info_key(bucket_name, img_obj_rb, img_width, img_height):
        m = hashlib.md5()
        m.update(img_obj_rb)
        return "{0}/{1}_{2}_{3}.jpeg".format(bucket_name, m.hexdigest(), img_width, img_height)


if __name__ == '__main__':
    u = ImageUploader("baijingting")
    print u.trans_img("http://japan.xinhuanet.com/2016-05/30/135394822_14644198711071n.jpg")
