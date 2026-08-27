import sys                  # Needed for argv
from pathlib import Path    # Cross platform paths
import pandas as pd
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, 
    QLabel, 
    QWidget, 
    QVBoxLayout, 
    QPlainTextEdit,
    QGroupBox,
    QHBoxLayout
)


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
        self.channels_layout = QHBoxLayout()

        self.label = QLabel("Drop CSV here")
        self.stats = QPlainTextEdit()
        self.stats.setReadOnly(True)
        #self.stats.setMaximumHeight(120)
        
        self.channels_widget = QWidget()
        self.channels_layout = QHBoxLayout()
        self.channels_widget.setLayout(self.channels_layout)
        
        layout.addWidget(self.label)
        layout.addWidget(self.stats)
        layout.addWidget(self.channels_widget)

        self.setLayout(layout)
        
    def create_channel_card(self, col, min_val, max_val):

        card = QGroupBox(col)

        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"Min: {min_val:.3f}"))
        layout.addWidget(QLabel(f"Max: {max_val:.3f}"))

        card.setLayout(layout)

        return card
    
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

            # Get metadata first to store header, srate, versiona and timestamp
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
            
            # Load recording CSV data (deending on header)
            if colnames == None or colnames == "":
                df = pd.read_csv(file_path, skiprows=skiprow_n)
            else:
                colnames = colnames.split(",")
                df = pd.read_csv(file_path, skiprows=skiprow_n, names=colnames)

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
            
            # Remove cards from previous file
            while self.channels_layout.count():
                item = self.channels_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # Create card per column of interest            
            for col in df.columns:
                card = self.create_channel_card(col, df[col].min(), df[col].max())
                self.channels_layout.addWidget(card)
            self.stats.setPlainText(summary)
app = QApplication(sys.argv)

# Instantiate
window = MainWindow()

window.show()

app.exec()