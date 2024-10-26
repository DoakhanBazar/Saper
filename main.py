import sys
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QApplication, QMainWindow
from random import randrange
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.flag_icon = QIcon('icon/flag.png')
        self.explosion_icon = QIcon('icon/explosion.png')
        self.timer_icon = QIcon('icon/timer.png')
        self.setWindowTitle("Сапёр")
        self.setGeometry(300, 300, 400, 300)

        # Параметры карты
        self.rows = 8
        self.cols = 8
        self.mines = 10
        self.create_mines_field()

        # Таймер
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.time_elapsed = 0
        self.first_click = True

        # Метка для времени
        self.time_label = QtWidgets.QLabel(self)
        self.time_label.setGeometry(300, 10, 80, 24)
        self.time_label.setText("Time: 0")

        self.time_icon = QtWidgets.QLabel(self)
        self.time_icon.setGeometry(200, 3 , 24, 24)
        self.time_icon.setStyleSheet("background-color: rgb(255, 255, 255);")
        #self.time_label.setIcon(self.time_icon)
        # Создание кнопок
        self.buttons = []  
        self.create_buttons()

        #Restart
        self.btn_restart = QtWidgets.QPushButton(self)
        self.btn_restart.setText('Restart')
        self.btn_restart.setGeometry(71, 200, 54, 24)
        self.btn_restart.setStyleSheet("background-color: #C0C0C0; color:#FF6347;")
        self.btn_restart.clicked.connect(self.re_start)

        self.game_status = True
        self.cell_states = [['empty' for _ in range(self.cols)] for _ in range(self.rows)]

    def create_buttons(self):
        for row in range(self.rows):
            button_row = []
            for col in range(self.cols):
                btn = QtWidgets.QPushButton(self)
                btn.setText(' ')
                btn.setGeometry(3 + col * 24, 3 + row * 24, 24, 24)
                btn.setStyleSheet("background-color: #2F4F4F; color:#A0522D;")
                btn.installEventFilter(self)
                btn.setObjectName(f"btn_{row * self.cols + col}")
                button_row.append(btn)
            self.buttons.append(button_row)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            # Получаем координаты кнопки
            clicked_button_name = obj.objectName()
            clicked_button = int(clicked_button_name[4:])
            m = clicked_button % self.cols
            n = clicked_button // self.cols

            button_value = self.GetElementValue(obj)
            if self.game_status:
                if event.button() == QtCore.Qt.LeftButton:
                    if self.first_click:
                        self.timer.start(1000)
                        self.first_click = False

                    if self.cell_states[n][m] == 'empty':
                        if button_value == 'm':
                            self.loss(obj)
                            obj.setStyleSheet("background-color: #FF4500;")
                        else:
                            obj.setText(str(button_value))
                            obj.setEnabled(False)
                            self.cell_states[n][m] = 'revealed'
                elif event.button() == QtCore.Qt.RightButton:

                    if self.cell_states[n][m] == 'empty':
                        obj.setIcon(self.flag_icon)
                        self.cell_states[n][m] = 'flag'
                    elif self.cell_states[n][m] == 'flag':
                        obj.setIcon(QIcon())
                        self.cell_states[n][m] = 'empty'

        return QtCore.QObject.event(obj, event)

    def update_timer(self):
        self.time_elapsed += 1
        self.time_label.setText(f"Time: {self.time_elapsed}")

    def GetElementValue(self, obj):
        clicked_button_name = obj.objectName()
        clicked_button = int(clicked_button_name[4:])
        m = clicked_button % self.cols
        n = clicked_button // self.cols
        button_value = self.mines_field[n][m]
        return button_value

    def create_mines_field(self):
        mines_field = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        k = 0
        while k < self.mines:
            first_mine = randrange(self.rows * self.cols)
            first_mine_column = first_mine % self.cols  # столбец
            first_mine_row = first_mine // self.cols  # строка
            if mines_field[first_mine_row][first_mine_column] != 'm':
                mines_field[first_mine_row][first_mine_column] = 'm'
                k += 1

        for row in range(len(mines_field)):
            for column in range(len(mines_field[row])):
                if mines_field[row][column] == 0:
                    neighbour_list = []
                    if column != 0:
                        neighbour_list.append(mines_field[row][column - 1])
                    if column != 7:
                        neighbour_list.append(mines_field[row][column + 1])
                    if row != 0 and column != 0:
                        neighbour_list.append(mines_field[row - 1][column - 1])
                    if row != 0 and column != 7:
                        neighbour_list.append(mines_field[row - 1][column + 1])
                    if row != 0:
                        neighbour_list.append(mines_field[row - 1][column])
                    if row != 7 and column != 0:
                        neighbour_list.append(mines_field[row + 1][column - 1])
                    if row != 7 and column != 7:
                        neighbour_list.append(mines_field[row + 1][column + 1])
                    if row != 7:
                        neighbour_list.append(mines_field[row + 1][column])
                    mines_count_nai = neighbour_list.count('m')
                    mines_field[row][column] = mines_count_nai
        self.mines_field = mines_field
        return mines_field

    def loss(self, obj):
        self.timer.stop()
        self.game_status = False
        for row in range(len(self.mines_field)):
            for col in range(len(self.mines_field[row])):
                button = self.buttons[row][col]
                button.setStyleSheet("background-color: #66CDAA;color:#A0522D;")
                if self.mines_field[row][col] == 'm':
                    button.setIcon(self.explosion_icon)
                    button.setStyleSheet("background-color: #FF4500;")
                else:
                    button.setText(str(self.mines_field[row][col]))
                button.setEnabled(False)

    def re_start(self):
        self.create_mines_field()
        for row in range(len(self.mines_field)):
            for col in range(len(self.mines_field[row])):
                button = self.buttons[row][col]
                button.setEnabled(True)
                button.setText('')
                button.setStyleSheet("background-color: #2F4F4F;")
                button.setIcon(QIcon())
        self.game_status = True
        self.cell_states = [['empty' for _ in range(self.cols)] for _ in range(self.rows)]
        self.timer.stop()
        self.time_elapsed = 0
        self.time_label.setText("Time: 0")
        self.first_click = True
def application():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    application()