import sys # Needed for argv
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout


# MainWindow class 
class MainWindow(QWidget):
    
    # Initialise class and QWidget
    def __init__(self):
        super().__init__()

        self.setWindowTitle("acqstat")
        self.resize(1000, 700)

        layout = QVBoxLayout()

        label = QLabel("Drop CSV here")
        layout.addWidget(label)

        self.setLayout(layout)


app = QApplication(sys.argv)

# Instantiate
window = MainWindow()

window.show()

app.exec()