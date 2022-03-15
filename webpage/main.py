from initialization import create_app
from parallelDetect import (
    setupDetection, initProcessObjects,
    processImage, showProcessedImage, showImage)

import time

def startApp(inpDict, inpLock, procDict, procLock):
    try:
        app = create_app(inpDict, inpLock, procDict, procLock)
        app.run()
    except Exception as e:
        print(e)

if __name__ == '__main__':
    #device, webcam, model, imgsz, names, colors, half = setupDetection(source = "client", weights= r"C:\Users\csokviktor\Desktop\maskdetection\best_maskdetv2_2_strip.pt",
    #                    deviceName = '0')
    inputDict, processedDict, inputLock, processedLock, pool = initProcessObjects()
    #pool.apply_async(runSubscriber, args=("tcp://127.0.0.1:5554", 0, managerList, managerLock))
    #pool.apply_async(runSubscriber, args=("tcp://127.0.0.1:5555", 1, managerList, managerLock))
    pool.apply_async(startApp, args=(inputDict, inputLock, processedDict, processedLock))
    pool.apply_async(showImage, args=(inputDict, inputLock))
    time.sleep(100000)
    #processImage(inputDict, processedDict, processedLock, device, webcam, model, imgsz, names, colors, half)