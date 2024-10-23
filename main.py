import sys
import yt_dlp
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QProgressBar, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class DownloadThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, url):
        QThread.__init__(self)
        self.url = url

    def run(self):
        ydl_opts = {
            'outtmpl': '%(title)s.%(ext)s',
            'progress_hooks': [self.hook],
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            self.finished.emit(True, "Download complete!")
        except Exception as e:
            error_message = f"Error: {str(e)}\nError type: {type(e).__name__}"
            if hasattr(e, 'args'):
                error_message += f"\nError args: {e.args}"
            self.finished.emit(False, error_message)

    def hook(self, d):
        if d['status'] == 'downloading':
            self.progress.emit(f"Downloading: {d['_percent_str']}")
        if d['status'] == 'finished':
            self.progress.emit("Download complete. Converting...")

class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('YouTube Video Downloader')
        self.setGeometry(300, 300, 400, 150)

        layout = QVBoxLayout()

        url_layout = QHBoxLayout()
        url_label = QLabel('Enter YouTube URL:')
        self.url_input = QLineEdit()
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)

        self.download_btn = QPushButton('Download')
        self.download_btn.clicked.connect(self.start_download)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)

        self.status_label = QLabel('Ready')

        layout.addLayout(url_layout)
        layout.addWidget(self.download_btn)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def start_download(self):
        url = self.url_input.text()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a YouTube URL.")
            return

        self.download_thread = DownloadThread(url)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.start()

        self.download_btn.setEnabled(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_label.setText("Starting download...")

    def update_progress(self, status):
        self.status_label.setText(status)

    def download_finished(self, success, message):
        self.download_btn.setEnabled(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100 if success else 0)
        
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)
        
        self.status_label.setText("Ready")

def main():
    app = QApplication(sys.argv)
    ex = YouTubeDownloader()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
