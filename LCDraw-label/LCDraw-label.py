import os
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.graphics import Color, Line, Rectangle
from configparser import SafeConfigParser
from kivy.core.window import Window


cfg_full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.ini'))
configParser = SafeConfigParser()
configParser.read(cfg_full_path)

class LCDrawApp(App):
    def build(self):
        Window.size = (int(configParser.get('base', 'windowWidth')), int(configParser.get('base', 'windowHeight')))
        return MainBox()
   
class PaintWidget(Widget):
    processing_full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.processing.png'))
    
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
            self.export_to_png(self.processing_full_path) #dirty but working
            self.parent.ids.dataBox.switch_label()
        self.canvas.clear()
     
class DataBox(BoxLayout):
    labelIndex = 0
    labels = configParser.get('base', 'labels')

    def switch_label(self):
        self.labelIndex = (self.labelIndex + 1) % len(self.labels)
        self.parent.ids.labelLabel.text = self.labels[self.labelIndex]
    
class MainBox(BoxLayout):
    pass

if __name__ == '__main__':
    LCDrawApp().run()



    
