import sys
import os, imageio, datetime
import numpy as np
from idx2numpy import convert_to_file
from qimage2ndarray import byte_view
from skimage import img_as_ubyte
from skimage.transform import resize
from configparser import ConfigParser
from PyQt5 import QtCore, QtGui as qt, QtWidgets as qw

data_path = os.path.abspath(os.path.dirname(__file__))
temp_fullpath = os.path.join(data_path, '.temp.png')

conf_fullpath = os.path.join(data_path, 'config.ini')
conf = ConfigParser()
conf.read(conf_fullpath)
windowWidth_px = int(conf.get('label', 'windowWidth_px'))
windowHeight_px = int(conf.get('label', 'windowHeight_px'))
imgSize_px = int(conf.get('label', 'imgSize_px'))
penWidth_px  = int(conf.get('label', 'penWidth_px'))
labelsStr = conf.get('label', 'labels')

startTimeStr = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M_") + str(imgSize_px) + "x" + str(imgSize_px) + "px_uint8"

class MainWindow(qw.QWidget):
    labelIndex = 0
    imgStorage = []
    lblStorage = []

    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, windowWidth_px, windowHeight_px)
        
        widgetBox = qw.QHBoxLayout()
        widgetBox.setSpacing(0)
        widgetBox.setContentsMargins(0, 0, 0, 0)

        drawWidgetSize = min(windowWidth_px, windowHeight_px)
        drawWidget = DrawWidget(self, drawWidgetSize, drawWidgetSize, penWidth_px, imgSize_px)
        controlWidget = ControlWidget(self, max(windowWidth_px, windowHeight_px) - drawWidgetSize, drawWidgetSize)
        
        widgetBox.addWidget(drawWidget)
        widgetBox.addWidget(controlWidget)

        controlWidget.setAutoFillBackground(True)
        p = controlWidget.palette()
        p.setColor(controlWidget.backgroundRole(), QtCore.Qt.darkGray)
        controlWidget.setPalette(p)
        controlWidget.updateLabel(labelsStr[0])

        self.setLayout(widgetBox)
        drawWidget.show()
        controlWidget.show()

        self.drawWidget = drawWidget
        self.controlWidget = controlWidget

    def imgReceived(self, imgQImageGreyscale8):
        imgNumpy = np.ndarray(shape=(imgQImageGreyscale8.width(), imgQImageGreyscale8.height(), 1), dtype=np.uint8)
        for v in range(imgQImageGreyscale8.height()):
            for u in range(imgQImageGreyscale8.width()):
                imgNumpy[v, u, 0] = qt.qGray(imgQImageGreyscale8.pixel(u, v))
        self.processImage(imgNumpy)

    def processImage(self, imgNumpy):
        (u_min, u_diff, u_max, v_min, v_diff, v_max, uv_diff, processed) = self.getSymbolBounds(imgNumpy)
        if (not processed):
            return

        lowerPad = int(uv_diff / 2)
        upperPad = round(uv_diff / 2)

        img_boundingBox = imgNumpy[v_min:v_max, u_min:u_max]
        if (u_diff < v_diff):
            img_boundingBox = np.pad(img_boundingBox, [(0,0),(lowerPad,upperPad),(0,0)], 'constant')
        else:
            img_boundingBox = np.pad(img_boundingBox, [(lowerPad,upperPad),(0,0),(0,0)], 'constant')

        img_resized = img_as_ubyte(resize(img_boundingBox, (imgSize_px, imgSize_px), anti_aliasing=True, mode='constant'))
        # imageio.imwrite('.img_resized.png', img_resized[:, :])
        
        self.imgStorage.append(img_resized)
        self.lblStorage.append(self.labelIndex)
        self.updateLabels(1)

    def updateLabels(self, sign):
        self.labelIndex = (self.labelIndex + sign) % len(labelsStr)
        self.controlWidget.updateLabel(labelsStr[self.labelIndex]) 

    def getSymbolBounds(self, img):
        (u_min, u_max, v_min, v_max) = (img.shape[1], 0, img.shape[0], 0)
        processed = False
        for v in range(img.shape[0]):
            for u in range(img.shape[1]):
                if (img[v,u,0] != 0):
                    processed = True
                    if (v < v_min):
                        v_min = v
                    if (v > v_max):
                        v_max = v
                    if (u < u_min):
                        u_min = u
                    if (u > u_max):
                        u_max = u      
        
        u_diff = u_max-u_min
        v_diff = v_max-v_min
        uv_diff = max(u_diff, v_diff) - min(u_diff, v_diff)
        
        return (u_min, u_diff, u_max, v_min, v_diff, v_max, uv_diff, processed)
    
    def rollbackImage(self):
        del self.imgStorage[-1]
        del self.lblStorage[-1]
        self.updateLabels(-1)

    def writeData(self):
        images = np.array(self.imgStorage, dtype=np.uint8)
        labels = np.array(self.lblStorage, dtype=np.uint8)
        convert_to_file(os.path.join(data_path, startTimeStr + "_" + str(len(images)) + "_img.idx"), images)
        convert_to_file(os.path.join(data_path, startTimeStr + "_" + str(len(images)) + "_lbl-" + labelsStr + ".idx"), labels)


class DrawWidget(qw.QWidget):
    def __init__(self, parent, widgetWidth_px, widgetHeight_px, penWidth_px, imgSize_px):
        qw.QWidget.__init__(self)
        self.parentWidget = parent
        self.drawing = False
        self.penWidth = penWidth_px

        qSize = QtCore.QSize(widgetWidth_px, widgetHeight_px)
        self.qImage = qt.QImage(qSize, qt.QImage.Format_Grayscale8)
        self.qImage.fill(0)

        self.label_imageDisplay = qw.QLabel(self)
        self.renderImage()
        self.label_imageDisplay.show()

        self.show()
        
    def renderImage(self):
        qPixmap = qt.QPixmap(qt.QPixmap.fromImage(self.qImage))
        self.label_imageDisplay.setPixmap(qPixmap)

    def mousePressEvent(self, event):
        if (event.button() == QtCore.Qt.LeftButton):
            self.prevPoint = event.pos()
            self.drawing = True

    def mouseMoveEvent(self, event):
        if (self.drawing):
            self.drawLineTo(event.pos())
            self.renderImage()

    def mouseReleaseEvent(self, event):
        if (event.button() == QtCore.Qt.LeftButton):
            self.drawLineTo(event.pos())
            self.drawing = False
            #self.qImage.save('C:\\Users\\Joachim\\Desktop\\Projects\\Mini LCD Home Control\\LCDraw-PyQt-V2\\out.png')
            self.parentWidget.imgReceived(self.qImage) # uint8
            self.qImage.fill(0)
            self.renderImage()

    def drawLineTo(self, point):
        painter = qt.QPainter(self.qImage)
        painter.setPen(qt.QPen(QtCore.Qt.white, self.penWidth, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawLine(self.prevPoint, point)

        rad = (self.penWidth / 2) + 2
        self.update(QtCore.QRect(self.prevPoint, point).normalized().adjusted(-rad, -rad, +rad, +rad))
        self.prevPoint = point


class ControlWidget(qw.QWidget):
    def __init__(self, parent, widgetWidth_px, widgetHeight_px):
        qw.QWidget.__init__(self)
        controlBox = qw.QVBoxLayout()
        controlBox.setSpacing(0)
        controlBox.setContentsMargins(0, 0, 0, 0)

        redoButton = qw.QPushButton("undo")
        writeButton = qw.QPushButton("write data")
        labelLabel = qw.QLabel("")

        redoButton.setFont(qt.QFont('SansSerif', widgetHeight_px/10))
        writeButton.setFont(qt.QFont('SansSerif', widgetHeight_px/10))
        labelLabel.setFont(qt.QFont('SansSerif', widgetHeight_px/5))
        labelLabel.setAlignment(QtCore.Qt.AlignCenter)

        redoButton.clicked.connect(lambda:parent.rollbackImage())
        writeButton.clicked.connect(lambda:parent.writeData())
        
        controlBox.addWidget(redoButton)
        controlBox.addWidget(writeButton)
        controlBox.addWidget(labelLabel)

        self.setLayout(controlBox)

        self.redoButton = redoButton
        self.writeButton = writeButton
        self.labelLabel = labelLabel

    def updateLabel(self, lbl):
        self.labelLabel.setText(lbl)
        
app = qw.QApplication(sys.argv)
mw = MainWindow()
mw.setWindowFlags(QtCore.Qt.FramelessWindowHint)
mw.show()
sys.exit(app.exec_())
