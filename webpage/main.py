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
    inputDict, processedDict, inputLock, processedLock, pool = initProcessObjects()
    pool.apply_async(startApp, args=(inputDict, inputLock, processedDict, processedLock))
    # pool.apply_async(showImage, args=(inputDict, inputLock))
    # pool.apply_async(showProcessedImage, args=(processedDict, processedLock))
    setup_args = setupDetection(
       source="client",
       weights=r"C:\Users\csokviktor\Desktop\maskdetection\best_maskdetv2_2_strip.pt",
       deviceName='0')
    processImage(inputDict, processedDict, processedLock, *setup_args)