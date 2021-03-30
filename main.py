import os
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtGui import QPainter
from PySide2.QtCore import Qt
from PIL import Image, ImageQt, ImageFilter, ImageDraw, ImageFont, ImageColor, ImageFilter
from PyQt5.QtGui import QPixmap


class Mark:
    def __init__(self, pos_x=100, pos_y=100, rotate=0, mark_text='MY MARK'):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rotate = rotate
        self.mark_text = mark_text

    def __repr__(self):
        return f" x={self.pos_x}, y={self.pos_y}, rotate={self.rotate}, text={self.mark_text}"


class MainWindow(QtWidgets.QWidget):
    def __init__(self, ctx):
        super(MainWindow, self).__init__()
        self.ctx = ctx
        self.mark = Mark()
        self.setWindowTitle("PyWaterMark")
        self.setup_Ui()
        self.font = ImageFont.truetype("arial.ttf", 200)

        self.colors = {'red': [255, 0, 0],
                       'green': [0, 255, 0],
                       'blue': [0, 0, 255],
                       'white': [255, 255, 255],
                       'black': [0, 0, 0]}

    def setup_Ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layout()
        self.addWidgetsToLayouts()
        self.setup_connections()

    def create_widgets(self):
        self.btn_open = QtWidgets.QPushButton('Open image')
        self.btn_mark = QtWidgets.QPushButton('Create Mark')
        self.btn_save = QtWidgets.QPushButton('Save')
        self.lbl_image = QtWidgets.QLabel()
        self.le_mark = QtWidgets.QLineEdit(str(self.mark.mark_text))
        self.le_rotate = QtWidgets.QLineEdit(str(self.mark.rotate))
        self.le_x = QtWidgets.QLineEdit(str(self.mark.pos_x))
        self.le_y = QtWidgets.QLineEdit(str(self.mark.pos_y))
        self.le_opacity = QtWidgets.QLineEdit("100")
        self.label_pos_x = QtWidgets.QLabel('X Coordonnate')
        self.label_pos_y = QtWidgets.QLabel('Y Coordonnate')
        self.label_rotate = QtWidgets.QLabel('Angle of rotation')
        self.label_mark = QtWidgets.QLabel('Write your mark here : ')
        self.label_opacity = QtWidgets.QLabel('Opacity %')
        self.label_drop_info = QtWidgets.QLabel("^ Drop image in the interface")
        self.label_color_box = QtWidgets.QLabel('Choose the color')
        self.color_box = QtWidgets.QComboBox()

    def modify_widgets(self):
        stylesheet = """
                        QWidget {}
                        QPushButton {}
                        QTextEdit { background-color : rgb(255,255,255) ; border : none ; font : Time ; font-size : 20px ; }
                        QLabel {color : black ; font-style: italic}
                        QLineEdit {font:Time}
                    """
        self.setStyleSheet(stylesheet)
        self.label_drop_info.setVisible(False)

        self.color_box.addItems(['red', 'blue', 'green', 'white', 'black'])
        self.setAcceptDrops(True)

    def create_layout(self):
        self.btn_layout = QtWidgets.QHBoxLayout()
        self.modif_layout = QtWidgets.QVBoxLayout()
        self.main_layout = QtWidgets.QGridLayout(self)

    def addWidgetsToLayouts(self):
        self.btn_layout.addWidget(self.btn_open)
        self.btn_layout.addWidget(self.btn_mark)
        self.btn_layout.addWidget(self.btn_save)
        self.modif_layout.addWidget(self.label_mark)
        self.modif_layout.addWidget(self.le_mark)
        self.modif_layout.addWidget(self.label_rotate)
        self.modif_layout.addWidget(self.le_rotate)
        self.modif_layout.addWidget(self.label_pos_x)
        self.modif_layout.addWidget(self.le_x)
        self.modif_layout.addWidget(self.label_pos_y)
        self.modif_layout.addWidget(self.le_y)
        self.modif_layout.addWidget(self.label_opacity)
        self.modif_layout.addWidget(self.le_opacity)
        self.modif_layout.addWidget(self.label_color_box)
        self.modif_layout.addWidget(self.color_box)
        self.main_layout.addLayout(self.btn_layout, 0, 0, 1, 1)
        self.main_layout.addWidget(self.lbl_image, 1, 0, 2, 2)
        self.main_layout.addLayout(self.modif_layout, 1, 2, 1, 2)
        self.main_layout.addWidget(self.label_drop_info, 3, 0, 1, 1)

    def setup_connections(self):
        self.btn_open.clicked.connect(self.open_image)
        self.btn_mark.clicked.connect(self.draw_mark)
        self.btn_save.clicked.connect(self.save_img)

    def dragEnterEvent(self, event):
        self.label_drop_info.setVisible(True)
        event.accept()

    def dragLeaveEvent(self, event):
        self.label_drop_info.setVisible(False)

    def dropEvent(self, event):
        event.accept()
        for url in event.mimeData().urls():
            self.image_path = url.toLocalFile()
            self.image = Image.open(self.image_path)
            self.update_pixmap()
        self.label_drop_info.setVisible(False)

    def open_image(self):
        self.image_path = QtWidgets.QFileDialog.getOpenFileName(self, ('Open Image (*.jpg)'))[0]
        self.image = Image.open(self.image_path)
        self.update_pixmap()

    def update_pixmap(self):
        self.image_qt = ImageQt.ImageQt(self.image)
        self.pixmap = QtGui.QPixmap(self.image_qt)
        self.lbl_image.setPixmap(
            self.pixmap.scaled(self.lbl_image.size(), QtCore.Qt.KeepAspectRatio))  # , QtCore.Qt.SmoothTransformation))
        # print(self.lbl_image.size().height(), self.lbl_image.size().width())

    def clear_pixmap(self):
        self.image = Image.open(self.image_path)
        self.update_pixmap()

    def draw_mark(self):

        try:
            self.clear_pixmap()
            color = self.color_box.itemText(self.color_box.currentIndex())
            self.mark.pos_x = int(self.le_x.text())
            self.mark.pos_y = int(self.le_y.text())
            self.mark.rotate = int(self.le_rotate.text())
            self.mark.mark_text = self.le_mark.text()
            opacity = int(256 * (int(self.le_opacity.text()) / 100))
            mark_width, mark_height = self.font.getsize(self.mark.mark_text)
            watermark = Image.new('RGBA', (self.image.width, self.image.height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark)
            draw.text((self.mark.pos_x, self.mark.pos_y),
                      fill=(self.colors[color][0], self.colors[color][1], self.colors[color][2], opacity),
                      font=self.font, text=self.mark.mark_text)
            watermark = watermark.rotate(self.mark.rotate, expand=1)
            self.image.paste(watermark, mask=watermark)
            self.update_pixmap()
        except AttributeError:
            pass

    def save_img(self):
        try:
            img_save = "marked_" + self.image_path.split('/')[-1]
            test = self.pixmap.save(img_save, quality=100)
            print(f"Save {img_save}")
        except AttributeError:
            pass


if __name__ == '__main__':
    app = QtWidgets.QApplication([])  # 1. Instantiate ApplicationContext
    window = MainWindow(ctx=app)
    window.resize(1920 / 4, 1200 / 2)
    window.show()
    app.exec_()