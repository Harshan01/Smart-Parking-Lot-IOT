# coal_server.py
import asyncio
import json

import aiocoap
import aiocoap.resource as resource


# app.py
import argparse
import base64
from io import BytesIO

import numpy as np
from PIL import Image
import torch


model = torch.hub.load('../yolov5', 'custom',
                       path='models/yolov5s_b50_s416.pt',
                       source='local')
model.conf = 0.5

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
    results_df = results.pandas()
    for idx, det in results_df.xyxyn[0].iterrows():
        if (det['xmin'] + det['xmax'])/2 <= 0.5:
            slot_no = 1
        else:
            slot_no = 2
        conf = det['confidence']
        detections.append(
            {
                'id': idx,
                'vehicle_type': det['name'],
                'slot_no': slot_no,
                'confidence': conf
            }
        )
    return detections


def test_image():
    import os
    for file in os.listdir('data/test_samples'):
        img = Image.open('data/test_samples/' + file)
        # img.show()
        print(detect_image(img))


class RecognizeResource(resource.Resource):

    def __init__(self):
        super().__init__()

    async def render_post(self, request):
        data = json.loads(request.payload)
        img = BytesIO(base64.b64decode(data['image']))
        img = np.array(Image.open(img))
        img = np.flipud(img)

        detections = detect_image(img)
        response = {
            "detections": detections
        }
        response = json.dumps(response).encode('utf-8')
        print(response)

        return aiocoap.Message(code=aiocoap.CHANGED, payload=response)


def main():
    root = resource.Site()
    root.add_resource(['recognize'], RecognizeResource())

    asyncio.Task(aiocoap.Context.create_server_context(
                 root, bind=('0.0.0.0', 5000)
                 ))

    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    if args.test:
        test_image()
    else:
        main()
