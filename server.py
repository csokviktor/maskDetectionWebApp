import zmq
import time
import numpy as np
import cv2
import base64


#my own iterator class for the webstream
class LoadClient:
    def __init__(self, ip="tcp://*:5555", img_size=640):
        self.img_size = img_size
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)

        self.socket.bind("tcp://*:5555")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, np.compat.unicode(''))
    
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
        """
        # Padded resize
        img = letterbox(img0, new_shape=self.img_size)[0]
        # Convert
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)
        """
        return img_path, img0, None
    
    def __len__(self):
        return 0


def runServer():
    it = LoadClient()

    for img_path, img0, calami in it:
        cv2.imshow("Frame", img0)

runServer()


