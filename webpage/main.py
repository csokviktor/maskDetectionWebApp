from initialization import create_app
from parallelDetect import (
    setupDetection, initProcessObjects,
    processImage, runSubscriber,
    showProcessedImage)

def startApp(list, lock):
    try:
        app = create_app(list, lock)
        app.run()
    except Exception as e:
        print(e)

if __name__ == '__main__':
    #device, webcam, model, imgsz, names, colors, half = setupDetection(source = "client", weights= r"C:\Users\csokviktor\Desktop\maskdetection\best_maskdetv2_2_strip.pt",
    #                    deviceName = '0')
    #managerList, processedList, managerLock, processedLock, pool = initProcessObjects()
    #processedList.insert(0, None)
    #processedList.insert(1, None)
    #pool.apply_async(runSubscriber, args=("tcp://127.0.0.1:5554", 0, managerList, managerLock))
    #pool.apply_async(runSubscriber, args=("tcp://127.0.0.1:5555", 1, managerList, managerLock))
    #pool.apply_async(startApp, args=(processedList, processedLock))
    #pool.apply_async(showProcessedImage, args=(processedList, processedLock))
    #processImage(managerList, processedList, processedLock, device, webcam, model, imgsz, names, colors, half)
    app = create_app()
    app.run()