import sys
import speech_recognition as sr
from deep_translator import GoogleTranslator
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import QThread, Signal, Qt, QTimer
from PySide6.QtGui import QFont, QColor, QPalette

# Thread to handle speech recognition
class SpeechThread(QThread):
    update_text = Signal(str, str)  # original text, translation
    mic_status = Signal(bool)       # True = active, False = inactive

    def run(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            while True:
                try:
                    audio = r.listen(source, timeout=3)
                    text = r.recognize_google(audio)
                    translation = GoogleTranslator(source='auto', target='de').translate(text)
                    self.update_text.emit(text, translation)
                    self.mic_status.emit(True)
                except sr.WaitTimeoutError:
                    # No speech detected
                    self.mic_status.emit(False)
                except sr.UnknownValueError:
                    self.update_text.emit("❌ Couldn't understand", "")
                    self.mic_status.emit(True)
                except sr.RequestError:
                    self.update_text.emit("⚠️ Service unavailable", "")
                    self.mic_status.emit(False)

# Main GUI
class TranslatorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎤 Speech to German Translator")
        self.setGeometry(100, 100, 700, 450)

        # Dark theme palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#1e1e1e"))
        palette.setColor(QPalette.WindowText, QColor("#ffffff"))
        palette.setColor(QPalette.Button, QColor("#3a3a3a"))
        palette.setColor(QPalette.ButtonText, QColor("#ffffff"))
        self.setPalette(palette)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)

        # Original text label
        self.label_original = QLabel("Original text will appear here")
        self.label_original.setFont(QFont("Segoe UI", 18))
        self.label_original.setStyleSheet(
            "color: #aad8ff; background-color: #2e2e2e; padding: 15px; border-radius: 12px;"
        )
        self.label_original.setAlignment(Qt.AlignCenter)

        # German translation label
        self.label_translation = QLabel("German translation will appear here")
        self.label_translation.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self.label_translation.setStyleSheet(
            "color: #ffcc66; background-color: #2e2e2e; padding: 20px; border-radius: 12px;"
        )
        self.label_translation.setAlignment(Qt.AlignCenter)

        # Listening indicator
        self.indicator = QLabel()
        self.indicator.setFixedSize(25, 25)
        self.indicator_opacity = 1.0
        self.fade_out = True
        self.active_color = "#55ff55"  # green
        self.inactive_color = "#ff5555"  # red
        self.current_color = self.active_color
        self.indicator.setStyleSheet(f"background-color: {self.current_color}; border-radius: 12px;")

        # Layout for indicator
        indicator_layout = QHBoxLayout()
        indicator_layout.setAlignment(Qt.AlignCenter)
        indicator_layout.addWidget(QLabel("Mic status:"))
        indicator_layout.addWidget(self.indicator)
        layout.addLayout(indicator_layout)

        # Quit button
        self.quit_btn = QPushButton("Quit")
        self.quit_btn.setFont(QFont("Segoe UI", 16))
        self.quit_btn.setStyleSheet(
            "background-color: #ff5555; color: white; padding: 10px 20px; border-radius: 10px;"
        )
        self.quit_btn.clicked.connect(self.close)
        layout.addWidget(self.quit_btn)

        self.setLayout(layout)

        # Start speech recognition thread
        self.thread = SpeechThread()
        self.thread.update_text.connect(self.update_labels)
        self.thread.mic_status.connect(self.update_mic_status)
        self.thread.start()

        # Timer to pulse the indicator
        self.timer = QTimer()
        self.timer.timeout.connect(self.pulse_indicator)
        self.timer.start(100)  # update every 100ms

        self.mic_active = True  # current status

    def update_labels(self, original, translation):
        self.label_original.setText(original)
        self.label_translation.setText(translation)

    def update_mic_status(self, active):
        self.mic_active = active
        self.current_color = self.active_color if active else self.inactive_color

    def pulse_indicator(self):
        # Pulse between bright and dim
        if self.fade_out:
            self.indicator_opacity -= 0.05
            if self.indicator_opacity <= 0.3:
                self.fade_out = False
        else:
            self.indicator_opacity += 0.05
            if self.indicator_opacity >= 1.0:
                self.fade_out = True
        color = self.current_color
        self.indicator.setStyleSheet(f"background-color: rgba({int(int(color[1:3],16))},{int(int(color[3:5],16))},{int(int(color[5:7],16))},{self.indicator_opacity}); border-radius: 12px;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TranslatorGUI()
    window.show()
    sys.exit(app.exec())
