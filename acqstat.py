import sys # Needed for argv
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout


app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("acqstat")
window.resize(1000, 700)

layout = QVBoxLayout()

label = QLabel("Drop CSV here")
layout.addWidget(label)

window.setLayout(layout)

window.show()

app.exec()