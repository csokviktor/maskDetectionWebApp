from initialization import create_app
from detect import setupDetection
import time

app = create_app()


if __name__ == '__main__':
    setupDetection(source='0', weights=r"C:\Users\csokviktor\Desktop\egyetem\MSC\onlab\runs\exp1_maskdetv2_2\weights\best_maskdetv2_2_strip.pt",
                            deviceName='0')
    app.run()