import sys # Needed for argv
import pandas as pd
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout


# MainWindow class 
class MainWindow(QWidget):
    
    # Initialise class and QWidget
    def __init__(self):
        super().__init__()

        self.setWindowTitle("acqstat")
        self.resize(1000, 700)
        
        # Drag and drop enabled
        self.setAcceptDrops(True)

        layout = QVBoxLayout()

        self.label = QLabel("Drop CSV here")
        layout.addWidget(self.label)

        self.setLayout(layout)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            if file_path.lower().endswith(".csv"):
                event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            df = pd.read_csv(file_path, skiprows=4)
            print(df.head(5))
            filename = file_path.split("/")[-1]
            self.label.setText(
            f"{filename}\n"
            f"Rows: {len(df)}\n"
            f"Columns: {len(df.columns)}"
            )
app = QApplication(sys.argv)

# Instantiate
window = MainWindow()

window.show()

app.exec()