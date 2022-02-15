import zmq
import time
import numpy as np
import cv2
import base64
import concurrent.futures
import multiprocessing

from utils.datasets import letterbox


#my own iterator class for the webstream
class LoadClient:
    def __init__(self, ip="tcp://localhost:5555", img_size=640):
        self.img_size = img_size
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.setsockopt(zmq.CONFLATE, 1)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, np.compat.unicode(''))
        self.socket.bind(ip)
    
    def __iter__(self):
        self.count = -1
        return self
    
    def __next__(self):
        self.count += 1
        if cv2.waitKey(1) == ord('q'):  # q to quit
            cv2.destroyAllWindows()
            raise StopIteration
        
        message = self.socket.recv_string()

        img = base64.b64decode(message)
        npimg = np.frombuffer(img, dtype=np.uint8)
        img0 = cv2.imdecode(npimg, 1)
        img_path = "client.jpg"

        # Padded resize
        img = letterbox(img0, new_shape=self.img_size)[0]
        # Convert
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)

        return img_path, img, img0, None, message
    
    def __len__(self):
        return 0


def runSubscriber(ip, id, managerList, lock):
    it = LoadClient(ip=ip)
    print("init")
    with lock:
        print("inside lock")
        managerList.insert(id, "")
    for img_path, img, img0, valami, message in it:
        with lock:
            managerList[id] = message
        print(f"img received from {ip}")
        #cv2.imshow("Frame", img0)

def showImage(managerList, lock):
    while True:
        with lock:
            for i, data in enumerate(managerList):
                if data != "":
                    img = base64.b64decode(data)
                    npimg = np.frombuffer(img, dtype=np.uint8)
                    img0 = cv2.imdecode(npimg, 1)
                    cv2.imshow(f"Frame {i}", img0)
                    if cv2.waitKey(10) == ord('q'):  # q to quit
                        cv2.destroyAllWindows()
                        raise StopIteration


if __name__ == "__main__":
    managerList = multiprocessing.Manager().list()
    lock = multiprocessing.Manager().Lock()
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    print("Starting processes")
    pool.apply_async(runSubscriber, args=("tcp://127.0.0.1:5554", 0, managerList, lock))
    pool.apply_async(runSubscriber, args=("tcp://127.0.0.1:5555", 1, managerList, lock))
    pool.apply_async(showImage, args=(managerList, lock))
    print("pools started")
    while True:
        time.sleep(2)
    print(managerList)
    #runServer("tcp://127.0.0.1:5554")