from flask import Flask, request
import argparse
import zmq
import cv2
import base64
import threading

app = Flask(__name__)

def transfer(ip):
    # initialize communication
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect(ip)
    while not flag.is_set() and camera.isOpened():
        mutex.acquire()
        ret, frame = camera.read()
        mutex.release()
        if ret:
            retval, buffer = cv2.imencode('.jpeg', frame)
            imstring = base64.b64encode(buffer)
            socket.send_string(imstring.decode("utf-8"))
            cv2.waitKey(10)
        if cv2.waitKey(1) & 0xff == 27:
            break
    flag.set()


@app.route("/play-notification", methods=['POST'])
def play_notification():
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Start camera client")
    parser.add_argument('--host', default='127.0.0.1', help='Host of the camera (127.0.0.1)')
    parser.add_argument('--port', default='5555', help='Port of the camera (5554)')
    args = parser.parse_args()

    camera = cv2.VideoCapture(0)
    mutex = threading.Lock()
    flag = threading.Event()

    ip_camera = f'tcp://{args.host}:{args.port}'
    host_server = f'{args.host}'
    port_server = int(args.port) + 1

    t = threading.Thread(target=transfer, args=(ip_camera,))
    t.start()
    app.run(host=host_server, port=port_server)
