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
    QHBoxLayout,
    QPushButton
)
from PyQt6.QtGui import QIcon, QFont

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# MainWindow class 
class MainWindow(QWidget):
    
    # Initialise class and QWidget
    def __init__(self):
        super().__init__()

        self.apply_style()
                
        self.setWindowIcon(QIcon("NV.ico"))
        
        self.colors = {
            "bre":   "darkcyan",   # CW breathing
            "pul":   "salmon",     # CW pulse
            "sound": "maroon",     # CW heart sound
            "ECG":   "deeppink",   # CW ECG
            "I":     "orange",     # I signal
            "Q":     "blue",       # Q signal
            "dist":  "grey",       # CW distance
	        "pzt":   "darkblue"    # ref PZT breathing
        }

        self.setWindowTitle("acqstat")
        self.resize(1000, 700)
        
        # Drag and drop enabled
        self.setAcceptDrops(True)

        self.label = QLabel("Drop CSV here")
        self.stats = QPlainTextEdit()
        self.stats.setReadOnly(True)
        self.stats.setMinimumHeight(110)
        
        self.channels_widget = QWidget()
        self.channels_layout = QHBoxLayout()
        self.channels_widget.setLayout(self.channels_layout)
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()        
        layout.addWidget(self.label)
        layout.addWidget(self.stats)
        layout.addWidget(self.channels_widget)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def apply_style(self):

        self.setFont(QFont("Segoe UI", 10))

        self.setStyleSheet("""
            QWidget {
                background-color: #eef7ef;
            }
            QGroupBox {
                background-color: white;
                border: 1px solid #c0c0c0;
                border-radius: 6px;
                margin-top: 10px;
                font-weight: bold;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 3px;
            }

            QPushButton {
                background-color: #b8e0b8;
                border: 1px solid #8ab58a;
                border-radius: 4px;
                padding: 4px;
            }
        """)

    def channel_color(self, col):
        for key, color in self.colors.items():
            if key in col:
                return color
        return "black"

    def create_channel_card(self, col, min_val, max_val, mean_val, std_val):

        card = QGroupBox(col)

        layout = QVBoxLayout()
        
        button = QPushButton("Plot " + col)
        button_1min = QPushButton("1min Plot " + col)

        layout.addWidget(button)
        layout.addWidget(button_1min)
        layout.addWidget(QLabel(f"Min: {min_val:.3f}"))
        layout.addWidget(QLabel(f"Max: {max_val:.3f}"))
        layout.addWidget(QLabel(f"Mean: {mean_val:.3f}"))
        layout.addWidget(QLabel(f"Std: {std_val:.3f}"))

        button.clicked.connect(
            lambda checked=False, c=col: self.plot_chart(col)
        )
        
        button_1min.clicked.connect(
            lambda checked=False, c=col: self.plot_chart_1min(col)
        )

        card.setLayout(layout)

        return card
    
    def set_time_vect(self):
        self.time = np.linspace(0, len(self.df)/self.srate, len(self.df))
    
    def plot_chart(self, col):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(self.time, self.df[col], color=self.channel_color(col))
        ax.set_title(col)
        ax.grid()
        ax.set_xlabel("time (s)")
        self.figure.tight_layout()
        self.canvas.draw()

    def plot_chart_1min(self, col):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(self.time[:int(self.srate*60)], self.df[col].iloc[:int(self.srate*60)], color=self.channel_color(col))
        ax.set_title(col)
        ax.grid()
        ax.set_xlabel("time (s)")
        self.canvas.draw()
    
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
                        
            # Display filename and summary
            filename = Path(file_path).name
            self.label.setText(f"{filename}\n")
            duration = len(df) / srate if srate else 0
            
            summary = (
                f"Version: {ver}\n"
                f"Sample rate: {srate} Hz\n"
                f"Rows: {len(df)}\n"
                f"Columns: {len(df.columns)}\n"
                f"Duration: {duration:.2f} sec\n\n"
            )
            
            
            # Store in class
            self.df = df
            self.srate = srate
            
            # Compute time
            self.set_time_vect()
            
            # Clear plot
            self.figure.clear() 
            self.canvas.draw()
                        
            # Remove cards from previous file
            while self.channels_layout.count():
                item = self.channels_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # Create card per column of interest            
            for col in df.columns:
                card = self.create_channel_card(col, np.min(df[col]), np.max(df[col]), np.mean(df[col]), np.std(df[col]))
                
                # Leave unwanted channels out
                if ("ANA" not in col) and ("AC" not in col):
                    self.channels_layout.addWidget(card)
            self.stats.setPlainText(summary)
app = QApplication(sys.argv)
app.setWindowIcon(QIcon("NV.ico"))

# Instantiate
window = MainWindow()
window.show()

app.exec()