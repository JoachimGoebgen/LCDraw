import os
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.graphics import Color, Line, Rectangle
from ConfigParser import SafeConfigParser
from kivy.core.window import Window


class PaintWidget(Widget):
    
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
            self.export_to_png(".processing.bmp") #dirty but working
        self.canvas.clear()

class LCDrawApp(App):
    def build(self):
        cfg_full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.ini'))
        configParser = SafeConfigParser()
        configParser.read(cfg_full_path)
        print(configParser.get('base', 'windowWidth'))
        Window.size = (int(configParser.get('base', 'windowWidth')), int(configParser.get('base', 'windowHeight')))
        return MainBoxLayout()
        
class MainBoxLayout(BoxLayout):
    pass

class InfoBoxLayout(BoxLayout):
    pass
    
if __name__ == '__main__':
    LCDrawApp().run()
    
