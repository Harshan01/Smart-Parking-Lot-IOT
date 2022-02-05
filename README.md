# Smart Parking Lot - IOT

Smart Parking Lot is built with an array of sensors (ultrasonic sensor, RGB camera) connected to the Raspberry Pi (client). Ideally, there are many such clients spread throughout the smart parking lot with different sensors. All the clients are connected to a local/remote server where the sensor data is processed and appropriate action is taken, or output is displayed to the user. The clients and server communicate using CoAP (Constrained Application Protocol) protocol.

* Server could be any machine capable of running inference on a PyTorch model
* Client is a Raspberry Pi (preferably Raspberry Pi 4)

The PyTorch model is trained on Vehicles class of OpenImages dataset using [Ultralytics YoloV5](https://github.com/ultralytics/yolov5). The trained model weights are saved in `server/models`.

### Client

In this case, client is a Raspberry Pi 4 with 2 LED lights, 1 ultrasonic sensor, and 1 RGB camera connected via GPIO and Camera Port respectively. When the ultrasonic sensor triggers (based on a threshold), the RGB camera is activated and sends the current frame periodically to the server.

`PIL` and `aiocoap` Python libraries need to be installed.

To run the client, copy the `client` folder onto the Raspberry Pi, and run the below command in the copied folder.

```bash
python3 sensors.py
```

### Server

The server receives the frame, preprocesses it using Pillow and runs the PyTorch model on it for detecting the vehicles. The detections are then sent back to the client and also displayed in the server side. This data can then be used to perform any appropriate action in the Smart Parking Lot.

To run the server, run the below command in the `server` folder.

```bash
python3 coap_server.py
```
