from flask import Flask, request
import datetime
import requests
from threading import Timer
import os
import xmltodict
import time
import re

from statsStock import StatsStock

os.system("sudo phddns start")

stats_stock = StatsStock()

app = Flask(__name__)

# app.debug = True

access_token = ""

stock_day_map = {}

with open("AppID", 'r') as file:
    AppID = file.readline()

with open("AppSecret", 'r') as file:
    AppSecret = file.readline()


def update_time():
    stats_stock.update_time()
    t = Timer(60 * 60, update_time)
    t.start()


def get_access_token():
    r = requests.get(
        "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}".format(AppID,
                                                                                                         AppSecret))
    data = r.json()
    print(data)
    global access_token
    access_token = data['access_token']
    expires_in = data['expires_in']
    print(access_token, expires_in)
    t = Timer(int(int(expires_in) * 3 / 4), get_access_token)
    t.start()


@app.route('/')
def hello_world():
    return 'Hello, World!' + '<br /><br />' + str(datetime.datetime.now())


@app.route('/wx', methods=["GET", "POST"])
def get():
    if request.method == "GET":  # 判断请求方式是GET请求
        my_echostr = request.args.get('echostr')  # 获取携带的echostr参数
        return my_echostr
    else:
        # 表示微信服务器转发消息过来
        xml_str = request.data
        if not xml_str:
            return ""
        resp_dict = None
        re_content = "信息错误"
        # 对xml字符串进行解析
        xml_dict = xmltodict.parse(xml_str)
        xml_dict = xml_dict.get("xml")

        # 提取消息类型
        msg_type = xml_dict.get("MsgType")
        if msg_type == "text":  # 表示发送的是文本消息
            content = xml_dict.get("Content")
            if content == "清除缓存":
                global stock_day_map
                stock_day_map = {}
                re_content = "缓存已清除"
            elif re.fullmatch(r'\d{6}\.\w{2}', content):
                resp_dict = handle_stats_stock(xml_dict)
            else:
                re_content = "请输入 002581.SZ 这样格式的股票代码"

        if not resp_dict:
            # 构造返回值，经由微信服务器回复给用户的消息内容
            resp_dict = {
                "xml": {
                    "ToUserName": xml_dict.get("FromUserName"),
                    "FromUserName": xml_dict.get("ToUserName"),
                    "CreateTime": int(time.time()),
                    "MsgType": "text",
                    "Content": re_content,
                }
            }

        # 将字典转换为xml字符串
        resp_xml_str = xmltodict.unparse(resp_dict)
        # 返回消息数据给微信服务器
        return resp_xml_str


def handle_stats_stock(xml_dict):
    ts_code = xml_dict.get("Content")
    media_id = None
    if not stock_day_map.get(ts_code):
        stock_day_map.update({ts_code: {}})
    if not stock_day_map[ts_code].get(datetime.date.today()):
        stock_day_map[ts_code][datetime.date.today()] = None
        try:
            is_stats = stats_stock.query(ts_code=ts_code)
            if is_stats:
                returned_value = os.popen(
                    "curl -s -F media=@plot.png \"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={}&type=image\"".format(
                        access_token)).read()
                returned_value = eval(returned_value)
                media_id_ = returned_value['media_id']
                if media_id_:
                    media_id = media_id_
                    stock_day_map[ts_code][datetime.date.today()] = media_id
        except:
            pass
    else:
        media_id = stock_day_map[ts_code][datetime.date.today()]
    if media_id:
        # 构造返回值，经由微信服务器回复给用户的消息内容
        resp_dict = {
            "xml": {
                "ToUserName": xml_dict.get("FromUserName"),
                "FromUserName": xml_dict.get("ToUserName"),
                "CreateTime": int(time.time()),
                "MsgType": "image",
                "Image": {
                    "MediaId": media_id,
                }
            }
        }
        return resp_dict
    # 构造返回值，经由微信服务器回复给用户的消息内容
    resp_dict = {
        "xml": {
            "ToUserName": xml_dict.get("FromUserName"),
            "FromUserName": xml_dict.get("ToUserName"),
            "CreateTime": int(time.time()),
            "MsgType": "text",
            "Content": "is stock code\nbut no midea_id",
        }
    }
    return resp_dict


if __name__ == "__main__":
    t = Timer(60 * 60, update_time)
    t.start()

    get_access_token()

    app.run(host="0.0.0.0", port=5000)
