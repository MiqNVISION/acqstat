import sys                  # Needed for argv
from pathlib import Path    # Cross platform paths
import pandas as pd
import numpy as np
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
            metadata_lines = []
            with open(file_path, "r") as f:
                for line in f:
                    if not line.startswith("#"):
                        break
                
                    metadata_lines.append(line)
#            print(metadata_lines)
            
            ver = None
            srate = None
            timestamp = None
            colnames = None


            for line in metadata_lines: 

                if "version" in line.lower():
                    ver = line.split(" ")[-1].strip()

                elif "rate" in line.lower():
                    srate = np.float64(line.split(" ")[-2])

                elif "time" in line.lower():
                    timestamp = line.split(":")[-1].strip()

                elif "format" in line.lower():
                    colnames = line.split(":")[-1].strip()
            
            skiprow_n = (len(metadata_lines))

            
            # Recording data
            df = pd.read_csv(file_path, skiprows=skiprow_n)
            duration = len(df) / srate if srate else 0
            filename = Path(file_path).name
            self.label.setText(f"{filename}\n")

            summary = (
                f"Version: {ver}\n"
                f"Sample rate: {srate} Hz\n"
                f"Rows: {len(df)}\n"
                f"Columns: {len(df.columns)}\n"
                f"Duration: {duration:.2f} sec\n\n"
            )
            
            for col in df.columns:
                summary += (
                f"{col}\n"  
                f" Min: {df[col].min()}\n"
                f" Max: {df[col].max()}\n\n"
            )
            self.stats.setPlainText(summary)
app = QApplication(sys.argv)

# Instantiate
window = MainWindow()

window.show()

app.exec()