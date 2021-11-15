from initialization import create_app
from parallelDetect import setupDetection, initProcessObjects, processImage, runSubscriber
import time

app = create_app()

managerList = None
processedList = None
managerLock = None
processedLock = None
pool = None

if __name__ == '__main__':
    device, webcam, model, imgsz, names, colors, half = setupDetection(source = "client", weights= r"C:\Users\csokviktor\Desktop\maskdetection\best_maskdetv2_2_strip.pt",
                        deviceName = '0')
    managerList, processedList, managerLock, processedLock, pool = initProcessObjects()
    processImage(managerList, processedList, processedLock, device, webcam, model, imgsz, names, colors, half)
    app.run()