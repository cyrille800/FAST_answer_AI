import tkinter as tk
from tkinter import Toplevel, Canvas
from PIL import ImageGrab
import time
import os

class ScreenCaptureTool:
    def __init__(self, root):
        self.root = root
        self.start_x = None
        self.start_y = None
        self.rectangle = None
        self.win = None
        self.canvas = None
        self.img_screens = []
        self.num_screen = 0
        self.folder = ""

    def start_capture(self, fol, c):
        self.num_screen = c
        self.folder = fol
        # Crée une fenêtre transparente pour la sélection de zone
        self.win = Toplevel(self.root)
        self.win.attributes('-fullscreen', True)
        self.win.attributes('-alpha', 0.2)  # Fenêtre semi-transparente

        self.canvas = Canvas(self.win, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Lie les événements de la souris à la toile
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        # Initialise le début du rectangle de sélection
        self.start_x, self.start_y = event.x, event.y
        self.rectangle = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline='#ccc', width=2, fill='white')

    def on_drag(self, event):
        # Redessine le rectangle pour suivre la souris
        self.canvas.coords(self.rectangle, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        # Capture la zone sélectionnée et ferme la fenêtre
        self.capture_area(self.start_x, self.start_y, event.x, event.y)
        self.win.destroy()

    def capture_area(self, x1, y1, x2, y2):
        # Ajuste les coordonnées en cas de sélection inverse
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        
        img.save(f"screenshot{self.num_screen}.png")
        
        if not os.path.exists(f"{self.folder}"):
            os.makedirs(f"{self.folder}")
            
        img.save(f"{self.folder}/screenshot{self.num_screen}.png")
        
        self.img_screens.append(f"screenshot{self.num_screen}.png")
        