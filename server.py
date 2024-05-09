import argparse
import json
import logging
import os
import time
import uuid

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from util import getAccessToken, optimizeText, generateVideo, queryVideo


app = Flask(__name__)
# 添加静态文件夹规则
app.static_folder = 'static'  # 默认的静态文件夹
app.static_url_path = '/static'  # 默认静态文件夹的 URL 路径前缀

# 添加额外的静态文件夹
app.add_url_rule('/videos/<path:filename>', endpoint='videos', view_func=app.send_static_file)
app.add_url_rule('/images/<path:filename>', endpoint='images', view_func=app.send_static_file)
CORS(app)

parser = argparse.ArgumentParser()
parser.add_argument("-config", help="your config file", default="config/config.json", type=str)
args = parser.parse_args()

with open(args.config, encoding='utf-8') as f:
    config = json.load(f)

appConfig = config.get('app')

baiduConfig = config.get('baidu')
videoConfig = config.get('video')

baiduAccessToken = getAccessToken(baiduConfig['accessTokenUrl'], baiduConfig['apiKey'], baiduConfig['secretKey'])
logger = logging.getLogger('mylogger')
logger.setLevel(logging.DEBUG)

# 创建FileHandler对象
fh = logging.FileHandler('utgvt.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

# 将FileHandler对象添加到Logger对象中
logger.addHandler(fh)



@app.route('/api/generate_video', methods=['POST'])
def generate_video():
    if 'text' not in request.json or 'images' not in request.json:
        return jsonify({'code': 1001, 'message': 'illegal param'})

    text = request.json['text']
    images = request.json['images']

    job_id = generateVideo(images, text, baiduConfig, videoConfig, baiduAccessToken)

    time.sleep(5)

    video_url = queryVideo(baiduConfig, baiduAccessToken, job_id)

    video_url = f"videos/飞书20240504-161305.mp4"  # just for test
    
    res = {}
    res['video'] = video_url

    return jsonify({'code': 1000, 'message': 'success', 'data': res})
    

@app.route('/api/optimize_text', methods=['POST'])
def optimize_text():
    if 'text' not in request.json:
        return jsonify({'code': 1001, 'message': 'illegal param'})

    raw_text = request.json['text']

    data = {}
    optimized_text = optimizeText(baiduConfig, baiduAccessToken, raw_text)
    data['text'] = optimized_text

    return jsonify({'code': 1000, 'message': 'success', 'data': data})


@app.route('/api/upload_images', methods=['POST'])
def upload():
    # 检查请求中是否有文件
    if 'images' not in request.files:
        return jsonify({'code': 1001, 'message': 'illegal param'})
    
    images = request.files.getlist('images')
    image_ids = []

    # 检查文件类型并保存
    for image in images:
        if image.filename == '':
            return jsonify({'code': 1001, 'message': 'illegal param'})

        if image and allowed_file(image.filename):
            image_id = uuid.uuid4()
            filename = secure_filename(image.filename)
            ext = get_file_extension(filename)
            new_filename = str(image_id) + '.' + ext
            image.save(os.path.join('images', new_filename))
            image_ids.append(new_filename)
        else:
            return jsonify({'code': 1001, 'message': 'illegal param'})

    return jsonify({'code': 1000, 'message': 'success', 'data': {'images': image_ids}})



def allowed_file(filename):
    # 检查文件类型是否为图片
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()


if __name__ == '__main__':
    app.run(host=appConfig['host'], port=appConfig['port'])