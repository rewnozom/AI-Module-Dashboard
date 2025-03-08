# ./ui/code_module_tab.py
import os
import sys
import glob
import json
import re
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import Qt, Signal, QMimeData, QSize, QPoint, QTimer
from PySide6.QtGui import QFont, QAction, QKeySequence, QDrag, QIcon, QColor
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QListWidget, QListWidgetItem, QMessageBox, QLabel, QFrame, QScrollArea,
    QCheckBox, QInputDialog, QGridLayout, QGroupBox, QComboBox, QFileDialog,
    QSplitter, QTabWidget, QToolBar, QMenu, QStatusBar, QProgressBar
)

from utils.theme_utils import apply_dark_theme
from utils.card_utils import create_card
from utils.code_utils import CodeAnalyzer, CodeModuleManager
from ui.code_module_widget import CodeModuleWidget

class CodeModuleTab(QWidget):
    """
    Fliken för kodmoduler, innehåller en lista med kodmoduler
    samt verktyg för filtrering och organisation.
    """
    def __init__(self, modules_directory="./modules/"):
        super().__init__()
        self.modules_directory = Path(modules_directory)
        self.ensure_directory_exists()
        
        # Sökväg till JSON-fil för att spara moduldata
        self.json_directory = "./modules/json/"
        self.ensure_json_directory_exists()
        
        # Kodmodulhanterare för filhantering
        self.module_manager = CodeModuleManager(str(self.modules_directory))
        
        # Sök efter befintliga JSON-filer
        self.json_files = sorted(glob.glob(os.path.join(self.json_directory, "code_modules*.json")))
        if not self.json_files:
            self.json_files = [os.path.join(self.json_directory, "code_modules.json")]
            self.create_default_json_file()
        
        self.current_file_index = 0
        self.code_modules = []
        self.history = []
        self.history_index = -1
        
        # Statusflaggor
        self.is_loading = False
        self.is_saving = False
        
        # Autoscan-timer för att upptäcka nya moduler på disk
        self.auto_scan_timer = QTimer(self)
        self.auto_scan_timer.setInterval(10000)  # 10 sekunder
        self.auto_scan_timer.timeout.connect(self.auto_scan_for_modules)
        
        # Initiera UI
        self.initUI()
        
        # Ladda moduldata
        self.load_data(self.json_files[self.current_file_index])
        
        # Starta autoscanning
        self.auto_scan_timer.start()
    
    def ensure_directory_exists(self):
        """Säkerställ att huvudkatalogen för moduler finns."""
        os.makedirs(self.modules_directory, exist_ok=True)
        
        # Skapa också underkataloger för olika språk och kategorier
        language_dirs = ['python', 'javascript', 'html', 'css', 'cpp', 'java']
        category_dirs = ['ui', 'utils', 'data', 'network', 'db', 'ai', 'algorithms', 'other']
        
        for lang in language_dirs:
            os.makedirs(os.path.join(self.modules_directory, lang), exist_ok=True)
        
        for category in category_dirs:
            os.makedirs(os.path.join(self.modules_directory, category), exist_ok=True)
    
    def ensure_json_directory_exists(self):
        """Säkerställ att katalogen för JSON-filer finns."""
        os.makedirs(self.json_directory, exist_ok=True)
    
    def create_default_json_file(self):
        """Skapa en standardfil om ingen JSON-fil finns."""
        try:
            with open(self.json_files[0], "w", encoding='utf-8') as f:
                json.dump([], f, indent=4, ensure_ascii=False)
        except Exception as e:
            QMessageBox.critical(self, "Fel vid skapande av JSON-fil", str(e))
    
    def initUI(self):
        """Initiera användargränssnittet."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        apply_dark_theme(self)
        
        # Övre området: Moduler och kontroller
        upper_container = QWidget()
        upper_layout = QHBoxLayout(upper_container)
        upper_layout.setSpacing(10)
        upper_layout.setContentsMargins(0, 0, 0, 0)
        
        # Vänster panel med kontroller
        left_panel = self.create_left_panel()
        upper_layout.addWidget(left_panel)
        
        # Höger panel: Modulvisning
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scrollbart område för moduler
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        
        # Använd rutnät för att visa moduler 2x2
        self.modules_layout = QGridLayout(self.scroll_content)
        self.modules_layout.setSpacing(15)
        self.modules_layout.setContentsMargins(5, 5, 5, 5)
        
        self.scroll_area.setWidget(self.scroll_content)
        right_layout.addWidget(self.scroll_area)
        
        # Global sökruta
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 5, 0, 5)
        
        self.global_search_input = QLineEdit()
        self.global_search_input.setPlaceholderText("Sök i moduler...")
        self.global_search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border-radius: 5px;
            }
        """)
        self.global_search_input.returnPressed.connect(self.search_modules)
        
        search_layout.addWidget(self.global_search_input)
        
        search_btn = QPushButton("🔍 Sök")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: 1px solid #005999;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0098FF;
            }
        """)
        search_btn.clicked.connect(self.search_modules)
        search_layout.addWidget(search_btn)
        
        # Lägg till sökpanelen
        right_layout.addWidget(search_container)
        
        upper_layout.addWidget(right_panel, 3)  # Ge högerpanelen mer utrymme
        
        # Lägg till övre behållaren
        main_layout.addWidget(upper_container)
        
        # Nedre verktygspanel för filtrering
        toolbox_panel = QFrame()
        toolbox_panel.setStyleSheet("""
            QFrame {
                background-color: #1C1C1C;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 10px;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #3C3C3C;
                color: #FFFFFF;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
        toolbox_layout = QHBoxLayout(toolbox_panel)
        toolbox_layout.setSpacing(10)
        
        # Filter-sektion
        filter_section = QHBoxLayout()
        
        # Kategorifiltreringsdropdown
        filter_section.addWidget(QLabel("Kategori:"))
        self.category_filter = QComboBox()
        self.category_filter.addItems(["Alla", "ui", "utils", "data", "network", "db", "ai", "algorithms", "other"])
        self.category_filter.setMinimumWidth(120)
        self.category_filter.currentTextChanged.connect(self.apply_filters)
        filter_section.addWidget(self.category_filter)
        
        # Språkfiltreringsdropdown
        filter_section.addWidget(QLabel("Språk:"))
        self.language_filter = QComboBox()
        self.language_filter.addItems(["Alla", "python", "javascript", "html", "css", "java", "cpp"])
        self.language_filter.setMinimumWidth(120)
        self.language_filter.currentTextChanged.connect(self.apply_filters)
        filter_section.addWidget(self.language_filter)
        
        # Taggfilter
        filter_section.addWidget(QLabel("Tagg:"))
        self.tag_filter = QLineEdit()
        self.tag_filter.setPlaceholderText("Filtrera med tagg...")
        self.tag_filter.returnPressed.connect(self.apply_filters)
        filter_section.addWidget(self.tag_filter)
        
        toolbox_layout.addLayout(filter_section)
        
        # Knappar för filtrering
        filter_btn = QPushButton("Använd Filter")
        filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #6A9955;
                color: white;
                border: 1px solid #4D7E3E;
                padding: 5px 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8FDC75;
            }
        """)
        filter_btn.clicked.connect(self.apply_filters)
        toolbox_layout.addWidget(filter_btn)
        
        clear_filter_btn = QPushButton("Rensa Filter")
        clear_filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #CE9178;
                color: white;
                border: 1px solid #A5735E;
                padding: 5px 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F9B195;
            }
        """)
        clear_filter_btn.clicked.connect(self.clear_filters)
        toolbox_layout.addWidget(clear_filter_btn)
        
        # Statusindikator för moduler
        self.modules_status = QLabel("0 moduler")
        self.modules_status.setStyleSheet("color: #AAAAAA; padding-left: 15px;")
        toolbox_layout.addWidget(self.modules_status)
        
        # Lägg till filterpanelen
        main_layout.addWidget(toolbox_panel)
        
        # Statusfält längst ner
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #1C1C1C;
                color: #AAAAAA;
                border-top: 1px solid #333333;
            }
        """)
        self.status_bar.showMessage("Redo")
        
        # Lägg till progessbar i statusfältet
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(15)
        self.progress_bar.setMaximumWidth(150)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        main_layout.addWidget(self.status_bar)
    
    def create_left_panel(self):
        """Skapa vänster kontrollpanel."""
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background-color: #1C1C1C;
                border: 2px solid #333333;
                border-radius: 10px;
            }
            QPushButton {
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
                color: white;
                margin: 3px;
            }
        """)
        left_panel.setFixedWidth(250)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(8)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        # Grupperingsboxar för organisering
        module_group = QGroupBox("Modulhantering")
        module_group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 5px;
                color: #CCCCCC;
            }
        """)
        module_layout = QVBoxLayout(module_group)
        
        # Huvudknappar
        add_module_btn = QPushButton("➕ Lägg till Ny Modul")
        add_module_btn.setStyleSheet("background-color: #6A9955; border: 1px solid #4D7E3E;")
        add_module_btn.setToolTip("Lägg till en ny modul")
        add_module_btn.clicked.connect(self.add_code_module)
        module_layout.addWidget(add_module_btn)
        
        scan_btn = QPushButton("🔄 Scanna efter moduler")
        scan_btn.setStyleSheet("background-color: #569CD6; border: 1px solid #3D7FB8;")
        scan_btn.setToolTip("Scanna filsystemet efter moduler")
        scan_btn.clicked.connect(self.scan_for_modules)
        module_layout.addWidget(scan_btn)
        
        left_layout.addWidget(module_group)
        
        # Gruppbox för JSON-hantering
        json_group = QGroupBox("JSON-hantering")
        json_group.setStyleSheet(module_group.styleSheet())
        json_layout = QVBoxLayout(json_group)
        
        # JSON-knappar
        load_btn = QPushButton("📂 Ladda JSON")
        load_btn.setStyleSheet("background-color: #569CD6; border: 1px solid #3D7FB8;")
        load_btn.setToolTip("Ladda från JSON")
        load_btn.clicked.connect(lambda: self.load_data(self.json_files[self.current_file_index]))
        json_layout.addWidget(load_btn)
        
        save_btn = QPushButton("💾 Spara JSON")
        save_btn.setStyleSheet("background-color: #569CD6; border: 1px solid #3D7FB8;")
        save_btn.setToolTip("Spara till JSON")
        save_btn.clicked.connect(lambda: self.save_data())
        json_layout.addWidget(save_btn)
        
        # Sidhantering
        page_layout = QHBoxLayout()
        
        add_page_btn = QPushButton("➕")
        add_page_btn.setFixedWidth(40)
        add_page_btn.setStyleSheet("background-color: #569CD6; border: 1px solid #3D7FB8;")
        add_page_btn.setToolTip("Lägg till en ny sida")
        add_page_btn.clicked.connect(self.add_page)
        page_layout.addWidget(add_page_btn)
        
        self.page_indicator = QLabel("Sida 1/1")
        self.page_indicator.setStyleSheet("color: white; font-size: 13px; background: transparent;")
        self.page_indicator.setAlignment(Qt.AlignCenter)
        page_layout.addWidget(self.page_indicator)
        
        remove_page_btn = QPushButton("🗑️")
        remove_page_btn.setFixedWidth(40)
        remove_page_btn.setStyleSheet("background-color: #C74545; border: 1px solid #A53535;")
        remove_page_btn.setToolTip("Ta bort nuvarande sida")
        remove_page_btn.clicked.connect(self.remove_current_page)
        page_layout.addWidget(remove_page_btn)
        
        json_layout.addLayout(page_layout)
        
        left_layout.addWidget(json_group)
        
        # Gruppbox för historik
        history_group = QGroupBox("Historik")
        history_group.setStyleSheet(module_group.styleSheet())
        history_layout = QVBoxLayout(history_group)
        
        # Ångra/gör om
        history_buttons = QHBoxLayout()
        
        undo_btn = QPushButton("↩️ Ångra")
        undo_btn.setFixedWidth(115)
        undo_btn.setStyleSheet("background-color: #9277A3; border: 1px solid #765286;")
        undo_btn.setToolTip("Ångra (Ctrl+Z)")
        undo_btn.clicked.connect(self.undo)
        history_buttons.addWidget(undo_btn)
        
        redo_btn = QPushButton("↪️ Gör om")
        redo_btn.setFixedWidth(115)
        redo_btn.setStyleSheet("background-color: #9277A3; border: 1px solid #765286;")
        redo_btn.setToolTip("Gör om (Ctrl+Y)")
        redo_btn.clicked.connect(self.redo)
        history_buttons.addWidget(redo_btn)
        
        history_layout.addLayout(history_buttons)
        
        left_layout.addWidget(history_group)
        
        # Gruppbox för import/export
        io_group = QGroupBox("Import/Export")
        io_group.setStyleSheet(module_group.styleSheet())
        io_layout = QVBoxLayout(io_group)
        
        # Import/Export
        import_all_btn = QPushButton("📥 Importera alla moduler")
        import_all_btn.setStyleSheet("background-color: #CE9178; border: 1px solid #A5735E;")
        import_all_btn.setToolTip("Importera moduler från katalog")
        import_all_btn.clicked.connect(self.import_all_modules)
        io_layout.addWidget(import_all_btn)
        
        export_all_btn = QPushButton("📤 Exportera alla moduler")
        export_all_btn.setStyleSheet("background-color: #CE9178; border: 1px solid #A5735E;")
        export_all_btn.setToolTip("Exportera alla moduler till katalog")
        export_all_btn.clicked.connect(self.export_all_modules)
        io_layout.addWidget(export_all_btn)
        
        left_layout.addWidget(io_group)
        
        left_layout.addStretch()
        
        return left_panel
    
    def add_code_module(self):
        """Lägg till en ny kodmodul."""
        module_id = str(len(self.code_modules))
        current_timestamp = datetime.now().isoformat()
        
        # Grundläggande moduldata
        module_data = {
            "id": module_id,
            "name": f"modul_{module_id}",
            "extension": ".py",
            "code": "",
            "tags": [],
            "category": "other",
            "created": current_timestamp,
            "modified": current_timestamp,
            "description": "",
            "file_path": "",
            "auto_save": True
        }
        
        # Skapa och konfigurera widget
        widget = CodeModuleWidget(module_id, module_data, self.modules_directory)
        self.configure_code_module_widget(widget)
        
        # Lägg till i grid-layout
        row, col = divmod(len(self.code_modules), 2)
        self.modules_layout.addWidget(widget, row, col)
        
        # Lägg till i moduldata
        self.code_modules.append(module_data)
        
        self.update_history()
        self.save_data()
        self.update_modules_status()
        
        # Visa statusmeddelande
        self.status_bar.showMessage(f"Ny modul '{module_data['name']}' skapad", 3000)
    
    def configure_code_module_widget(self, widget):
        """Konfigurera signaler och inställningar för en kodmodulwidget."""
        # Koppla widgetsignaler till hanteringsfunktioner
        widget.moduleAdded.connect(self.on_module_added)
        widget.moduleRemoved.connect(self.on_module_removed)
        widget.moduleUpdated.connect(self.on_module_updated)
    
    def on_module_added(self, module_id, module_data):
        """När en ny modul läggs till."""
        # Uppdatera moduldata i listan
        for i, module in enumerate(self.code_modules):
            if module["id"] == module_id:
                self.code_modules[i] = module_data
                break
        
        self.update_history()
        self.save_data()
    
    def on_module_removed(self, module_id):
        """När en modul tas bort."""
        for i, module in enumerate(self.code_modules):
            if module["id"] == module_id:
                # Ta bort modulen från listan
                del self.code_modules[i]
                break
        
        self.refresh_ui()
        self.update_history()
        self.save_data()
        self.update_modules_status()
    
    def on_module_updated(self, module_id, update_type, module_data):
        """När en modul uppdateras."""
        # Uppdatera moduldata i listan
        for i, module in enumerate(self.code_modules):
            if module["id"] == module_id:
                self.code_modules[i] = module_data
                break
        
        # Om vi inte redan håller på att ladda eller spara
        if not self.is_loading and not self.is_saving:
            self.update_history()
            self.save_data()
    
    def update_history(self):
        """Uppdatera historiken för ångra/gör om."""
        # Trimma historiken om vi är någonstans i mitten
        self.history = self.history[:self.history_index + 1]
        
        # Lägg till den nuvarande tillståndet till historiken
        self.history.append(json.loads(json.dumps(self.code_modules)))
        self.history_index += 1
    
    def undo(self):
        """Ångra senaste åtgärd."""
        if self.history_index > 0:
            self.history_index -= 1
            # Djupkopiera historikdata till nuvarande tillstånd
            self.code_modules = json.loads(json.dumps(self.history[self.history_index]))
            self.refresh_ui()
            self.save_data()
            
            self.status_bar.showMessage("Ångra: En åtgärd ångrades", 3000)
        else:
            QMessageBox.information(self, "Info", "Ingenting att ångra.")
    
    def redo(self):
        """Gör om åtgärd."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            # Djupkopiera historikdata till nuvarande tillstånd
            self.code_modules = json.loads(json.dumps(self.history[self.history_index]))
            self.refresh_ui()
            self.save_data()
            
            self.status_bar.showMessage("Gör om: En åtgärd gjordes om", 3000)
        else:
            QMessageBox.information(self, "Info", "Ingenting att göra om.")
    
    def refresh_ui(self):
        """Uppdatera användargränssnittet med aktuella moduler."""
        # Rensa alla moduler från layout
        for i in reversed(range(self.modules_layout.count())):
            widget = self.modules_layout.itemAt(i).widget()
            if widget:
                self.modules_layout.removeWidget(widget)
                widget.deleteLater()
        
        # Återskapa moduler från data
        for idx, module in enumerate(self.code_modules):
            # Skapa ny widget för modulen
            widget = CodeModuleWidget(module["id"], module, self.modules_directory)
            self.configure_code_module_widget(widget)
            
            # Lägg till i grid
            row, col = divmod(idx, 2)
            self.modules_layout.addWidget(widget, row, col)
        
        # Uppdatera statusfältet
        self.update_modules_status()
        
        # Uppdatera sidindikator
        self.update_page_indicator()
    
    def update_modules_status(self):
        """Uppdatera statusmeddelandet för antal moduler."""
        count = len(self.code_modules)
        self.modules_status.setText(f"{count} {'moduler' if count != 1 else 'modul'}")
    
    def update_page_indicator(self):
        """Uppdatera sidindikator."""
        if self.json_files:
            current_page = self.current_file_index + 1
            total_pages = len(self.json_files)
            self.page_indicator.setText(f"Sida {current_page}/{total_pages}")
        else:
            self.page_indicator.setText("Sida 0/0")
    
    def save_data(self):
        """Spara alla moduldata till JSON."""
        if self.is_saving:
            return
        
        self.is_saving = True
        
        try:
            # Visa progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_bar.showMessage("Sparar moduler...")
            
            # Säkerställ att alla widgets har uppdaterat sina moduldata
            for i in range(self.modules_layout.count()):
                widget_item = self.modules_layout.itemAt(i)
                if widget_item and isinstance(widget_item.widget(), CodeModuleWidget):
                    widget = widget_item.widget()
                    
                    # Hitta motsvarande modul i listan
                    for module in self.code_modules:
                        if module["id"] == widget.module_id:
                            # Uppdatera kod och andra fält
                            module["code"] = widget.code_editor.toPlainText()
                            module["name"] = widget.name_label.text()
                            module["extension"] = widget.extension_input.text()
                            module["tags"] = widget.module_data.get("tags", [])
                            module["file_path"] = str(widget.module_data.get("file_path", ""))
                            module["modified"] = datetime.now().isoformat()
            
            file_name = self.json_files[self.current_file_index]
            with open(file_name, "w", encoding='utf-8') as f:
                json.dump(self.code_modules, f, indent=4, ensure_ascii=False)
            
            self.progress_bar.setValue(100)
            self.status_bar.showMessage(f"Sparad till {file_name}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Fel vid sparande", str(e))
        finally:
            self.is_saving = False
            # Dölj progressbar efter en liten fördröjning
            QTimer.singleShot(1000, lambda: self.progress_bar.setVisible(False))
    
    def load_data(self, file_name=None):
        """Ladda moduldata från JSON."""
        if self.is_loading:
            return
        
        if file_name is None:
            file_name = self.json_files[self.current_file_index]
        
        self.is_loading = True
        
        try:
            # Visa progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_bar.showMessage("Laddar moduler...")
            
            with open(file_name, "r", encoding='utf-8') as f:
                self.code_modules = json.load(f)
            
            self.progress_bar.setValue(50)
            
            # Uppdatera UI
            self.refresh_ui()
            
            # Uppdatera historik om det inte finns någon
            if not self.history:
                self.update_history()
            
            self.progress_bar.setValue(100)
            self.status_bar.showMessage(f"Laddad från {file_name}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Fel vid laddning", str(e))
        finally:
            self.is_loading = False
            # Dölj progressbar efter en liten fördröjning
            QTimer.singleShot(1000, lambda: self.progress_bar.setVisible(False))
    
    def apply_filters(self):
        """Filtrera moduler baserat på kategori, språk och taggar."""
        selected_category = self.category_filter.currentText()
        selected_language = self.language_filter.currentText()
        tag_filter = self.tag_filter.text().strip().lower()


        # Hämta original data om vi har filtrerat
        if hasattr(self, 'original_modules'):
            self.code_modules = self.original_modules.copy()
        else:
            # Spara originalet första gången vi filtrerar
            self.original_modules = self.code_modules.copy()
        
        # Filtrera baserat på kategori
        if selected_category != "Alla":
            self.code_modules = [m for m in self.code_modules if m.get("category", "other") == selected_category]
        
        # Filtrera baserat på språk (extrapolerat från filändelse)
        if selected_language != "Alla":
            if selected_language == "python":
                self.code_modules = [m for m in self.code_modules if m.get("extension", "").lower() == ".py"]
            elif selected_language == "javascript":
                self.code_modules = [m for m in self.code_modules if m.get("extension", "").lower() in [".js", ".jsx"]]
            elif selected_language == "html":
                self.code_modules = [m for m in self.code_modules if m.get("extension", "").lower() in [".html", ".htm"]]
            elif selected_language == "css":
                self.code_modules = [m for m in self.code_modules if m.get("extension", "").lower() == ".css"]
            elif selected_language == "java":
                self.code_modules = [m for m in self.code_modules if m.get("extension", "").lower() == ".java"]
            elif selected_language == "cpp":
                self.code_modules = [m for m in self.code_modules if m.get("extension", "").lower() in [".cpp", ".h", ".c", ".hpp"]]
        
        # Filtrera baserat på taggar
        if tag_filter:
            self.code_modules = [
                m for m in self.code_modules 
                if "tags" in m and any(tag_filter in tag.lower() for tag in m["tags"])
            ]
        
        # Uppdatera användargränssnittet
        self.refresh_ui()
        
        # Visa statusmeddelande
        filter_text = []
        
        if selected_category != "Alla":
            filter_text.append(f"kategori: {selected_category}")
        
        if selected_language != "Alla":
            filter_text.append(f"språk: {selected_language}")
        
        if tag_filter:
            filter_text.append(f"tagg: {tag_filter}")
        
        if filter_text:
            filters = ", ".join(filter_text)
            self.status_bar.showMessage(f"Filter applicerat: {filters}", 3000)
    
    def clear_filters(self):
        """Rensa alla filter och visa alla moduler."""
        # Återställ UI-element
        self.category_filter.setCurrentText("Alla")
        self.language_filter.setCurrentText("Alla")
        self.tag_filter.clear()
        
        # Återställ moduldata från originalet om det finns
        if hasattr(self, 'original_modules'):
            self.code_modules = self.original_modules.copy()
            delattr(self, 'original_modules')  # Ta bort originalreferensen
        
        # Uppdatera UI
        self.refresh_ui()
        
        # Visa statusmeddelande
        self.status_bar.showMessage("Filter rensade", 3000)
    
    def add_page(self):
        """Lägg till en ny sida (JSON-fil)."""
        new_index = len(self.json_files)
        new_file = os.path.join(self.json_directory, f"code_modules_{new_index}.json")
        
        try:
            with open(new_file, "w", encoding='utf-8') as f:
                json.dump([], f, indent=4)
            
            self.json_files.append(new_file)
            self.current_file_index = new_index
            self.load_data(new_file)
            
            # Uppdatera sidindikator
            self.update_page_indicator()
            
            self.status_bar.showMessage(f"Ny sida skapad: {new_file}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Fel", f"Kunde inte skapa ny sida: {str(e)}")
    
    def remove_current_page(self):
        """Ta bort aktuell sida (JSON-fil)."""
        if len(self.json_files) <= 1:
            QMessageBox.warning(self, "Varning", "Minst en sida måste finnas.")
            return
        
        current = self.json_files[self.current_file_index]
        reply = QMessageBox.question(
            self, "Ta Bort Sida", 
            f"Ta bort sidan '{current}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                os.remove(current)
                self.json_files.pop(self.current_file_index)
                
                if self.current_file_index >= len(self.json_files):
                    self.current_file_index = len(self.json_files) - 1
                
                self.load_data(self.json_files[self.current_file_index])
                
                # Uppdatera sidindikator
                self.update_page_indicator()
                
                self.status_bar.showMessage(f"Sida borttagen: {current}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Fel", f"Kunde inte ta bort sidan: {str(e)}")
    
    def search_modules(self):
        """Sök i modulkod och namn."""
        term = self.global_search_input.text().strip()
        if not term:
            QMessageBox.warning(self, "Tom Sökning", "Ange en sökterm.")
            return
        
        # Spara originalet om det inte redan är sparat
        if not hasattr(self, 'original_modules'):
            self.original_modules = self.code_modules.copy()
        
        # Sök genom alla moduler
        matching_modules = []
        
        for module in self.original_modules:
            # Sök i olika fält
            if (
                term.lower() in module.get("name", "").lower() or
                term.lower() in module.get("code", "").lower() or
                term.lower() in module.get("description", "").lower() or
                any(term.lower() in tag.lower() for tag in module.get("tags", []))
            ):
                matching_modules.append(module)
        
        if matching_modules:
            # Uppdatera listan med matchande moduler
            self.code_modules = matching_modules
            self.refresh_ui()
            self.status_bar.showMessage(f"Hittade {len(matching_modules)} moduler som matchade '{term}'", 3000)
        else:
            QMessageBox.information(self, "Inga resultat", f"Inga moduler matchade söktermen '{term}'.")
    
    def import_all_modules(self):
        """Importera alla moduler från en katalog."""
        directory = QFileDialog.getExistingDirectory(self, "Välj Katalog med Kodmoduler")
        if not directory:
            return
        
        try:
            # Visa progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_bar.showMessage("Importerar moduler...")
            
            # Scanna genom alla filer i katalogen
            file_count = 0
            imported_count = 0
            
            # Rensa nuvarande moduler om användaren vill det
            reply = QMessageBox.question(
                self, "Rensa befintliga?", 
                "Vill du rensa befintliga moduler före import?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.code_modules = []
            
            next_id = max([int(m["id"]) for m in self.code_modules] + [-1]) + 1
            
            # Rekursiv traversering av mappstruktur
            for root, _, files in os.walk(directory):
                for file in files:
                    file_count += 1
                    file_path = os.path.join(root, file)
                    
                    # Kontrollera filändelse för att hitta kodfiler
                    _, ext = os.path.splitext(file)
                    if ext.lower() in ['.py', '.js', '.html', '.css', '.cpp', '.h', '.java', '.jsx']:
                        try:
                            # Läs filen
                            with open(file_path, 'r', encoding='utf-8') as f:
                                code = f.read()
                            
                            # Bestäm kategori baserat på katalogstruktur
                            rel_path = os.path.relpath(root, directory)
                            category_name = rel_path.split(os.sep)[0] if rel_path != '.' else "other"
                            if category_name not in ["ui", "utils", "data", "network", "db", "ai", "algorithms", "other"]:
                                category_name = "other"
                            
                            # Bestäm namn baserat på filnamn
                            module_name = os.path.splitext(file)[0]
                            
                            # Skapa moduldata
                            module_data = {
                                "id": str(next_id),
                                "name": module_name,
                                "extension": ext,
                                "code": code,
                                "tags": [],
                                "category": category_name,
                                "created": datetime.now().isoformat(),
                                "modified": datetime.now().isoformat(),
                                "description": f"Importerad från {file_path}",
                                "file_path": file_path,
                                "auto_save": True
                            }
                            
                            # Lägg till modulen
                            self.code_modules.append(module_data)
                            imported_count += 1
                            next_id += 1
                            
                            # Uppdatera progress
                            if file_count % 10 == 0:
                                self.progress_bar.setValue(min(90, int(file_count / (file_count + 10) * 100)))
                                QApplication.processEvents()
                            
                        except Exception as e:
                            print(f"Kunde inte importera {file_path}: {e}")
            
            # Uppdatera UI och spara
            self.refresh_ui()
            self.update_history()
            self.save_data()
            
            self.progress_bar.setValue(100)
            self.status_bar.showMessage(
                f"Import klar. Importerade {imported_count} av {file_count} filer.", 5000
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Fel vid import", str(e))
        finally:
            # Dölj progressbar efter en liten fördröjning
            QTimer.singleShot(1000, lambda: self.progress_bar.setVisible(False))
    
    def export_all_modules(self):
        """Exportera alla moduler till en katalog."""
        directory = QFileDialog.getExistingDirectory(self, "Välj Katalog för Export")
        if not directory:
            return
        
        try:
            # Visa progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_bar.showMessage("Exporterar moduler...")
            
            # Uppdatera moduldata från widgets
            for i in range(self.modules_layout.count()):
                widget_item = self.modules_layout.itemAt(i)
                if widget_item and isinstance(widget_item.widget(), CodeModuleWidget):
                    widget = widget_item.widget()
                    for module in self.code_modules:
                        if module["id"] == widget.module_id:
                            module["code"] = widget.code_editor.toPlainText()
                            module["name"] = widget.name_label.text()
                            module["extension"] = widget.extension_input.text()
                            module["tags"] = widget.tags
            
            # Exportera alla moduler
            module_count = len(self.code_modules)
            exported_count = 0
            
            for i, module in enumerate(self.code_modules):
                # Uppdatera progress
                self.progress_bar.setValue(int((i / module_count) * 100))
                QApplication.processEvents()
                
                # Hoppa över tomma moduler
                if not module.get("code", "").strip():
                    continue
                
                # Skapa underkatalog baserat på kategori
                category_dir = os.path.join(directory, module.get("category", "other"))
                os.makedirs(category_dir, exist_ok=True)
                
                # Generera filnamn
                extension = module.get("extension", ".py")
                if not extension.startswith('.'):
                    extension = '.' + extension
                
                filename = module.get("name", f"module_{module['id']}") + extension
                file_path = os.path.join(category_dir, filename)
                
                # Kontrollera om filen redan finns
                if os.path.exists(file_path):
                    # Lägg till ett suffix för att undvika konflikter
                    base_name = os.path.splitext(filename)[0]
                    counter = 1
                    while os.path.exists(file_path):
                        new_name = f"{base_name}_{counter}{extension}"
                        file_path = os.path.join(category_dir, new_name)
                        counter += 1
                
                # Spara filen
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(module["code"])
                
                exported_count += 1
            
            self.progress_bar.setValue(100)
            self.status_bar.showMessage(
                f"Export klar. Exporterade {exported_count} av {module_count} moduler.", 5000
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Fel vid export", str(e))
        finally:
            # Dölj progressbar efter en liten fördröjning
            QTimer.singleShot(1000, lambda: self.progress_bar.setVisible(False))
    
    def scan_for_modules(self):
        """Scanna efter kodfiler i modulkatalogen och lägg till dem."""
        try:
            # Visa progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_bar.showMessage("Scannar efter moduler...")
            
            # Hämta befintliga filsökvägar för att undvika dubbletter
            existing_paths = [
                module.get("file_path", "") for module in self.code_modules
            ]
            
            # Hämta alla moduler via modulhanteraren
            discovered_modules = self.module_manager.list_modules()
            
            self.progress_bar.setValue(50)
            QApplication.processEvents()
            
            # Lägg till nya moduler
            new_count = 0
            next_id = max([int(m["id"]) for m in self.code_modules] + [-1]) + 1
            
            for discovered in discovered_modules:
                if discovered["path"] not in existing_paths:
                    # Skapa en ny modul
                    module_data = {
                        "id": str(next_id),
                        "name": discovered["name"],
                        "extension": discovered["extension"],
                        "code": discovered["code"],
                        "tags": [],
                        "category": "other",  # Standard-kategori
                        "created": datetime.now().isoformat(),
                        "modified": datetime.now().isoformat(),
                        "description": f"Upptäckt vid scanning: {discovered['path']}",
                        "file_path": discovered["path"],
                        "auto_save": True
                    }
                    
                    # Lägg till modulen i listan
                    self.code_modules.append(module_data)
                    new_count += 1
                    next_id += 1
            
            # Uppdatera UI om vi hittade några nya moduler
            if new_count > 0:
                self.refresh_ui()
                self.update_history()
                self.save_data()
                
                self.status_bar.showMessage(f"Scanning klar. Hittade {new_count} nya moduler.", 5000)
            else:
                self.status_bar.showMessage("Scanning klar. Inga nya moduler hittades.", 3000)
            
            self.progress_bar.setValue(100)
            
        except Exception as e:
            QMessageBox.critical(self, "Fel vid scanning", str(e))
        finally:
            # Dölj progressbar efter en liten fördröjning
            QTimer.singleShot(1000, lambda: self.progress_bar.setVisible(False))
    
    def auto_scan_for_modules(self):
        """Autoscan för nya moduler i bakgrunden."""
        # Hoppa över om vi håller på att ladda eller spara
        if self.is_loading or self.is_saving:
            return
        
        try:
            # Hämta befintliga filsökvägar för att undvika dubbletter
            existing_paths = [
                module.get("file_path", "") for module in self.code_modules
            ]
            
            # Hämta alla moduler via modulhanteraren
            discovered_modules = self.module_manager.list_modules()
            
            # Lägg till nya moduler
            new_count = 0
            next_id = max([int(m["id"]) for m in self.code_modules] + [-1]) + 1
            
            for discovered in discovered_modules:
                if discovered["path"] and discovered["path"] not in existing_paths:
                    # Skapa en ny modul
                    module_data = {
                        "id": str(next_id),
                        "name": discovered["name"],
                        "extension": discovered["extension"],
                        "code": discovered["code"],
                        "tags": [],
                        "category": "other",  # Standard-kategori
                        "created": datetime.now().isoformat(),
                        "modified": datetime.now().isoformat(),
                        "description": f"Automatiskt upptäckt: {discovered['path']}",
                        "file_path": discovered["path"],
                        "auto_save": True
                    }
                    
                    # Lägg till modulen i listan
                    self.code_modules.append(module_data)
                    new_count += 1
                    next_id += 1
            
            # Uppdatera UI om vi hittade några nya moduler
            if new_count > 0:
                self.refresh_ui()
                self.update_history()
                self.save_data()
                
                self.status_bar.showMessage(f"Auto-scanning: Hittade {new_count} nya moduler.", 3000)
        except Exception as e:
            # Logga felet men visa inte för användaren
            print(f"Fel vid auto-scanning: {e}")

class CodeModuleTabWrapper(QWidget):
    """
    En wrapper för kodmodulfliken som ska användas i huvuddashboarden.
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.tab = CodeModuleTab()
        layout.addWidget(self.tab)

