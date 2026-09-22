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
from io import StringIO

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
	        "pzt":   "darkblue",    # ref PZT breathing
            "HR":    "indianred"   # computed hear rate
        }

        self.setWindowTitle("acqstat")
        self.resize(1000, 700)
        
        # Drag and drop enabled
        self.setAcceptDrops(True)

        self.label = QLabel("Drop CSV here")
        self.stats = QLabel()
        self.stats.setFixedHeight(120)
        
        # Report button
        self.report_button = QPushButton("Report")
        self.report_button.clicked.connect(self.generate_report)
        self.report_button.setEnabled(False)


        self.channels_widget = QWidget()
        self.channels_layout = QHBoxLayout()
        self.channels_widget.setLayout(self.channels_layout)
        
        self.figure = Figure(facecolor="#eef7ef")
        # size does not apply when in widget canvas
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setFixedWidth(600)
        self.canvas.setMinimumHeight(200)

        layout = QVBoxLayout()        
        layout.addWidget(self.label)
        layout.addWidget(self.stats)
        layout.addWidget(self.report_button)
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

            QGroupBox#hwprocessed {
                background-color: #d6d4d4;
                border: 1px solid #c77522;
            }

            QGroupBox#processed {
                background-color: #fff4e8;
                border: 1px solid #c77522;
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

            QPushButton:pressed {
                background-color: #8fc98f;
                border: 1px solid #72b572;
            }
        """)
        


    def channel_color(self, col):
        for key, color in self.colors.items():
            if key in col:
                return color
        return "black"

    def create_channel_card(self, col, min_val, max_val, mean_val, std_val):

        card = QGroupBox(col)

        if "distance" in col.lower() or "filter" in col.lower():
            card.setObjectName("hwprocessed")

        if col in ["ECG", "HR", "Annotation"]:
            card.setObjectName("processed")

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
            lambda checked=False, c=col: self.plot_chart_wrapper(c)
        )
        
        button_1min.clicked.connect(
            lambda checked=False, c=col: self.plot_chart_wrapper(c, "1min")
        )

        card.setLayout(layout)

        return card
    
    def set_time_vect(self):
        self.time = np.linspace(0, len(self.df)/self.srate, len(self.df))
    
    def generate_svg_IQ(self, left_col, right_col, max_sample=None):
        return self.generate_svg(
            left_col=left_col,
            right_col=right_col,
            signal_type="I_Q",
            max_sample=max_sample,
            figsize=(3, 2),
            layout="twinx",
            title="I/Q recording",
        )

    def generate_svg(
        self,
        left_col,
        right_col,
        signal_type="I_Q",
        max_sample=None,
        figsize=(7.2, 3),
        layout="stacked",   # "stacked" or "twinx"
        title=None
        ):
        
        if max_sample is None or max_sample > len(self.df):
            max_sample = (
                len(self.df)
                if layout == "twinx"
                else min(len(self.df), int(self.srate * 60))
            )

        if signal_type == "breath_pulse":
            left_label = "breathing" + r"$_{dist}$" + " (a.u.)"
            right_label = "pulse" + r"$_{dist}$" + " (a.u.)"
        elif signal_type == "I_Q":
            left_label = "I (V)"
            right_label = "Q (V)"
       
        fig = Figure(figsize=figsize)

        if layout == "twinx":
            ax1 = fig.add_subplot(111)
            ax2 = ax1.twinx()

            ax1.plot(
                self.time[:max_sample],
                self.df[left_col].iloc[:max_sample],
                color=self.channel_color(left_col),
            )

            ax2.plot(
                self.time[:max_sample],
                self.df[right_col].iloc[:max_sample],
                color=self.channel_color(right_col),
            )

            ax1.set_xlabel("time (s)")
            ax1.set_ylabel(
                left_label,
                color=self.channel_color(left_col),
            )
            ax2.set_ylabel(
                right_label,
                color=self.channel_color(right_col),
            )

            ax1.grid()
            ax1.set_title(title or "I/Q recording")

        else:  # stacked
            ax1 = fig.add_subplot(211)
            ax2 = fig.add_subplot(212)

            ax1.plot(
                self.time[:max_sample],
                self.df[left_col].iloc[:max_sample],
                color=self.channel_color(left_col),
            )

            ax2.plot(
                self.time[:max_sample],
                self.df[right_col].iloc[:max_sample],
                color=self.channel_color(right_col),
            )

            ax1.set_xlabel("time (s)")

            ax1.set_ylabel(
                left_label,
                color=self.channel_color(left_col),
                rotation=0,
                ha="left",
            )

            ax2.set_ylabel(
                right_label,
                color=self.channel_color(right_col),
                rotation=0,
                ha="left",
            )

            ax1.yaxis.set_label_coords(-0.08, 1.02)
            ax2.yaxis.set_label_coords(-0.08, 1.02)

            ax1.grid()
            ax2.grid()
            ax1.set_title(title or self.file_id)

        fig.tight_layout()

        svg_buffer = StringIO()
        fig.savefig(svg_buffer, format="svg")

        svg_text = svg_buffer.getvalue()
        return svg_text[svg_text.find("<svg"):]
        
    def resolve_column(self, *candidates):

        for col in candidates:
            if col in self.df.columns:
                return col

        return None

    def generate_report(self):

        # Assign values for plotting
        I_col = self.resolve_column("I", "I_raw")
        Q_col = self.resolve_column("Q", "Q_raw")
        breath_col = self.resolve_column("Distance_breath", "d_breath")
        pulse_col  = self.resolve_column("Distance_pulse", "d_pulse")

        key_svg = self.generate_svg_IQ(
            I_col,
            Q_col, 
            signal_type = "I_Q" 
        )
        
        if breath_col and pulse_col:
            left_col, right_col = breath_col, pulse_col
            signal_type = "breath_pulse" 
        else:
            left_col, right_col = I_col, Q_col
            signal_type = "I_Q"

        overview_svg = self.generate_svg(
            left_col,
            right_col, 
            signal_type
        )
        


        # Read template
        with open("report/report_template.html", "r", encoding="utf-8") as f:
            html = f.read()

        replacements = {
            "{{FILE_ID}}": self.file_id,
            "{{DATE}}": self.timestamp,
            "{{DURATION}}": f"{self.duration:.1f} sec",
            "{{SRATE}}": str(self.srate),

            "{{QUALITY}}": "N/A",
            "{{SNR}}": "N/A",

            "{{KEY_FINDINGS}}": """
            <ul>
                <li>Report generation prototype.</li>
                <li>No quality assessment implemented yet.</li>
            </ul>
            """,

            "{{KEY_PLOT}}": key_svg,


#            "{{OVERVIEW_PLOT}}": "overview.png",
            "{{OVERVIEW_PLOT}}": overview_svg,
            "{{SPECTRUM_PLOT}}": "spectrum.png",

            "{{MEAN}}": "N/A",
            "{{RMS}}": "N/A",
            "{{MISSING}}": "N/A",
            "{{CLIPPING}}": "N/A",
            "{{EVENTS}}": "N/A",

            "{{CONCLUSION}}": "Report generation pipeline operational.",

            "{{COMPANY}}": "INTERA"
        }

        for key, value in replacements.items():
            html = html.replace(key, str(value))

        outname = self.file_id + "_report.html"

        with open(outname, "w", encoding="utf-8") as f:
            f.write(html)

    def plot_chart_wrapper(self, col, limit=None):
        if limit == "1min":
            max_sample = int(self.srate*60)
        
        elif limit == None:
            max_sample = len(self.df)
        self.plot_chart(max_sample, col)
        
    def plot_chart(self, max_sample, col):
        self.figure.clear()
        self.figure.set_facecolor("#eef7ef")
        ax = self.figure.add_subplot(111)
        ax.plot(self.time[:max_sample], self.df[col].iloc[:max_sample], color=self.channel_color(col))
        ax.set_title(col)
        ax.grid()
        ax.set_xlabel("time (s)")
        self.figure.tight_layout()
        self.canvas.draw()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            if file_path.lower().endswith(".csv"):
                event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            
            self.report_button.setEnabled(False)

            
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
            self.version = ver
            self.timestamp = timestamp
            self.duration = duration
            self.filename = filename
            self.file_id = Path(filename).stem

            
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
            self.stats.setText(summary)
            
            # Enable report button
            self.report_button.setEnabled(True)
app = QApplication(sys.argv)
app.setWindowIcon(QIcon("NV.ico"))

# Instantiate
window = MainWindow()
window.show()

app.exec()