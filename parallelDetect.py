import argparse
import os
import shutil
import time
import requests
import json
import multiprocessing
import base64
import cv2
import torch
import torch.backends.cudnn as cudnn
import numpy as np
from numpy import random
from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages, LoadClient
from utils.general import (
    check_img_size, non_max_suppression, apply_classifier, scale_coords, xyxy2xywh, plot_one_box, strip_optimizer)
from utils.torch_utils import select_device, load_classifier, time_synchronized


def showImage(managerDict, lock):
    print("starting show image")
    while True:
        with lock:
            if len(managerDict.keys()) == 0:
                continue
            try:
                for key, data in managerDict.items():
                    if data != "" and data != -1:
                        img = base64.b64decode(data)
                        npimg = np.frombuffer(img, dtype=np.uint8)
                        img0 = cv2.imdecode(npimg, 1)
                        cv2.imshow(f"Frame {key}", img0)
                        if cv2.waitKey(10) == ord('q'):  # q to quit
                            cv2.destroyAllWindows()
                            raise StopIteration
            except Exception as e:
                print(e)


def showProcessedImage(showDict, lock):
    print("starting show image processed")
    while True:
        with lock:
            if len(showDict.keys()) == 0:
                continue
            for k, value in showDict.items():
                try:
                    cv2.imshow(f"Frame {k}", value)
                    if cv2.waitKey(10) == ord('q'):  # q to quit
                        cv2.destroyAllWindows()
                        raise StopIteration
                except Exception as e:
                    print(e)
                    continue


def runSubscriber(ip, id, inputDict, lock):
    it = LoadClient(ip=ip)
    with lock:
        inputDict[id] = ""
    for img_path, img, img0, valami, message in it:
        try:
            with lock:
                if inputDict[id] == -1:
                    return
                inputDict[id] = message
        except Exception as e:
            print(e)


def initProcessObjects():
    inputDict = multiprocessing.Manager().dict()
    processedDict = multiprocessing.Manager().dict()
    inputLock = multiprocessing.Manager().Lock()
    processedLock = multiprocessing.Manager().Lock()
    pool = multiprocessing.Pool(multiprocessing.cpu_count())

    return inputDict, processedDict, inputLock, processedLock, pool


def sendNotificationData(url, cameraID, status):
    data = {'cameraID': cameraID, 'status': status}
    requests.post(url, json=json.dumps(data))


def setupDetection(imgs: int = 640, out: str = "inference/output",
                   source: str = "0",
                   weights: str = r"C:\Users\csokviktor\Desktop\maskdetectionv2\runs\exp1_maskdetv2_2\weights\best_maskdetv2_2_strip.pt",
                   deviceName: str = "0"):
    # Initialize
    webcam = source == '0' or source.startswith('rtsp') or source.startswith('http') or source.endswith('.txt')

    device = select_device(deviceName)
    if os.path.exists(out):
        shutil.rmtree(out)  # delete output folder
    os.makedirs(out)  # make new output folder
    half = device.type != 'cpu'  # half precision only supported on CUDA

    # Load model
    model = attempt_load(weights, map_location=device)  # load FP32 model
    imgsz = check_img_size(imgs, s=model.stride.max())  # check img_size
    if half:
        model.half()  # to FP16

    # Get names and colors
    names = model.module.names if hasattr(model, 'module') else model.names
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(names))]

    return device, webcam, model, imgsz, names, colors, half


def setupDataLoader(webcam=False, source: str = "0", ip: str = ""):
    # Set Dataloader
    if webcam:
        view_img = False
        cudnn.benchmark = True  # set True to speed up constant image size inference
        dataset = LoadStreams(source, img_size=imgsz)
    elif source == "client":
        view_img = False
        cudnn.benchmark = True  # set True to speed up constant image size inference
        dataset = LoadClient(img_size=imgsz, ip=ip)
    else:
        save_img = False
        dataset = LoadImages(source, img_size=imgsz)

    return dataset


def processImage(inputDict, processedDict, lock, device, webcam, model, imgsz, names, colors, half,
                 augment: bool = True, conf_thres: float = 0.4, iou_thres: float = 0.5, classes=None,
                 agnostic_nms=True):
    from utils.datasets import letterbox
    print("starting processing")

    with torch.no_grad():
        # Run inference
        t0 = time.time()
        img = torch.zeros((1, 3, imgsz, imgsz), device=device)  # init img
        _ = model(img.half() if half else img) if device.type != 'cpu' else None  # run once
        while True:
            for key, value in inputDict.items():
                if value == "" or value == -1:
                    continue

                img = base64.b64decode(value)
                npimg = np.frombuffer(img, dtype=np.uint8)
                img0 = cv2.imdecode(npimg, 1)
                path = f"Frame{key}"

                # Padded resize
                img = letterbox(img0, new_shape=imgsz)[0]
                # Convert
                img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
                img = np.ascontiguousarray(img)

                img = torch.from_numpy(img).to(device)
                img = img.half() if half else img.float()  # uint8 to fp16/32
                img /= 255.0  # 0 - 255 to 0.0 - 1.0
                if img.ndimension() == 3:
                    img = img.unsqueeze(0)

                # Inference
                t1 = time_synchronized()
                pred = model(img, augment=augment)[0]

                # Apply NMS
                pred = non_max_suppression(pred, conf_thres, iou_thres, classes=classes, agnostic=agnostic_nms)
                t2 = time_synchronized()

                # Process detections
                for j, det in enumerate(pred):  # detections per image
                    if webcam:  # batch_size >= 1
                        p, s, im0 = path[j], '%g: ' % j, img0[j].copy()
                    else:
                        p, s, im0 = path, '', img0

                    s += '%gx%g ' % img.shape[2:]  # print string
                    gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
                    if det is not None and len(det):
                        # Rescale boxes from img_size to im0 size
                        det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                        # Print results
                        for c in det[:, -1].unique():
                            n = (det[:, -1] == c).sum()  # detections per class
                            s += '%g %ss, ' % (n, names[int(c)])  # add to string
                            # add notification sending here

                        # Write results
                        for *xyxy, conf, cls in det:
                            if True:  # Add bbox to image
                                label = '%s' % (names[int(cls)])
                                plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=2)
                with lock:
                    processedDict[key] = im0
                """
                cv2.imshow(f"Frame {i}", im0)
                if cv2.waitKey(1) == ord('q'):  # q to quit
                    raise StopIteration
                """


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default='yolov4-p5.pt', help='model.pt path(s)')
    parser.add_argument('--source', type=str, default='inference/images', help='source')  # file/folder, 0 for webcam
    parser.add_argument('--output', type=str, default='inference/output', help='output folder')  # output folder
    parser.add_argument('--img-size', type=int, default=640, help='inference size (pixels)')
    parser.add_argument('--conf-thres', type=float, default=0.4, help='object confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.5, help='IOU threshold for NMS')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true', help='display results')
    parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --class 0, or --class 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--update', action='store_true', help='update all models')
    opt = parser.parse_args()

    with torch.no_grad():
        inputDict, processedDict, inputLock, processedLock, pool = initProcessObjects()
        processedDict[0] = None
        processedDict[1] = None
        print("Starting processes")
        pool.apply_async(runSubscriber, args=("tcp://127.0.0.1:5554", 0, inputDict, inputLock))
        pool.apply_async(runSubscriber, args=("tcp://127.0.0.1:5555", 1, inputDict, inputLock))
        pool.apply_async(showProcessedImage, args=(processedDict, processedLock))
        print("pools started")

        device, webcam, model, imgsz, names, colors, half = setupDetection(source="client",
                                                                           weights=r"C:\Users\csokviktor\Desktop\maskdetection\best_maskdetv2_2_strip.pt",
                                                                           deviceName='0')
        processImage(inputDict, processedDict, processedLock, device, webcam, model, imgsz, names, colors, half)
