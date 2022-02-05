import os
import json
import time
import base64
import asyncio
# import requests
from io import BytesIO
from PIL import Image
import RPi.GPIO as GPIO
from threading import Thread

from aiocoap import Message, Context, POST


SERVER_IP = '192.168.43.92'
SERVER_PORT = 5000

THRESH_DIST = 10
N_SLOTS = 2

TRIG = 23
ECHO = 24
LIGHT1 = 8
LIGHT2 = 25


# def send_one_request(img):
#     req = requests.post(f'http://{SERVER_IP}:{SERVER_PORT}/recognize', json={"image": img})
#     if req.status_code == 200:
#         res = req.json()
#         return res


async def send_one_request(img):
    context = await Context.create_client_context()
    
    request_data = {"image": img}
    payload = json.dumps(request_data).encode('utf-8')

    request = Message(
            code=POST,
            payload=payload,
            uri=f"coap://{SERVER_IP}:{SERVER_PORT}/recognize")

    print(f'> Request sent to {SERVER_IP}:{SERVER_PORT}')

    response = await context.request(request).response

    print(f'> Response received from {SERVER_IP}:{SERVER_PORT}')

    response_data = json.loads(response.payload)
    return response_data


def get_img():
    # Save a still image to a temp file in RAM using rsapistill command
    image_path = "/dev/shm/_tmp_iot_img.jpg"
    os.system("raspistill -o " + image_path )

    # Read the image and convert to base64
    img = Image.open(image_path)
    buffered = BytesIO()
    img_base64 = img
    img_base64.save(buffered, format="JPEG")

    return base64.b64encode(buffered.getvalue()).decode('utf-8')


def get_distance():    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    # print("Distance Measurement In Progress")
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    GPIO.output(TRIG, False)

    # print("Waiting For Distance Sensor To Settle")
    # time.sleep(2)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    # print("Distance:", distance, "cm")
    GPIO.cleanup()
    return distance


async def blink_led(LIGHT):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LIGHT, GPIO.OUT)
    # print('> LEDs blinked once...')
    GPIO.output(LIGHT, GPIO.HIGH)
    time.sleep(5)
    # print('LEDs switched off...')
    GPIO.output(LIGHT, GPIO.LOW)


def detect_vehicles():
    print('Waiting for vehicle at entrance...')

    while True:
        dist = get_distance()
        if dist <= THRESH_DIST:
            print('\nVehicle detected at entrance!!!')
            
            # Blink status LED
            asyncio.run(blink_led(LIGHT1))

            time.sleep(1)
            
            #Get Image from camera
            print('> Capturing image from camera...')
            asyncio.run(blink_led(LIGHT2))
            img = get_img()
            
            #Send request to server and receive response
            response = asyncio.run(send_one_request(img))
            
            slot_info = dict([(idx, None) for idx in range(1, N_SLOTS+1)])

            print('\n> Detections:')
            for idx, det in enumerate(response['detections']):
                vehicle_type = det['vehicle_type']
                slot_no = det['slot_no']
                if slot_info[slot_no] is None or det['confidence'] > slot_info[slot_no]['confidence']:
                    slot_info[slot_no] = det

            if len(response['detections']) == 0:
                print('  * No detections...')
            else:
                n_empty = 0
                for idx, det in slot_info.items():
                    if det is not None:
                        vehicle_type = det['vehicle_type']
                        slot_no = det['slot_no']
                        print(f'  * Slot No. {idx}\t has vehicle type : {vehicle_type}')
                    else:
                        n_empty += 1
                        print(f'  * Slot No. {idx}\t is vacant')
                print(f'\n{n_empty} slot(s) are vacant')
            
            print('\nWaiting for vehicle at entrance...')

        time.sleep(0.2)

if __name__ == '__main__':
    detect_vehicles()

