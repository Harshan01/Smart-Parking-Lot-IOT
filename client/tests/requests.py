import requests


SERVER_IP = '192.168.43.92'
SERVER_PORT = 5000

def send_one_request():
    req = requests.post(f'http://{SERVER_IP}:{SERVER_PORT}/recognize', json={"Z": "Y"})
    if req.status_code == 200:
        res = req.json()
        # Do something with response
        print(res)


if __name__ == '__main__':
    send_one_request()

