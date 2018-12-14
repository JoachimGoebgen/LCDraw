import os, imageio, numpy, scipy
from skimage.transform import resize
from configparser import ConfigParser
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.graphics import Color, Line, Rectangle
from kivy.core.window import Window

labelToCountDict = {}

temp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.img.png'))
conf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.ini'))
conf = ConfigParser()
conf.read(conf_path)

windowWidth = int(conf.get('base', 'windowWidth'))
windowHeight = int(conf.get('base', 'windowHeight'))
reSize_px = int(conf.get('base', 'imgSize_px'))


class LCDrawApp(App):
    def build(self):
        Window.size = (windowWidth, windowHeight)
        return MainBox()
   
class PaintWidget(Widget):
    paintWidgetSize_ratio = float(windowHeight) / windowWidth

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            with self.canvas:
                Color(1, 1, 1, 1)
                touch.ud['line'] = Line(points=(touch.x, touch.y), width=self.lineWidth)

    def on_touch_move(self, touch):
        if self.collide_point(touch.x, touch.y):
            touch.ud['line'].points += [touch.x, touch.y]

    def on_touch_up(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.export_to_png(temp_path) # if its stupid and it works, it aint stupid
            App.get_running_app().root.process_image()
        self.canvas.clear()


class DataBox(BoxLayout):
    dataBoxSize_ratio = 1 - float(windowHeight) / windowWidth


class MainBox(BoxLayout):
    labelIndex = 0
    labels = conf.get('base', 'labels')
    global labelToCountDict
    for char in labels:
        labelToCountDict[char] = 0

    def process_image(self):
        img = numpy.asarray(imageio.imread(temp_path))
        (u_min, u_mid, u_max, v_min, v_mid, v_max, size_half) = self.getSymbolBounds(img)
        if (u_min >= u_max or v_min >= v_max):
            return
        img_boundingBox = img[v_mid-size_half:v_mid+size_half, u_mid-size_half:u_mid+size_half, 0]
        img_resized = resize(img_boundingBox, (reSize_px, reSize_px), anti_aliasing=False)
        imageio.imwrite('.img_resized.png', img_resized[:, :])
        self.update_labels(1)

    def rollback_image(self):
        self.update_labels(-1)

    def update_labels(self, sign):
        self.labelIndex = (self.labelIndex + sign) % len(self.labels)
        self.ids.labelLabel.text = self.labels[self.labelIndex]    

    def getSymbolBounds(self, img):
        (u_min, u_max, v_min, v_max) = (img.shape[1], 0, img.shape[0], 0)
        for v in range(img.shape[0]):
            for u in range(img.shape[1]):
                if (img[v,u,0] != 0):
                    if (v < v_min):
                        v_min = v
                    if (v > v_max):
                        v_max = v
                    if (u < u_min):
                        u_min = u
                    if (u > u_max):
                        u_max = u                
        return (u_min, (u_max + u_min) / 2, u_max, v_min, (v_max + v_min) / 2, v_max, max(u_max - u_min, v_max - v_min) / 2)
    

if __name__ == '__main__':
    LCDrawApp().run()



    
