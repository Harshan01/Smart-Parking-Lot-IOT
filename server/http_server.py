# app.py
import argparse
import base64
from io import BytesIO

from flask import Flask, request, jsonify

import numpy as np
from PIL import Image
import torch


app = Flask(__name__)

model = torch.hub.load('../yolov5', 'custom',
                       path='models/yolov5s_b50_s416.pt',
                       source='local')

parser = argparse.ArgumentParser()
parser.add_argument('--test', dest='test', action='store_true',
                    help='Test model using demo sample')
parser.add_argument('--imgshow', dest='imgshow', action='store_true',
                    help='Show rendered object detection output on screen')
args = parser.parse_args()


def detect_image(img):
    # Yolov5 object detection model
    results = model(img)
    results.render()

    if args.imgshow:
        img = Image.fromarray(results.imgs[0])
        img.resize(
            (img.size[0] * 800 // img.size[1], 800),
            Image.BICUBIC
        ).show()

    detections = []
    for id, det in results.pandas().xyxyn[0].iterrows():
        if (det['xmin'] + det['xmax'])/2 <= 0.5:
            slot_no = 1
        else:
            slot_no = 2
        detections.append(
            {
                'id': id,
                'vehicle_type': det['name'],
                'slot_no': slot_no
            }
        )
    return detections


def test_image():
    import os
    for file in os.listdir('data/test_samples'):
        img = Image.open('data/test_samples/' + file)
        # img.show()
        print(detect_image(img))


@app.route('/recognize', methods=['POST'])
def recognize():
    data = request.get_json()
    img = BytesIO(base64.b64decode(data['image']))
    img = np.array(Image.open(img))

    detections = detect_image(img)
    response = {
        "detections": detections
    }
    return jsonify(response)


if __name__ == '__main__':
    if args.test:
        test_image()
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)
