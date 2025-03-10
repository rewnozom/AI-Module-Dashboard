# ./dashboard.py

import os
import sys
import glob
import json

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPalette, QColor, QLinearGradient, QFont, QAction, QKeySequence
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QApplication

from utils.theme_utils import apply_dark_theme
from ui.search_tab import SearchTabWrapper
from ui.code_module_tab import CodeModuleTabWrapper

class TitleBar(QWidget):
    """
    Anpassad titelrad för det ramlösa fönstret.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(40)
        self.setStyleSheet("""
            QWidget {
                background-color: #1C1C1C;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
            }
            QPushButton {
                border: none;
                background-color: transparent;
                color: #FFFFFF;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        self.initUI()
    
    def initUI(self):
        from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        self.title_label = QLabel("Utvecklar-Dashboard")
        self.title_label.setFont(QFont("Arial", 12))
        layout.addWidget(self.title_label)
        layout.addStretch()
        self.minimize_btn = QPushButton("—")
        self.minimize_btn.setFixedSize(30, 30)
        self.minimize_btn.clicked.connect(self.parent.showMinimized)
        layout.addWidget(self.minimize_btn)
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setFixedSize(30, 30)
        self.maximize_btn.clicked.connect(self.maximize_restore)
        layout.addWidget(self.maximize_btn)
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.clicked.connect(self.parent.close)
        layout.addWidget(self.close_btn)
    
    def maximize_restore(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.maximize_btn.setText("□")
        else:
            self.parent.showMaximized()
            self.maximize_btn.setText("❐")
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.parent.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.parent.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

class Dashboard(QMainWindow):
    """
    Huvuddashboardfönster med flera flikar.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Utvecklar-Dashboard")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 1400, 900)
        
        # Konfigurera huvudwidget med anpassad titelrad
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(main_widget)
        
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)
        
        # Lägg till flikar för Sök, Kodmoduler och AI Vault
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabBar::tab:selected { background: #2E2E2E; }
            QTabBar::tab { background: #1C1C1C; color: #FFFFFF; padding: 10px; }
            QTabWidget::pane { border: 1px solid #555555; }
        """)
        
        # Befintlig sökflik
        self.search_tab = SearchTabWrapper()
        tabs.addTab(self.search_tab, "Sökfält Dashboard")
        
        # Ny kodmodulflik
        self.code_module_tab = CodeModuleTabWrapper()
        tabs.addTab(self.code_module_tab, "Kodmodul Manager")
        
        main_layout.addWidget(tabs)
        
        # Applicera mörkt tema
        apply_dark_theme(main_widget)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Konfigurera mörkläge för hela applikationen
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(20, 20, 20))
    palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
    palette.setColor(QPalette.Base, QColor(30, 30, 30))
    palette.setColor(QPalette.AlternateBase, QColor(35, 35, 35))
    palette.setColor(QPalette.ToolTipBase, QColor(30, 30, 30))
    palette.setColor(QPalette.ToolTipText, QColor(230, 230, 230))
    palette.setColor(QPalette.Text, QColor(230, 230, 230))
    palette.setColor(QPalette.Button, QColor(45, 45, 45))
    palette.setColor(QPalette.ButtonText, QColor(230, 230, 230))
    palette.setColor(QPalette.Highlight, QColor(70, 70, 70))
    palette.setColor(QPalette.HighlightedText, QColor(230, 230, 230))
    app.setPalette(palette)
    
    # Starta dashboarden
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec())