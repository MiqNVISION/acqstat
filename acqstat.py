import sys                  # Needed for argv
from pathlib import Path    # Cross platform paths
import pandas as pd
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPlainTextEdit


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
        self.stats = QPlainTextEdit()
        self.stats.setReadOnly(True)
        layout.addWidget(self.label)
        layout.addWidget(self.stats)

        self.setLayout(layout)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            if file_path.lower().endswith(".csv"):
                event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            # Metadata
            with open(file_path, "r") as f:
                metadata = [f.readline().strip() for _ in range(4)]
            print(metadata)
            
            # Recording data
            df = pd.read_csv(file_path, skiprows=4)
            print(df.head(5))
            filename = Path(file_path).name
            self.label.setText(f"{filename}\n")
            self.stats.setPlainText(
            f"Rows: {len(df)}\n"
            f"Columns: {len(df.columns)}"
            )
app = QApplication(sys.argv)

# Instantiate
window = MainWindow()

window.show()

app.exec()