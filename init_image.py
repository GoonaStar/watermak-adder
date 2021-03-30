from tkinter import *
from PIL import Image, ImageTk
import sys
import easygui


class Example(Frame):
    def __init__(self):
        super().__init__()

        self.loadImage()
        self.initUI()

    def loadImage(self):
        try:
            self.img = Image.open(self.open_file())
        except IOError:
            print("Unable to load image")
            sys.exit(1)

    def initUI(self):
        self.master.title("Label")

        image = ImageTk.PhotoImage(self.img)
        label = Label(self, image=image)

        label.image = image

        label.pack()
        self.pack()

    def open_file(self):
        self.input_file = easygui.fileopenbox(filetypes=["*.docx"])
        return self.input_file