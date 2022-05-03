from flask import Flask, request, Response
import argparse
import zmq
import cv2
import base64
import threading
import pyttsx3

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
    try:
        content = request.get_json(force=True)
    except Exception as e:
        print(e)
        return Response('JSON is not parsable', status=500)
    pyttsx3.speak("I will speak this text")
    return Response(status=200)


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
