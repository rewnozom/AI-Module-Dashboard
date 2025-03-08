
## =======    PART - 1    ======= ##
# ./ui/code_module_widget.py
import os
import sys
import json
import re
import time
import hashlib
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QMimeData, QPoint, QTimer, QUrl, QSize
from PySide6.QtGui import (
    QFont, QAction, QKeySequence, QDrag, QIcon, QColor, QSyntaxHighlighter, 
    QTextCharFormat, QTextCursor, QPalette, QTextDocument, QKeyEvent, QPainter,
    QTextFormat
)
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QListWidget, QListWidgetItem, QMessageBox, QLabel, QFrame, QScrollArea,
    QCheckBox, QInputDialog, QGridLayout, QGroupBox, QComboBox, QTextEdit,
    QFileDialog, QMenu, QToolButton, QSplitter, QTabWidget, QToolBar, QStatusBar,
    QDialog, QDialogButtonBox, QPlainTextEdit, QCompleter, QTreeWidget, QTreeWidgetItem,
    QWidgetAction
)

class SyntaxHighlighter(QSyntaxHighlighter):
    """Basklassen för syntaxmarkering"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlight_rules = []
        self.setup_rules()
    
    def setup_rules(self):
        """Överskuggas i underklasser för att definiera språkspecifika regler"""
        pass
    
    def highlightBlock(self, text):
        """Applicera markeringsregler på textblocket"""
        for pattern, format in self.highlight_rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)

class PythonSyntaxHighlighter(SyntaxHighlighter):
    """Syntaxmarkering för Python-kod"""
    def setup_rules(self):
        # Keyword format
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "and", "as", "assert", "break", "class", "continue", "def",
            "del", "elif", "else", "except", "False", "finally", "for",
            "from", "global", "if", "import", "in", "is", "lambda", "None",
            "nonlocal", "not", "or", "pass", "raise", "return", "True",
            "try", "while", "with", "yield", "async", "await", "self"
        ]
        for word in keywords:
            pattern = r'\b' + word + r'\b'
            self.highlight_rules.append((re.compile(pattern), keyword_format))
        
        # String format
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self.highlight_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        self.highlight_rules.append((re.compile(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))
        self.highlight_rules.append((re.compile(r'""".*?"""', re.DOTALL), string_format))
        self.highlight_rules.append((re.compile(r"'''.*?'''", re.DOTALL), string_format))
        
        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self.highlight_rules.append((re.compile(r'#[^\n]*'), comment_format))
        
        # Function format
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#DCDCAA"))
        function_format.setFontWeight(QFont.Bold)
        self.highlight_rules.append((re.compile(r'\bdef\s+([a-zA-Z_][a-zA-Z0-9_]*)\b'), function_format))
        
        # Class format
        class_format = QTextCharFormat()
        class_format.setForeground(QColor("#4EC9B0"))
        class_format.setFontWeight(QFont.Bold)
        self.highlight_rules.append((re.compile(r'\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)\b'), class_format))
        
        # Decorator format
        decorator_format = QTextCharFormat()
        decorator_format.setForeground(QColor("#C586C0"))
        self.highlight_rules.append((re.compile(r'@[a-zA-Z_][a-zA-Z0-9_\.]*'), decorator_format))
        
        # Number format
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.highlight_rules.append((re.compile(r'\b[0-9]+\b'), number_format))
        self.highlight_rules.append((re.compile(r'\b0[xX][0-9a-fA-F]+\b'), number_format))
        self.highlight_rules.append((re.compile(r'\b[0-9]+\.[0-9]*\b'), number_format))
        self.highlight_rules.append((re.compile(r'\b\.[0-9]+\b'), number_format))
        
        # Built-in functions format
        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor("#4EC9B0"))
        builtins = [
            "abs", "all", "any", "ascii", "bin", "bool", "bytearray", "bytes", "callable",
            "chr", "classmethod", "compile", "complex", "delattr", "dict", "dir", "divmod",
            "enumerate", "eval", "exec", "filter", "float", "format", "frozenset",
            "getattr", "globals", "hasattr", "hash", "help", "hex", "id", "input",
            "int", "isinstance", "issubclass", "iter", "len", "list", "locals", "map",
            "max", "memoryview", "min", "next", "object", "oct", "open", "ord", "pow",
            "print", "property", "range", "repr", "reversed", "round", "set", "setattr",
            "slice", "sorted", "staticmethod", "str", "sum", "super", "tuple", "type",
            "vars", "zip", "__import__"
        ]
        builtin_pattern = r'\b(' + '|'.join(builtins) + r')\b'
        self.highlight_rules.append((re.compile(builtin_pattern), builtin_format))

class JavaScriptSyntaxHighlighter(SyntaxHighlighter):
    """Syntaxmarkering för JavaScript-kod"""
    def setup_rules(self):
        # Keyword format
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "break", "case", "catch", "class", "const", "continue", "debugger",
            "default", "delete", "do", "else", "export", "extends", "false",
            "finally", "for", "function", "if", "import", "in", "instanceof",
            "new", "null", "return", "super", "switch", "this", "throw", "true",
            "try", "typeof", "var", "void", "while", "with", "yield", "let",
            "static", "get", "set", "async", "await"
        ]
        for word in keywords:
            pattern = r'\b' + word + r'\b'
            self.highlight_rules.append((re.compile(pattern), keyword_format))
        
        # String format
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self.highlight_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        self.highlight_rules.append((re.compile(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))
        self.highlight_rules.append((re.compile(r'`[^`\\]*(\\.[^`\\]*)*`'), string_format))
        
        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self.highlight_rules.append((re.compile(r'//[^\n]*'), comment_format))
        self.highlight_rules.append((re.compile(r'/\*.*?\*/', re.DOTALL), comment_format))
        
        # Function format
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#DCDCAA"))
        function_format.setFontWeight(QFont.Bold)
        self.highlight_rules.append((re.compile(r'\bfunction\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\b'), function_format))
        self.highlight_rules.append((re.compile(r'\b([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\('), function_format))
        self.highlight_rules.append((re.compile(r'\b([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*function\b'), function_format))
        self.highlight_rules.append((re.compile(r'\b([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*\(.*?\)\s*=>\s*', re.DOTALL), function_format))
        
        # Number format
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.highlight_rules.append((re.compile(r'\b[0-9]+\b'), number_format))
        self.highlight_rules.append((re.compile(r'\b0[xX][0-9a-fA-F]+\b'), number_format))
        self.highlight_rules.append((re.compile(r'\b[0-9]+\.[0-9]*\b'), number_format))
        self.highlight_rules.append((re.compile(r'\b\.[0-9]+\b'), number_format))

class CodeEditor(QPlainTextEdit):
    """
    Avancerad kodredigerare med radnumrering och syntaxmarkering
    """
    contentChanged = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.textChanged.connect(self.on_text_changed)
        
        # Uppdatera marginaler för radnummer
        self.updateLineNumberAreaWidth(0)
        
        # Konfigurera teckensnitt för kodredigerare
        font = QFont("Consolas", 11)
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Standardinställningar
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 4)
        
        # Autospara-timer
        self.last_saved_content = ""
        self.save_timer = QTimer(self)
        self.save_timer.setInterval(2000)  # 2 sekunder
        self.save_timer.timeout.connect(self.check_for_changes)
        self.save_timer.start()
        
        # Markera aktuell rad
        self.highlightCurrentLine()
        
        # Aktivera stödlinjer för indentering
        self.setIndentationGuides(True)
    
    def on_text_changed(self):
        """Anropas när texten ändras"""
        self.contentChanged.emit()
    
    def check_for_changes(self):
        """Kontrollerar om innehållet har ändrats sedan senaste sparningen"""
        current_content = self.toPlainText()
        if current_content != self.last_saved_content:
            self.contentChanged.emit()
    
    def lineNumberAreaWidth(self):
        """Beräkna bredd för radnummerområdet baserat på antalet rader"""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num /= 10
            digits += 1
        
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def updateLineNumberAreaWidth(self, _):
        """Uppdatera bredden på radnummerområdet"""
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)
    
    def updateLineNumberArea(self, rect, dy):
        """Uppdatera radnummerområdet när synlig vy ändras"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)
    
    def resizeEvent(self, event):
        """Hantera storleksändring och uppdatera radnummerområdet"""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height())
    
    def lineNumberAreaPaintEvent(self, event):
        """Rita radnummer i radnummerområdet"""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#1E1E1E"))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#AAAAAA"))
                painter.drawText(0, top, self.line_number_area.width() - 5, self.fontMetrics().height(),
                                Qt.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
    
    def highlightCurrentLine(self):
        """Markera den aktuella raden"""
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#282828")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)
    
    def setIndentationGuides(self, enable):
        """Ställ in om indenteringsguider ska visas"""
        if enable:
            # Skulle implementera anpassade ritfunktioner för indenteringsguider
            pass
    
    def keyPressEvent(self, event):
        """Hantera tangentbordshändelser för särskilda kodningsfunktioner"""
        if event.key() == Qt.Key_Tab:
            # Indentera med mellanslag istället för tabbar
            cursor = self.textCursor()
            if cursor.hasSelection():
                # Indentera markerade rader
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
                cursor.setPosition(start)
                cursor.movePosition(QTextCursor.StartOfLine)
                cursor.setPosition(end, QTextCursor.KeepAnchor)
                if not cursor.atBlockEnd():
                    cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
                
                selected_text = cursor.selectedText()
                lines = selected_text.split('\u2029')
                
                new_text = []
                for line in lines:
                    new_text.append("    " + line)
                
                cursor.removeSelectedText()
                cursor.insertText('\n'.join(new_text))
            else:
                # Indentera bara nuvarande position
                cursor.insertText("    ")
            return
        elif event.key() == Qt.Key_Backtab:
            # Ta bort indentering (shift+tab)
            cursor = self.textCursor()
            if cursor.hasSelection():
                # Ta bort indentering från markerade rader
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
                cursor.setPosition(start)
                cursor.movePosition(QTextCursor.StartOfLine)
                cursor.setPosition(end, QTextCursor.KeepAnchor)
                if not cursor.atBlockEnd():
                    cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
                
                selected_text = cursor.selectedText()
                lines = selected_text.split('\u2029')
                
                new_text = []
                for line in lines:
                    if line.startswith("    "):
                        new_text.append(line[4:])
                    elif line.startswith("\t"):
                        new_text.append(line[1:])
                    else:
                        new_text.append(line)
                
                cursor.removeSelectedText()
                cursor.insertText('\n'.join(new_text))
            return
        elif event.key() == Qt.Key_Return:
            # Automatisk indentering vid Enter
            cursor = self.textCursor()
            line = cursor.block().text()
            indent = re.match(r'(\s*)', line).group(1)
            
            if line.rstrip().endswith(':'):
                indent += "    "
            
            super().keyPressEvent(event)
            cursor = self.textCursor()
            cursor.insertText(indent)
            return
        
        # Fortsätt med standardbeteende för andra tangenter
        super().keyPressEvent(event)

class LineNumberArea(QWidget):
    """Widget för att visa radnummer bredvid kodeditorn"""
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
    
    def sizeHint(self):
        """Returnera lämplig storlek baserat på redigeraren"""
        return QSize(self.editor.lineNumberAreaWidth(), 0)
    
    def paintEvent(self, event):
        """Delegera ritning till redigeraren"""
        self.editor.lineNumberAreaPaintEvent(event)






## =======    PART - 2    ======= ##


class ClickableLabel(QLabel):
    """En klickbar etikett för att redigera namn"""
    clicked = Signal()
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

class CodeModuleWidget(QFrame):
    """
    En förbättrad widget för att hantera en kodmodul med stöd för automatisk sparning,
    filsystemsintegration och avancerad kodeditor.
    """
    # Signaler för kommunikation med överordnade widgets
    moduleAdded = Signal(str, dict)
    moduleRemoved = Signal(str)
    moduleUpdated = Signal(str, str, dict)  # module_id, update_type, module_data
    
    def __init__(self, module_id, module_data=None, modules_directory="./modules/"):
        super().__init__()
        
        # Initialisera code_editor till None - viktigt att göra detta INNAN någon metod anropas som kan använda den
        self.code_editor = None
        
        self.module_id = module_id
        self.modules_directory = Path(modules_directory)
        
        # Standardvärden om inget module_data angavs
        if module_data is None:
            module_data = {
                "name": f"modul_{module_id}",
                "extension": ".py",
                "code": "",
                "tags": [],
                "category": "other",
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat(),
                "description": "",
                "file_path": "",
                "auto_save": True
            }
        
        self.module_data = module_data
        
        # Säkerställ att modulen har alla nödvändiga fält
        self._ensure_module_data_fields()
        
        # Skapa en unik hash-identifierare för modulen
        self.module_hash = self._generate_module_hash()
        
        # Spara om automatisk sparning är på
        self.auto_save = self.module_data.get("auto_save", True)
        
        # Historikspårning för ångra/gör om
        self.history = []
        self.history_index = -1
        
        # Funktionsanalys och cache
        self.function_cache = {}
        self.class_cache = {}
        self.variable_cache = {}
        
        # Initiera UI - detta kommer att skapa code_editor
        self.initUI()
        
        # Sätt flaggor för att spåra ändringar
        self.is_dirty = False
        self.last_saved_code = self.module_data.get("code", "")
        
        # Anslut ändringar till uppdateringsfunktion - nu EFTER code_editor skapats
        self.code_editor.contentChanged.connect(self.on_content_changed)
        
        # Autospara-timer
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.setInterval(2000)  # 2 sekunder
        self.auto_save_timer.timeout.connect(self.auto_save_if_needed)
        if self.auto_save:
            self.auto_save_timer.start()
        
        # Uppdatera UI från moduldata
        self.refresh_from_data()
        
        # Parsera koden för att hitta funktioner, klasser och variabler
        self.update_code_structure_cache()
    
    def _ensure_module_data_fields(self):
        """Säkerställ att alla nödvändiga fält finns i module_data"""
        required_fields = {
            "name": f"modul_{self.module_id}",
            "extension": ".py",
            "code": "",
            "tags": [],
            "category": "other",
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "description": "",
            "file_path": "",
            "auto_save": True
        }
        
        for field, default in required_fields.items():
            if field not in self.module_data:
                self.module_data[field] = default
    
    def _generate_module_hash(self):
        """Generera en unik hash för denna modul"""
        unique_str = f"{self.module_id}_{self.module_data['name']}_{time.time()}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:8]
    
    def initUI(self):
        """Initiera användargränssnittet för modulwidgeten"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Stilar för widgeten
        self.setStyleSheet("""
            QFrame {
                background-color: #2E2E2E;
                border: 2px solid #555;
                border-radius: 10px;
            }
            QLabel {
                color: #FFFFFF;
                background: transparent;
            }
            QPlainTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: 1px solid #555;
                border-radius: 5px;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            QLineEdit {
                background-color: #3C3C3C;
                color: #FFFFFF;
                border: 1px solid #555;
                padding: 5px;
                border-radius: 5px;
            }
            QStatusBar {
                background-color: #3C3C3C;
                color: #AAAAAA;
                border-top: 1px solid #555;
                border-radius: 0px 0px 5px 5px;
            }
            QToolButton {
                background-color: transparent;
                border: none;
                color: white;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #4C4C4C;
                border-radius: 5px;
            }
        """)
        
        # Topp-delen: Modulnamn och kontroller
        header_layout = QHBoxLayout()
        
        # Vänster sida: Namn och filändelse
        left_layout = QHBoxLayout()
        
        # Namnetikett (klickbar för redigering)
        self.name_label = ClickableLabel(self.module_data["name"])
        self.name_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.name_label.setStyleSheet("color: #FFFFFF; padding: 2px 5px;")
        self.name_label.setToolTip("Klicka för att redigera modulnamn")
        self.name_label.clicked.connect(self.edit_name)
        left_layout.addWidget(self.name_label)
        
        # Filändelse
        self.extension_input = QLineEdit(self.module_data["extension"])
        self.extension_input.setFixedWidth(50)
        self.extension_input.setToolTip("Filändelse (t.ex. .py)")
        self.extension_input.textChanged.connect(self.update_extension)
        left_layout.addWidget(self.extension_input)
        
        header_layout.addLayout(left_layout)
        header_layout.addStretch()
        
        # Höger sida: Knappar för funktioner
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setStyleSheet("""
            QToolBar {
                background-color: transparent;
                border: none;
                spacing: 2px;
            }
        """)
        
        # Skapa alla knappar
        self.create_toolbar_buttons()
        
        header_layout.addWidget(self.toolbar)
        main_layout.addLayout(header_layout)
        
        # Mittsektion: Flikar för kod, dokumentation, etc.
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #555;
                border-radius: 5px;
                background-color: #2E2E2E;
            }
            QTabBar::tab {
                background-color: #3C3C3C;
                color: #CCCCCC;
                border: 1px solid #555;
                border-bottom-color: #555;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 5px 10px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            QTabBar::tab:hover {
                background-color: #4C4C4C;
            }
        """)
        
        # Kodredigeringsfliken
        self.code_editor = CodeEditor()
        if self.module_data["extension"].lower().endswith('.py'):
            self.highlighter = PythonSyntaxHighlighter(self.code_editor.document())
        elif self.module_data["extension"].lower().endswith('.js'):
            self.highlighter = JavaScriptSyntaxHighlighter(self.code_editor.document())
        
        self.tab_widget.addTab(self.code_editor, "Kod")
        
        # Fliken för dokumentation/metadata
        self.doc_widget = QWidget()
        doc_layout = QVBoxLayout(self.doc_widget)
        
        doc_form = QGridLayout()
        
        # Beskrivning
        doc_form.addWidget(QLabel("Beskrivning:"), 0, 0)
        self.description_edit = QLineEdit(self.module_data.get("description", ""))
        self.description_edit.setPlaceholderText("Ange en kort beskrivning av modulen")
        self.description_edit.textChanged.connect(self.update_description)
        doc_form.addWidget(self.description_edit, 0, 1)
        
        # Kategori
        doc_form.addWidget(QLabel("Kategori:"), 1, 0)
        self.category_combo = QComboBox()
        categories = ["other", "ui", "utils", "data", "network", "db", "ai", "algorithms"]
        self.category_combo.addItems(categories)
        
        current_category = self.module_data.get("category", "other")
        index = self.category_combo.findText(current_category)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        
        self.category_combo.currentTextChanged.connect(self.update_category)
        doc_form.addWidget(self.category_combo, 1, 1)
        
        # Taggar
        doc_form.addWidget(QLabel("Taggar:"), 2, 0)
        self.tags_edit = QLineEdit(", ".join(self.module_data.get("tags", [])))
        self.tags_edit.setPlaceholderText("Ange taggar separerade med kommatecken")
        self.tags_edit.textChanged.connect(self.update_tags)
        doc_form.addWidget(self.tags_edit, 2, 1)
        
        # Filsökväg (skrivskyddad)
        doc_form.addWidget(QLabel("Filsökväg:"), 3, 0)
        self.file_path_label = QLabel(str(self.module_data.get("file_path", "Ingen fil sparad")))
        self.file_path_label.setStyleSheet("color: #AAAAAA;")
        doc_form.addWidget(self.file_path_label, 3, 1)
        
        # Skapat / Ändrat
        doc_form.addWidget(QLabel("Skapad:"), 4, 0)
        created_date = datetime.fromisoformat(self.module_data.get("created", datetime.now().isoformat()))
        self.created_label = QLabel(created_date.strftime("%Y-%m-%d %H:%M"))
        self.created_label.setStyleSheet("color: #AAAAAA;")
        doc_form.addWidget(self.created_label, 4, 1)
        
        doc_form.addWidget(QLabel("Ändrad:"), 5, 0)
        modified_date = datetime.fromisoformat(self.module_data.get("modified", datetime.now().isoformat()))
        self.modified_label = QLabel(modified_date.strftime("%Y-%m-%d %H:%M"))
        self.modified_label.setStyleSheet("color: #AAAAAA;")
        doc_form.addWidget(self.modified_label, 5, 1)
        
        # Autospara-inställning
        doc_form.addWidget(QLabel("Autospara:"), 6, 0)
        self.auto_save_checkbox = QCheckBox()
        self.auto_save_checkbox.setChecked(self.auto_save)
        self.auto_save_checkbox.stateChanged.connect(self.toggle_auto_save)
        doc_form.addWidget(self.auto_save_checkbox, 6, 1)
        
        doc_layout.addLayout(doc_form)
        doc_layout.addStretch()
        
        self.tab_widget.addTab(self.doc_widget, "Metadata")
        
        # Fliken för struktur (funktioner/klasser/variabler)
        self.structure_widget = QWidget()
        structure_layout = QVBoxLayout(self.structure_widget)
        
        self.structure_tree = QTreeWidget()
        self.structure_tree.setHeaderLabels(["Namn", "Typ", "Rad"])
        self.structure_tree.setColumnWidth(0, 200)
        self.structure_tree.setColumnWidth(1, 100)
        self.structure_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: 1px solid #555;
                border-radius: 5px;
            }
            QTreeWidget::item:selected {
                background-color: #3C3C3C;
            }
            QTreeWidget::item:hover {
                background-color: #2C2C2C;
            }
        """)
        self.structure_tree.itemDoubleClicked.connect(self.navigate_to_item)
        
        structure_layout.addWidget(self.structure_tree)
        
        # Sökfält för att hitta specifika element
        structure_search_layout = QHBoxLayout()
        self.structure_search_input = QLineEdit()
        self.structure_search_input.setPlaceholderText("Sök i struktur...")
        self.structure_search_input.returnPressed.connect(self.search_structure)
        structure_search_layout.addWidget(self.structure_search_input)
        
        structure_search_btn = QPushButton("Sök")
        structure_search_btn.clicked.connect(self.search_structure)
        structure_search_layout.addWidget(structure_search_btn)
        
        structure_layout.addLayout(structure_search_layout)
        
        self.tab_widget.addTab(self.structure_widget, "Struktur")
        
        # LLM-integrationsfliken
        self.llm_widget = QWidget()
        llm_layout = QVBoxLayout(self.llm_widget)
        
        # Instruktioner för LLM-användning
        llm_help = QLabel("Denna flik används för att integrera med AI/LLM-system. Här kan du:")
        llm_help.setWordWrap(True)
        llm_layout.addWidget(llm_help)
        
        llm_help_list = QLabel(
            "• Klistra in kodbidrag från en AI<br>"
            "• Uppdatera specifika funktioner<br>"
            "• Lägga till nya funktioner<br>"
            "• Ändra variabelvärden eller egenskaper"
        )
        llm_help_list.setStyleSheet("color: #AAAAAA;")
        llm_layout.addWidget(llm_help_list)
        
        # Åtgärdsval
        llm_action_layout = QHBoxLayout()
        llm_action_layout.addWidget(QLabel("Åtgärd:"))
        
        self.llm_action_combo = QComboBox()
        self.llm_action_combo.addItems([
            "Lägg till funktion/klass",
            "Uppdatera funktion/klass",
            "Ändra variabel",
            "Erbjud strukturförslag"
        ])
        llm_action_layout.addWidget(self.llm_action_combo)
        
        llm_layout.addLayout(llm_action_layout)
        
        # Målelement (funktion/klass att uppdatera)
        llm_target_layout = QHBoxLayout()
        llm_target_layout.addWidget(QLabel("Målnamn:"))
        
        self.llm_target_combo = QComboBox()
        self.llm_target_combo.setEditable(True)
        llm_target_layout.addWidget(self.llm_target_combo)
        
        llm_layout.addLayout(llm_target_layout)
        
        # Kodinmatning från LLM
        llm_layout.addWidget(QLabel("Klistra in kod från AI:"))
        
        self.llm_code_edit = QPlainTextEdit()
        self.llm_code_edit.setMinimumHeight(150)
        llm_layout.addWidget(self.llm_code_edit)
        
        # Knapp för att tillämpa LLM-ändringar
        llm_button_layout = QHBoxLayout()
        
        apply_llm_btn = QPushButton("Tillämpa ändring")
        apply_llm_btn.clicked.connect(self.apply_llm_changes)
        llm_button_layout.addWidget(apply_llm_btn)
        
        validate_llm_btn = QPushButton("Validera kod")
        validate_llm_btn.clicked.connect(self.validate_llm_code)
        llm_button_layout.addWidget(validate_llm_btn)
        
        llm_button_layout.addStretch()
        
        llm_layout.addLayout(llm_button_layout)
        
        # Resultat av LLM-operation
        llm_layout.addWidget(QLabel("Resultat:"))
        
        self.llm_result_edit = QPlainTextEdit()
        self.llm_result_edit.setReadOnly(True)
        self.llm_result_edit.setMinimumHeight(100)
        llm_layout.addWidget(self.llm_result_edit)
        
        self.tab_widget.addTab(self.llm_widget, "AI Integration")
        
        main_layout.addWidget(self.tab_widget)
        
        # Nederst: Statusinformation och sökruta
        bottom_layout = QHBoxLayout()
        
        # Statusfält
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        self.status_bar.setStyleSheet("QStatusBar { border: none; }")
        self.status_bar.showMessage("Redo")
        
        # Sökfält
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Sök eller lägg till funktion...")
        self.search_input.setStyleSheet("padding: 5px;")
        self.search_input.setFixedHeight(30)
        self.search_input.returnPressed.connect(self.search_or_add_function)
        
        search_btn = QPushButton("➕")
        search_btn.setToolTip("Sök eller lägg till funktion")
        search_btn.setFixedSize(30, 30)
        search_btn.clicked.connect(self.search_or_add_function)
        
        bottom_layout.addWidget(self.status_bar, 3)
        bottom_layout.addWidget(self.search_input, 2)
        bottom_layout.addWidget(search_btn, 0)
        
        main_layout.addLayout(bottom_layout)
    
    def create_toolbar_buttons(self):
        """Skapa knappar för verktygsfältet"""
        # Spara
        save_action = QAction("💾", self)
        save_action.setToolTip("Spara modul")
        save_action.triggered.connect(self.save_module)
        self.toolbar.addAction(save_action)
        
        # Importera från fil
        import_action = QAction("📂", self)
        import_action.setToolTip("Importera från fil")
        import_action.triggered.connect(self.import_from_file)
        self.toolbar.addAction(import_action)
        
        # Exportera
        export_action = QAction("📤", self)
        export_action.setToolTip("Exportera till fil")
        export_action.triggered.connect(self.export_to_file)
        self.toolbar.addAction(export_action)
        
        # Taggar
        tag_action = QAction("🏷️", self)
        tag_action.setToolTip("Hantera taggar")
        tag_action.triggered.connect(self.edit_tags_dialog)
        self.toolbar.addAction(tag_action)
        
        # Ångra - använd en wrapper-funktion istället för direktkoppling
        undo_action = QAction("↩️", self)
        undo_action.setToolTip("Ångra (Ctrl+Z)")
        undo_action.triggered.connect(self.do_undo)
        self.toolbar.addAction(undo_action)
        
        # Göra om - använd en wrapper-funktion istället för direktkoppling
        redo_action = QAction("↪️", self)
        redo_action.setToolTip("Gör om (Ctrl+Y)")
        redo_action.triggered.connect(self.do_redo)
        self.toolbar.addAction(redo_action)
        
        # Ta bort modul
        delete_action = QAction("🗑️", self)
        delete_action.setToolTip("Ta bort modul")
        delete_action.triggered.connect(self.delete_module)
        self.toolbar.addAction(delete_action)

    def do_undo(self):
        """Säker wrapper för undo-funktionen"""
        if hasattr(self, 'code_editor') and self.code_editor is not None:
            self.code_editor.undo()

    def do_redo(self):
        """Säker wrapper för redo-funktionen"""
        if hasattr(self, 'code_editor') and self.code_editor is not None:
            self.code_editor.redo()


    def delete_module(self):
        """Ta bort modulen"""
        # Bekräfta med användaren innan borttagning
        reply = QMessageBox.question(
            self, "Bekräfta borttagning", 
            f"Är du säker på att du vill ta bort modulen '{self.module_data['name']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Ta bort filen om den existerar
            if self.module_data.get("file_path", ""):
                try:
                    file_path = Path(self.module_data["file_path"])
                    if file_path.exists():
                        file_path.unlink()  # Ta bort filen
                except Exception as e:
                    QMessageBox.warning(self, "Fel vid borttagning", 
                                    f"Kunde inte ta bort filen: {e}")
            
            # Meddela överordnade widgets om borttagningen
            self.moduleRemoved.emit(self.module_id)
            
            # Ta bort widgeten från föräldraobjektet
            if self.parent():
                layout = self.parent().layout()
                if layout:
                    layout.removeWidget(self)
            
            # Radera widget
            self.deleteLater()

    def update_description(self, description):
        """Uppdatera modulbeskrivningen"""
        self.module_data["description"] = description
        self.is_dirty = True
        self.moduleUpdated.emit(self.module_id, "description", self.module_data)
        self.auto_save_if_needed()


    def update_category(self, category):
        """Uppdatera modulkategorin"""
        old_category = self.module_data.get("category", "other")
        self.module_data["category"] = category
        self.is_dirty = True
        self.moduleUpdated.emit(self.module_id, "category", self.module_data)
        
        # Om filen redan är sparad, flytta den till den nya kategorimappen
        if self.module_data.get("file_path", ""):
            old_path = Path(self.module_data["file_path"])
            if old_path.exists():
                try:
                    # Skapa den nya kategorimappen om den inte finns
                    new_dir = self.modules_directory / category
                    new_dir.mkdir(exist_ok=True, parents=True)
                    
                    # Skapa den nya sökvägen
                    new_path = new_dir / old_path.name
                    
                    # Flytta filen
                    old_path.rename(new_path)
                    
                    # Uppdatera filsökvägen
                    self.module_data["file_path"] = str(new_path)
                    self.file_path_label.setText(str(new_path))
                except Exception as e:
                    QMessageBox.warning(self, "Fel vid kategoriändring", 
                                    f"Kunde inte flytta filen till ny kategori: {e}")
                    # Återställ kategorin vid fel
                    self.module_data["category"] = old_category
                    self.category_combo.blockSignals(True)
                    self.category_combo.setCurrentText(old_category)
                    self.category_combo.blockSignals(False)
        
        self.auto_save_if_needed()

    def update_tags(self, tags_text):
        """Uppdatera taggar från textfältet"""
        self._update_tags_from_text(tags_text)

    def _update_tags_from_text(self, tags_text):
        """Intern metod för att uppdatera taggar från text"""
        # Dela upp taggarna, rensa vitspace och ta bort dubbletter
        tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
        tags = list(dict.fromkeys(tags))  # Ta bort dubletter men behåll ordning
        
        self.module_data["tags"] = tags
        self.is_dirty = True
        self.moduleUpdated.emit(self.module_id, "tags", self.module_data)
        self.auto_save_if_needed()

    def toggle_auto_save(self, state):
        """Växla automatisk sparning på/av"""
        self.auto_save = (state == Qt.Checked)
        self.module_data["auto_save"] = self.auto_save
        
        if self.auto_save:
            self.auto_save_timer.start()
        else:
            self.auto_save_timer.stop()
        
        self.moduleUpdated.emit(self.module_id, "auto_save", self.module_data)


    def navigate_to_item(self, item, column):
        """Navigera till vald funktion/klass/variabel i koden"""
        if not hasattr(self, 'code_editor') or self.code_editor is None:
            QMessageBox.warning(self, "Initialiseringsfel", "Kodredigeraren är inte initialiserad.")
            return
        
        # Hämta data från det valda objektet
        item_type = item.text(1)  # Andra kolumnen innehåller typen
        item_name = item.text(0)  # Första kolumnen innehåller namnet
        item_line = item.text(2)  # Tredje kolumnen innehåller radnummer
        
        if not item_line:
            # Detta är en kategorirad (Funktioner, Klasser, Variabler)
            return
        
        try:
            # Konvertera radnummret till en int
            line_number = int(item_line) - 1  # 0-baserat index för texteditor
            
            # Skapa en cursor och flytta den till rätt rad
            cursor = self.code_editor.textCursor()
            block = self.code_editor.document().findBlockByLineNumber(line_number)
            cursor.setPosition(block.position())
            
            # Markera hela raden
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            
            # Ange den nya cursorpositionen
            self.code_editor.setTextCursor(cursor)
            
            # Scrollar till den valda raden
            self.code_editor.centerCursor()
            
            # Byt till kodfliken
            self.tab_widget.setCurrentIndex(0)  # Anta att kodflik är den första fliken
        except (ValueError, AttributeError, Exception) as e:
            QMessageBox.warning(self, "Navigeringsfel", f"Kunde inte navigera till raden: {e}")

    def search_structure(self):
        """Sök igenom strukturträdet efter matchande element"""
        if not hasattr(self, 'structure_search_input') or not hasattr(self, 'structure_tree'):
            QMessageBox.warning(self, "Initialiseringsfel", "Sökfunktionen är inte korrekt initialiserad.")
            return
        
        search_text = self.structure_search_input.text().strip().lower()
        if not search_text:
            return
        
        # Återställ alla trädobjekt (visa alla)
        for i in range(self.structure_tree.topLevelItemCount()):
            top_item = self.structure_tree.topLevelItem(i)
            top_item.setHidden(False)
            for j in range(top_item.childCount()):
                child_item = top_item.child(j)
                child_item.setHidden(False)
                for k in range(child_item.childCount()):
                    child_item.child(k).setHidden(False)
        
        # Om söktexten är tom, avsluta
        if not search_text:
            return
        
        # Flagga för att hålla reda på om något matchade
        found_match = False
        
        # Gå igenom alla huvudkategorier (Funktioner, Klasser, Variabler)
        for i in range(self.structure_tree.topLevelItemCount()):
            top_item = self.structure_tree.topLevelItem(i)
            category_has_match = False
            
            # Gå igenom alla underkategorier (funktioner, klasser, etc.)
            for j in range(top_item.childCount()):
                child_item = top_item.child(j)
                item_name = child_item.text(0).lower()
                
                # Kolla om namnet matchar söktexten
                if search_text in item_name:
                    category_has_match = True
                    found_match = True
                    
                    # Expandera föräldraobjektet
                    top_item.setExpanded(True)
                    
                    # Markera om det exakt matchar
                    if item_name == search_text:
                        self.structure_tree.setCurrentItem(child_item)
                else:
                    # Göm objekt som inte matchar
                    child_item.setHidden(True)
                    
                    # Men kolla om något av barnen matchar (parametrar för funktioner)
                    child_has_match = False
                    for k in range(child_item.childCount()):
                        param_item = child_item.child(k)
                        param_name = param_item.text(0).lower()
                        if search_text in param_name:
                            child_has_match = True
                            category_has_match = True
                            found_match = True
                            param_item.setHidden(False)
                        else:
                            param_item.setHidden(True)
                    
                    # Visa förälderobjektet om något av barnen matchade
                    if child_has_match:
                        child_item.setHidden(False)
                        top_item.setExpanded(True)
                        child_item.setExpanded(True)
            
            # Göm huvudkategorin om inga matchningar fanns
            if not category_has_match:
                top_item.setHidden(True)
        
        # Visa ett meddelande om inga matchningar hittades
        if not found_match:
            self.status_bar.showMessage(f"Inga matchningar för '{search_text}'", 3000)
        else:
            self.status_bar.showMessage(f"Sökresultat för '{search_text}'", 3000)

    def search_or_add_function(self):
        """Sök efter eller lägg till funktioner baserat på söktext"""
        if not hasattr(self, 'search_input') or not hasattr(self, 'code_editor'):
            QMessageBox.warning(self, "Initialiseringsfel", "Sökfunktionen är inte korrekt initialiserad.")
            return
        
        search_text = self.search_input.text().strip()
        if not search_text:
            return
        
        # Kontrollera om texten matchar en befintlig funktion, klass eller variabel
        found = False
        
        # Sök i funktioner
        if search_text in self.function_cache:
            found = True
            # Navigera till funktionen
            function_info = self.function_cache[search_text]
            line_number = function_info.get("lineno", 1) - 1
            self._navigate_to_line(line_number)
            self.status_bar.showMessage(f"Hittade funktion: {search_text}", 3000)
        
        # Sök i klasser
        elif search_text in self.class_cache:
            found = True
            # Navigera till klassen
            class_info = self.class_cache[search_text]
            line_number = class_info.get("lineno", 1) - 1
            self._navigate_to_line(line_number)
            self.status_bar.showMessage(f"Hittade klass: {search_text}", 3000)
        
        # Sök i variabler
        elif search_text in self.variable_cache:
            found = True
            # Navigera till variabeln
            var_info = self.variable_cache[search_text]
            line_number = var_info.get("lineno", 1) - 1
            self._navigate_to_line(line_number)
            self.status_bar.showMessage(f"Hittade variabel: {search_text}", 3000)
        
        # Om ingen matchning hittades, fråga om användaren vill lägga till funktionen
        if not found:
            reply = QMessageBox.question(
                self, "Lägg till funktion", 
                f"Ingen matchning för '{search_text}'. Vill du lägga till en ny funktion med detta namn?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.add_new_function(search_text)
        
        # Rensa sökfältet
        self.search_input.clear()

    def _navigate_to_line(self, line_number):
        """Navigera till en specifik rad i kod-editorn"""
        if not hasattr(self, 'code_editor') or self.code_editor is None:
            return
        
        try:
            # Skapa en cursor och flytta den till rätt rad
            cursor = self.code_editor.textCursor()
            block = self.code_editor.document().findBlockByLineNumber(line_number)
            cursor.setPosition(block.position())
            
            # Markera hela raden
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            
            # Ange den nya cursorpositionen
            self.code_editor.setTextCursor(cursor)
            
            # Scrollar till den valda raden
            self.code_editor.centerCursor()
            
            # Byt till kodfliken
            self.tab_widget.setCurrentIndex(0)  # Anta att kodflik är den första fliken
        except Exception as e:
            # Tyst hantering av fel - detta är en hjälpmetod
            pass




    def edit_name(self):
        """Redigera modulnamnet."""
        current_name = self.module_data["name"]
        new_name, ok = QInputDialog.getText(
            self, "Redigera modulnamn", "Nytt namn:", 
            QLineEdit.Normal, current_name
        )
        
        if ok and new_name and new_name != current_name:
            self.module_data["name"] = new_name
            self.name_label.setText(new_name)
            self.moduleUpdated.emit(self.module_id, "name", self.module_data)
            self.is_dirty = True
            
            # Uppdatera filsökväg om modulen är sparad
            if self.module_data.get("file_path", ""):
                # Ersätta gamla filnamnet med det nya
                old_path = Path(self.module_data["file_path"])
                new_path = old_path.parent / f"{new_name}{old_path.suffix}"
                
                if old_path.exists():
                    try:
                        # Byt namn på filen om den existerar
                        old_path.rename(new_path)
                        self.module_data["file_path"] = str(new_path)
                        self.file_path_label.setText(str(new_path))
                    except Exception as e:
                        QMessageBox.warning(self, "Fel vid namnbyte", 
                                        f"Kunde inte byta namn på filen: {e}")
                        # Återställ modulnamnet om filbytet misslyckas
                        self.module_data["name"] = current_name
                        self.name_label.setText(current_name)
                else:
                    # Uppdatera bara sökvägen för framtida sparningar
                    self.module_data["file_path"] = str(new_path)
                    self.file_path_label.setText(str(new_path))
            
            self.auto_save_if_needed()

    def update_extension(self, extension):
        """Uppdatera filändelsen"""
        # Säkerställ att filändelsen börjar med punkt
        if not extension.startswith('.'):
            extension = f".{extension}"
            # Blockera signaler för att undvika rekursion
            self.extension_input.blockSignals(True)
            self.extension_input.setText(extension)
            self.extension_input.blockSignals(False)
        
        self.module_data["extension"] = extension
        self.moduleUpdated.emit(self.module_id, "extension", self.module_data)
        
        # Uppdatera syntax highlighter baserat på filändelse
        self.update_syntax_highlighter()
        
        # Uppdatera filsökväg om modulen är sparad
        if self.module_data.get("file_path", ""):
            old_path = Path(self.module_data["file_path"])
            new_path = old_path.parent / f"{old_path.stem}{extension}"
            
            if old_path.exists():
                try:
                    # Byt filändelse på filen om den existerar
                    old_path.rename(new_path)
                    self.module_data["file_path"] = str(new_path)
                    self.file_path_label.setText(str(new_path))
                except Exception as e:
                    QMessageBox.warning(self, "Fel vid filändring", 
                                    f"Kunde inte ändra filändelse: {e}")
                    # Återställ filändelsen om bytet misslyckas
                    self.extension_input.blockSignals(True)
                    self.extension_input.setText(old_path.suffix)
                    self.extension_input.blockSignals(False)
                    self.module_data["extension"] = old_path.suffix
            else:
                # Uppdatera bara sökvägen för framtida sparningar
                self.module_data["file_path"] = str(new_path)
                self.file_path_label.setText(str(new_path))
        
        self.is_dirty = True
        self.auto_save_if_needed()


    def save_module(self, silent=False):
        """Spara modulen till fil"""
        if self.module_data.get("file_path", ""):
            # Om modulen redan har en filsökväg, spara direkt
            try:
                with open(self.module_data["file_path"], 'w', encoding='utf-8') as f:
                    f.write(self.code_editor.toPlainText())
                
                self.last_saved_code = self.code_editor.toPlainText()
                self.is_dirty = False
                
                if not silent:
                    self.status_bar.showMessage(f"Sparad till {self.module_data['file_path']}", 3000)
                
                return True
            except Exception as e:
                if not silent:
                    QMessageBox.critical(self, "Fel vid sparande", str(e))
                return False
        else:
            # Annars skapa en ny fil
            return self._save_module_to_file(silent)
        
    def _save_module_to_file(self, silent=False):
        """Spara modulen till en ny fil"""
        try:
            # Skapa mappstruktur baserat på kategori
            category_dir = self.modules_directory / self.module_data["category"]
            os.makedirs(category_dir, exist_ok=True)
            
            # Generera filnamn baserat på modulnamn och filändelse
            filename = self.module_data["name"] + self.module_data["extension"]
            file_path = category_dir / filename
            
            # Kontrollera om filen redan finns
            if file_path.exists() and not silent:
                reply = QMessageBox.question(
                    self, "Filen finns redan", 
                    f"Filen {file_path} finns redan. Vill du skriva över den?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.No:
                    # Be användaren om ett nytt namn
                    new_name, ok = QInputDialog.getText(
                        self, "Nytt filnamn", "Ange nytt filnamn:", 
                        QLineEdit.Normal, self.module_data["name"]
                    )
                    
                    if ok and new_name:
                        self.module_data["name"] = new_name
                        self.name_label.setText(new_name)
                        filename = new_name + self.module_data["extension"]
                        file_path = category_dir / filename
                    else:
                        return False
            
            # Spara filen
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.code_editor.toPlainText())
            
            # Uppdatera moduldata
            self.module_data["file_path"] = str(file_path)
            self.file_path_label.setText(str(file_path))
            self.last_saved_code = self.code_editor.toPlainText()
            self.is_dirty = False
            
            if not silent:
                self.status_bar.showMessage(f"Sparad till {file_path}", 3000)
            
            self.moduleUpdated.emit(self.module_id, "file_path", self.module_data)
            return True
        except Exception as e:
            if not silent:
                QMessageBox.critical(self, "Fel vid sparande", str(e))
            return False

    def on_content_changed(self):
        """Anropas när textinnehållet i editorn ändras"""
        self.is_dirty = True
        self.moduleUpdated.emit(self.module_id, "content", self.module_data)

    def auto_save_if_needed(self):
        """Spara automatiskt om det finns osparade ändringar"""
        if self.auto_save and self.is_dirty:
            current_code = self.code_editor.toPlainText()
            if current_code != self.last_saved_code:
                self.module_data["code"] = current_code
                self.module_data["modified"] = datetime.now().isoformat()
                self.save_module(silent=True)


    def import_from_file(self):
        """Importera kod från en extern fil"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Källkodsfiler (*.py *.js *.html *.css *.cpp *.h);;Alla filer (*)")
        
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                # Uppdatera modulens egenskaper baserat på den importerade filen
                imported_file = Path(file_path)
                
                # Fråga användaren om modulnamnet ska uppdateras
                reply = QMessageBox.question(
                    self, "Uppdatera modulnamn?", 
                    f"Vill du uppdatera modulnamnet till '{imported_file.stem}'?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.module_data["name"] = imported_file.stem
                    self.name_label.setText(imported_file.stem)
                
                # Uppdatera filändelsen
                self.module_data["extension"] = imported_file.suffix
                self.extension_input.setText(imported_file.suffix)
                
                # Uppdatera koden
                self.code_editor.setPlainText(code)
                self.module_data["code"] = code
                
                # Uppdatera filsökvägen
                self.module_data["file_path"] = str(file_path)
                self.file_path_label.setText(str(file_path))
                
                # Uppdatera tidsstämplar
                self.module_data["modified"] = datetime.now().isoformat()
                self.modified_label.setText(datetime.now().strftime("%Y-%m-%d %H:%M"))
                
                # Uppdatera syntax highlighter
                self.update_syntax_highlighter()
                
                # Uppdatera strukturen
                self.update_code_structure_cache()
                self.update_structure_tree()
                
                # Uppdatera status
                self.status_bar.showMessage(f"Importerad från {file_path}", 3000)
                
                # Signalera att modulen har uppdaterats
                self.moduleUpdated.emit(self.module_id, "import", self.module_data)
                
                # Uppdatera sparstatus
                self.last_saved_code = code
                self.is_dirty = False
                
                return True
            except Exception as e:
                QMessageBox.critical(self, "Fel vid import", str(e))
                return False
        
        return False


    def export_to_file(self):
        """Exportera modul till en annan fil"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportera modul", 
            str(self.modules_directory / f"{self.module_data['name']}{self.module_data['extension']}"),
            f"Källkodsfiler (*{self.module_data['extension']});;Alla filer (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.code_editor.toPlainText())
                
                self.status_bar.showMessage(f"Exporterad till {file_path}", 3000)
                return True
            except Exception as e:
                QMessageBox.critical(self, "Fel vid export", str(e))
                return False
        
        return False


    def edit_tags_dialog(self):
        """Visa en dialog för att redigera taggar"""
        current_tags = ", ".join(self.module_data.get("tags", []))
        new_tags, ok = QInputDialog.getText(
            self, "Redigera taggar", "Ange taggar separerade med kommatecken:", 
            QLineEdit.Normal, current_tags
        )
        
        if ok:
            self.tags_edit.setText(new_tags)
            self._update_tags_from_text(new_tags)


    def edit_tags_dialog(self):
        """Visa en dialog för att redigera taggar"""
        current_tags = ", ".join(self.module_data.get("tags", []))
        new_tags, ok = QInputDialog.getText(
            self, "Redigera taggar", "Ange taggar separerade med kommatecken:", 
            QLineEdit.Normal, current_tags
        )
        
        if ok:
            self.tags_edit.setText(new_tags)
            self._update_tags_from_text(new_tags)















    def refresh_from_data(self):
        """Uppdatera UI-element från moduldata"""
        # Uppdatera namn och filändelse
        self.name_label.setText(self.module_data["name"])
        self.extension_input.setText(self.module_data["extension"])
        
        # Uppdatera kod
        if "code" in self.module_data:
            self.code_editor.setPlainText(self.module_data["code"])
            self.last_saved_code = self.module_data["code"]
        
        # Uppdatera syntax highlighter baserat på filändelse
        self.update_syntax_highlighter()
        
        # Uppdatera metadata
        self.description_edit.setText(self.module_data.get("description", ""))
        
        current_category = self.module_data.get("category", "other")
        index = self.category_combo.findText(current_category)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        
        self.tags_edit.setText(", ".join(self.module_data.get("tags", [])))
        self.file_path_label.setText(str(self.module_data.get("file_path", "Ingen fil sparad")))
        
        # Uppdatera struktur-trädet
        self.update_structure_tree()
        
        # Uppdatera LLM-målkombo
        self.update_llm_target_combo()
    
    def update_syntax_highlighter(self):
        """Uppdatera syntaxmarkeringen baserat på filändelse"""
        extension = self.extension_input.text().lower()
        
        if hasattr(self, 'highlighter'):
            # Ta bort tidigare syntaxmarkerare
            self.highlighter.setDocument(None)
        
        if extension.endswith('.py'):
            self.highlighter = PythonSyntaxHighlighter(self.code_editor.document())
        elif extension.endswith('.js'):
            self.highlighter = JavaScriptSyntaxHighlighter(self.code_editor.document())
        else:
            # Använd Python-syntax som standard
            self.highlighter = PythonSyntaxHighlighter(self.code_editor.document())
    
    def update_structure_tree(self):
        """Uppdatera struktur-trädet med funktioner, klasser och variabler"""
        self.structure_tree.clear()
        
        # Skapa översta nivåelement
        functions_item = QTreeWidgetItem(self.structure_tree, ["Funktioner", "", ""])
        functions_item.setExpanded(True)
        
        classes_item = QTreeWidgetItem(self.structure_tree, ["Klasser", "", ""])
        classes_item.setExpanded(True)
        
        variables_item = QTreeWidgetItem(self.structure_tree, ["Variabler", "", ""])
        variables_item.setExpanded(True)
        
        # Uppdatera kodstrukturcachen och populera trädet
        self.update_code_structure_cache()
        
        # Lägg till funktioner
        for func_name, func_info in self.function_cache.items():
            func_item = QTreeWidgetItem(functions_item, [
                func_name, 
                "Funktion", 
                str(func_info.get("lineno", ""))
            ])
            
            # Lägg till parametrar som underträd
            if "params" in func_info:
                for param in func_info["params"]:
                    param_item = QTreeWidgetItem(func_item, [
                        param, 
                        "Parameter", 
                        ""
                    ])
        
        # Lägg till klasser
        for class_name, class_info in self.class_cache.items():
            class_item = QTreeWidgetItem(classes_item, [
                class_name, 
                "Klass", 
                str(class_info.get("lineno", ""))
            ])
            
            # Lägg till metoder som underträd
            if "methods" in class_info:
                for method_name, method_info in class_info["methods"].items():
                    method_item = QTreeWidgetItem(class_item, [
                        method_name, 
                        "Metod", 
                        str(method_info.get("lineno", ""))
                    ])
                    
                    # Lägg till parametrar
                    if "params" in method_info:
                        for param in method_info["params"]:
                            param_item = QTreeWidgetItem(method_item, [
                                param, 
                                "Parameter", 
                                ""
                            ])
            
            # Lägg till egenskaper
            if "properties" in class_info:
                for prop_name, prop_info in class_info["properties"].items():
                    prop_item = QTreeWidgetItem(class_item, [
                        prop_name, 
                        "Egenskap", 
                        str(prop_info.get("lineno", ""))
                    ])
        
        # Lägg till globala variabler
        for var_name, var_info in self.variable_cache.items():
            var_item = QTreeWidgetItem(variables_item, [
                var_name, 
                "Variabel", 
                str(var_info.get("lineno", ""))
            ])
    
    def update_llm_target_combo(self):
        """Uppdatera målkombofältet för LLM-integration med tillgängliga funktioner/klasser"""
        self.llm_target_combo.clear()
        
        # Lägg till funktioner
        for func_name in self.function_cache.keys():
            self.llm_target_combo.addItem(f"funktion:{func_name}")
        
        # Lägg till klasser
        for class_name in self.class_cache.keys():
            self.llm_target_combo.addItem(f"klass:{class_name}")
            
            # Lägg också till klassmetoder
            if "methods" in self.class_cache[class_name]:
                for method_name in self.class_cache[class_name]["methods"].keys():
                    self.llm_target_combo.addItem(f"metod:{class_name}.{method_name}")
        
        # Lägg till globala variabler
        for var_name in self.variable_cache.keys():
            self.llm_target_combo.addItem(f"variabel:{var_name}")
    
    def update_code_structure_cache(self):
        """Analysera koden och uppdatera cache för funktioner, klasser och variabler"""
        code = self.code_editor.toPlainText()
        extension = self.extension_input.text().lower()
        
        # Rensa cacheerna
        self.function_cache = {}
        self.class_cache = {}
        self.variable_cache = {}
        
        if extension.endswith('.py'):
            self.parse_python_structure(code)
        elif extension.endswith('.js'):
            self.parse_javascript_structure(code)
    
    def parse_python_structure(self, code):
        """Parsea Pythonstruktur från kod"""
        try:
            import ast
            tree = ast.parse(code)
            
            # Extrahera funktioner
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    params = []
                    for arg in node.args.args:
                        if hasattr(arg, 'annotation') and arg.annotation:
                            # Om det finns typannotering
                            if isinstance(arg.annotation, ast.Name):
                                params.append(f"{arg.arg}: {arg.annotation.id}")
                            else:
                                params.append(arg.arg)
                        else:
                            params.append(arg.arg)
                    
                    # Funktion direkt i modulscope är en global funktion
                    self.function_cache[node.name] = {
                        "lineno": node.lineno,
                        "params": params,
                        "ast_node": node
                    }
                
                elif isinstance(node, ast.ClassDef):
                    # Extrahera klassdetaljer
                    class_info = {
                        "lineno": node.lineno,
                        "bases": [base.id for base in node.bases if isinstance(base, ast.Name)],
                        "methods": {},
                        "properties": {},
                        "ast_node": node
                    }
                    
                    # Hitta metoder och klassvariabler
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            # Extrahera metod med parametrar
                            params = []
                            
                            # Hoppa över 'self' i parameterlistan
                            skip_first = False
                            if item.args.args and item.args.args[0].arg == 'self':
                                skip_first = True
                            
                            for i, arg in enumerate(item.args.args):
                                if skip_first and i == 0:
                                    continue
                                    
                                if hasattr(arg, 'annotation') and arg.annotation:
                                    if isinstance(arg.annotation, ast.Name):
                                        params.append(f"{arg.arg}: {arg.annotation.id}")
                                    else:
                                        params.append(arg.arg)
                                else:
                                    params.append(arg.arg)
                            
                            class_info["methods"][item.name] = {
                                "lineno": item.lineno,
                                "params": params,
                                "ast_node": item
                            }
                        
                        elif isinstance(item, ast.Assign):
                            # Hitta klassattribut
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    class_info["properties"][target.id] = {
                                        "lineno": item.lineno,
                                        "ast_node": item
                                    }
                    
                    self.class_cache[node.name] = class_info
                
                elif isinstance(node, ast.Assign) and all(isinstance(target, ast.Name) for target in node.targets):
                    # Globala variabler
                    for target in node.targets:
                        self.variable_cache[target.id] = {
                            "lineno": node.lineno,
                            "ast_node": node
                        }
        
        except SyntaxError:
            # Ignorera syntaxfel under parsning
            pass

    # ===== SLUT PÅ parse_python_structure ====

    # ===== BÖRJAN PÅ add_new_function =====
    def add_new_function(self, function_name):
        """Lägg till en ny funktion i modulen"""
        # Fråga efter parametrar
        params, ok = QInputDialog.getText(
            self, "Funktionsparametrar", 
            "Ange parameternamn separerade med kommatecken:",
            QLineEdit.Normal, ""
        )
        
        if ok:
            param_list = [p.strip() for p in params.split(',') if p.strip()]
            
            # Välj funktion eller metod
            items = ["Global funktion", "Klassmetod"]
            item, ok = QInputDialog.getItem(
                self, "Funktionstyp", 
                "Välj typ av funktion:",
                items, 0, False
            )
            
            if ok:
                if item == "Global funktion":
                    # Lägg till en global funktion
                    if self.module_data["extension"].lower().endswith('.py'):
                        function_template = self.generate_python_function(function_name, param_list)
                    elif self.module_data["extension"].lower().endswith('.js'):
                        function_template = self.generate_javascript_function(function_name, param_list)
                    else:
                        function_template = self.generate_python_function(function_name, param_list)
                    
                    # Lägg till i slutet av filen
                    cursor = self.code_editor.textCursor()
                    cursor.movePosition(cursor.End)
                    
                    # Lägg till två tomma rader före om det inte är tomt
                    if not self.code_editor.toPlainText().strip():
                        cursor.insertText(function_template)
                    else:
                        cursor.insertText("\n\n" + function_template)
                    
                    self.status_bar.showMessage(f"Funktion '{function_name}' tillagd", 3000)
                
                elif item == "Klassmetod":
                    # Välj vilken klass metoden ska tillhöra
                    class_names = list(self.class_cache.keys())
                    if class_names:
                        class_name, ok = QInputDialog.getItem(
                            self, "Välj klass", 
                            "Välj klass för metoden:",
                            class_names, 0, False
                        )
                        
                        if ok:
                            # Lägg till en klassmetod
                            if self.module_data["extension"].lower().endswith('.py'):
                                method_template = self.generate_python_method(function_name, param_list)
                            elif self.module_data["extension"].lower().endswith('.js'):
                                method_template = self.generate_javascript_method(function_name, param_list)
                            else:
                                method_template = self.generate_python_method(function_name, param_list)
                            
                            # Hitta slutet av klassen
                            if class_name in self.class_cache:
                                class_info = self.class_cache[class_name]
                                if hasattr(class_info, 'ast_node') and hasattr(class_info.ast_node, 'end_lineno'):
                                    end_line = class_info.ast_node.end_lineno
                                else:
                                    # Hitta klassdefinitionen manuellt
                                    code = self.code_editor.toPlainText()
                                    lines = code.split('\n')
                                    class_line = class_info.get("lineno", 1) - 1
                                    
                                    # Hitta slutet av klassen genom att räkna indrag
                                    class_indent = len(lines[class_line]) - len(lines[class_line].lstrip())
                                    end_line = class_line
                                    
                                    for i in range(class_line + 1, len(lines)):
                                        line = lines[i]
                                        if line.strip() and len(line) - len(line.lstrip()) <= class_indent:
                                            # Hittade en rad med samma eller mindre indrag
                                            end_line = i - 1
                                            break
                                        end_line = i
                                
                                # Indentera metoden korrekt
                                if self.module_data["extension"].lower().endswith('.py'):
                                    # Python använder 4 mellanslag för indentering
                                    indented_method = "\n".join("    " + line for line in method_template.split('\n'))
                                else:
                                    # JavaScript använder två mellanslag
                                    indented_method = "\n".join("  " + line for line in method_template.split('\n'))
                                
                                # Infoga metoden på rätt plats
                                cursor = self.code_editor.textCursor()
                                block = self.code_editor.document().findBlockByLineNumber(end_line)
                                cursor.setPosition(block.position() + block.length() - 1)
                                cursor.insertText("\n" + indented_method)
                                
                                self.status_bar.showMessage(f"Metod '{function_name}' tillagd till klass '{class_name}'", 3000)
                            else:
                                QMessageBox.warning(self, "Klass saknas", f"Kunde inte hitta klassen '{class_name}'")
                    else:
                        QMessageBox.warning(self, "Inga klasser", "Det finns inga klasser i modulen att lägga till metoden i.")
            
            # Uppdatera strukturträdet
            self.update_code_structure_cache()
            self.update_structure_tree()
    
    def generate_python_function(self, name, params):
        """Generera en Python-funktionsmall"""
        params_str = ", ".join(params)
        template = f"def {name}({params_str}):\n"
        template += f"    \"\"\"\n"
        template += f"    {name} - Beskrivning av funktionen\n"
        
        if params:
            template += f"\n"
            template += f"    Args:\n"
            for param in params:
                template += f"        {param}: Beskrivning av parametern\n"
        
        template += f"\n"
        template += f"    Returns:\n"
        template += f"        Beskrivning av returvärdet\n"
        template += f"    \"\"\"\n"
        template += f"    # Implementering av funktionen\n"
        template += f"    pass\n"
        
        return template
    
    def generate_python_method(self, name, params):
        """Generera en Python-metodmall"""
        # Lägg till 'self' som första parameter
        params_with_self = ["self"] + params
        params_str = ", ".join(params_with_self)
        
        template = f"def {name}({params_str}):\n"
        template += f"    \"\"\"\n"
        template += f"    {name} - Beskrivning av metoden\n"
        
        if params:
            template += f"\n"
            template += f"    Args:\n"
            for param in params:
                template += f"        {param}: Beskrivning av parametern\n"
        
        template += f"\n"
        template += f"    Returns:\n"
        template += f"        Beskrivning av returvärdet\n"
        template += f"    \"\"\"\n"
        template += f"    # Implementering av metoden\n"
        template += f"    pass\n"
        
        return template
    
    def generate_javascript_function(self, name, params):
        """Generera en JavaScript-funktionsmall"""
        params_str = params if params else []
        params_str = ", ".join(params_str)
        
        template = f"/**\n"
        template += f" * {name} - Beskrivning av funktionen\n"
        
        if params:
            for param in params:
                template += f" * @param {{{param.split(':')[0] if ':' in param else 'any'}}} {param.split(':')[0]} - Beskrivning av parametern\n"
        
        template += f" * @returns {{any}} Beskrivning av returvärdet\n"
        template += f" */\n"
        template += f"function {name}({params_str}) {{\n"
        template += f"  // Implementering av funktionen\n"
        template += f"  return null;\n"
        template += f"}}\n"
        
        return template
    
    def generate_javascript_method(self, name, params):
        """Generera en JavaScript-metodmall"""
        params_str = params if params else []
        params_str = ", ".join(params_str)
        
        template = f"/**\n"
        template += f" * {name} - Beskrivning av metoden\n"
        
        if params:
            for param in params:
                template += f" * @param {{{param.split(':')[0] if ':' in param else 'any'}}} {param.split(':')[0]} - Beskrivning av parametern\n"
        
        template += f" * @returns {{any}} Beskrivning av returvärdet\n"
        template += f" */\n"
        template += f"{name}({params_str}) {{\n"
        template += f"  // Implementering av metoden\n"
        template += f"  return null;\n"
        template += f"}}\n"
        
        return template
    
    def apply_llm_changes(self):
        """Tillämpa ändringar från LLM-integrationsfliken"""
        action = self.llm_action_combo.currentText()
        target = self.llm_target_combo.currentText()
        code = self.llm_code_edit.toPlainText().strip()
        
        if not code:
            QMessageBox.warning(self, "Tomma ändringar", "Ingen kod har angetts.")
            return
        
        try:
            if action == "Lägg till funktion/klass":
                self.llm_add_function_or_class(code)
            elif action == "Uppdatera funktion/klass":
                if not target:
                    QMessageBox.warning(self, "Inget mål", "Ange namnet på funktionen/klassen som ska uppdateras.")
                    return
                self.llm_update_function_or_class(target, code)
            elif action == "Ändra variabel":
                if not target:
                    QMessageBox.warning(self, "Inget mål", "Ange namnet på variabeln som ska ändras.")
                    return
                self.llm_update_variable(target, code)
            elif action == "Erbjud strukturförslag":
                self.llm_suggest_structure(code)
        except Exception as e:
            QMessageBox.critical(self, "Fel vid LLM-operation", str(e))
            self.llm_result_edit.setPlainText(f"Fel: {str(e)}")
    
    def llm_add_function_or_class(self, code):
        """Lägg till en funktion eller klass från LLM-input"""
        # Identifiera om det är en funktion eller klass genom att analysera koden
        is_function = False
        is_class = False
        
        if self.module_data["extension"].lower().endswith('.py'):
            if code.strip().startswith("def "):
                is_function = True
            elif code.strip().startswith("class "):
                is_class = True
        elif self.module_data["extension"].lower().endswith('.js'):
            if code.strip().startswith("function ") or "=> {" in code:
                is_function = True
            elif code.strip().startswith("class "):
                is_class = True
        
        # Validera och formatera koden
        formatted_code = self.format_code(code)
        
        # Lägg till i slutet av filen
        current_code = self.code_editor.toPlainText()
        
        if current_code.strip():
            # Det finns redan kod, lägg till två tomma rader
            new_code = current_code + "\n\n" + formatted_code
        else:
            # Filen är tom
            new_code = formatted_code
        
        # Uppdatera koden
        self.code_editor.setPlainText(new_code)
        
        # Uppdatera strukturen
        self.update_code_structure_cache()
        self.update_structure_tree()
        
        # Visa resultat
        if is_function:
            entity_type = "funktion"
        elif is_class:
            entity_type = "klass"
        else:
            entity_type = "kod"
        
        self.llm_result_edit.setPlainText(f"Lade till {entity_type} i slutet av filen.\n\nResultat:\n{formatted_code}")
    
    def llm_update_function_or_class(self, target, code):
        """Uppdatera en befintlig funktion eller klass"""
        # Parsa målsträngen
        target_parts = target.split(':', 1)
        target_type = target_parts[0] if len(target_parts) > 1 else "funktion"
        target_name = target_parts[1] if len(target_parts) > 1 else target
        
        # För klassmetoder måste vi hantera format "klass.metod"
        if '.' in target_name and target_type == "metod":
            class_name, method_name = target_name.split('.', 1)
        else:
            class_name = None
            method_name = None
        
        # Hitta koden för målentiteten
        current_code = self.code_editor.toPlainText()
        
        # Validera och formatera koden
        formatted_code = self.format_code(code)
        
        # Olika hantering beroende på måltyp och filändelse
        if self.module_data["extension"].lower().endswith('.py'):
            # Python-hantering
            if target_type == "funktion" or (target_type == "metod" and not class_name):
                # Hitta funktionen i cachen
                if target_name in self.function_cache:
                    func_info = self.function_cache[target_name]
                    if hasattr(func_info, 'ast_node'):
                        # Hitta funktionens kodsegment
                        start_line = func_info.ast_node.lineno - 1
                        end_line = func_info.ast_node.end_lineno if hasattr(func_info.ast_node, 'end_lineno') else start_line
                        
                        # Dela koden i rader
                        lines = current_code.split('\n')
                        
                        # Ersätt funktionen
                        new_lines = lines[:start_line] + formatted_code.split('\n') + lines[end_line:]
                        new_code = '\n'.join(new_lines)
                        
                        # Uppdatera koden
                        self.code_editor.setPlainText(new_code)
                        
                        # Visa resultat
                        self.llm_result_edit.setPlainText(f"Uppdaterade funktionen '{target_name}'.\n\nResultat:\n{formatted_code}")
                    else:
                        # Funktionen hittades inte i AST (ovanligt)
                        raise Exception(f"Kunde inte hitta funktionskroppen för '{target_name}'")
                else:
                    # Funktionen hittades inte, erbjud att lägga till den
                    reply = QMessageBox.question(
                        self, "Funktion saknas", 
                        f"Funktionen '{target_name}' hittades inte. Vill du lägga till den?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    
                    if reply == QMessageBox.Yes:
                        self.llm_add_function_or_class(formatted_code)
                    else:
                        self.llm_result_edit.setPlainText(f"Operationen avbröts: Funktionen '{target_name}' hittades inte.")
            
            elif target_type == "klass":
                # Hitta klassen i cachen
                if target_name in self.class_cache:
                    class_info = self.class_cache[target_name]
                    if hasattr(class_info, 'ast_node'):
                        # Hitta klassens kodsegment
                        start_line = class_info.ast_node.lineno - 1
                        end_line = class_info.ast_node.end_lineno if hasattr(class_info.ast_node, 'end_lineno') else start_line
                        
                        # Dela koden i rader
                        lines = current_code.split('\n')
                        
                        # Ersätt klassen
                        new_lines = lines[:start_line] + formatted_code.split('\n') + lines[end_line:]
                        new_code = '\n'.join(new_lines)
                        
                        # Uppdatera koden
                        self.code_editor.setPlainText(new_code)
                        
                        # Visa resultat
                        self.llm_result_edit.setPlainText(f"Uppdaterade klassen '{target_name}'.\n\nResultat:\n{formatted_code}")
                    else:
                        # Klassen hittades inte i AST (ovanligt)
                        raise Exception(f"Kunde inte hitta klasskroppen för '{target_name}'")
                else:
                    # Klassen hittades inte, erbjud att lägga till den
                    reply = QMessageBox.question(
                        self, "Klass saknas", 
                        f"Klassen '{target_name}' hittades inte. Vill du lägga till den?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    
                    if reply == QMessageBox.Yes:
                        self.llm_add_function_or_class(formatted_code)
                    else:
                        self.llm_result_edit.setPlainText(f"Operationen avbröts: Klassen '{target_name}' hittades inte.")
            
            elif target_type == "metod" and class_name:
                # Hitta klassen i cachen
                if class_name in self.class_cache:
                    class_info = self.class_cache[class_name]
                    
                    # Kontrollera om metoden finns
                    if method_name in class_info.get("methods", {}):
                        method_info = class_info["methods"][method_name]
                        
                        if hasattr(method_info, 'ast_node'):
                            # Hitta metodens kodsegment
                            start_line = method_info.ast_node.lineno - 1
                            end_line = method_info.ast_node.end_lineno if hasattr(method_info.ast_node, 'end_lineno') else start_line
                            
                            # Dela koden i rader
                            lines = current_code.split('\n')
                            
                            # Kontrollera indentering för metoden
                            indent = len(lines[start_line]) - len(lines[start_line].lstrip())
                            
                            # Indentera den nya koden korrekt
                            formatted_lines = formatted_code.split('\n')
                            indented_lines = []
                            
                            for i, line in enumerate(formatted_lines):
                                if i == 0:
                                    # Första raden behöver inte indentering om det är en metoddeklaration
                                    if line.strip().startswith("def "):
                                        indented_lines.append(" " * indent + line.strip())
                                    else:
                                        indented_lines.append(" " * indent + line)
                                else:
                                    # Andra rader behöver mer indentering
                                    indented_lines.append(" " * indent + line)
                            
                            # Ersätt metoden
                            new_lines = lines[:start_line] + indented_lines + lines[end_line:]
                            new_code = '\n'.join(new_lines)
                            
                            # Uppdatera koden
                            self.code_editor.setPlainText(new_code)
                            
                            # Visa resultat
                            indented_code = '\n'.join(indented_lines)
                            self.llm_result_edit.setPlainText(f"Uppdaterade metoden '{class_name}.{method_name}'.\n\nResultat:\n{indented_code}")
                        else:
                            # Metoden hittades inte i AST (ovanligt)
                            raise Exception(f"Kunde inte hitta metodkroppen för '{class_name}.{method_name}'")
                    else:
                        # Metoden hittades inte, erbjud att lägga till den
                        reply = QMessageBox.question(
                            self, "Metod saknas", 
                            f"Metoden '{method_name}' i klassen '{class_name}' hittades inte. Vill du lägga till den?",
                            QMessageBox.Yes | QMessageBox.No
                        )
                        
                        if reply == QMessageBox.Yes:
                            # Lägg till metoden i klassen
                            if hasattr(class_info, 'ast_node'):
                                # Hitta klassens slut
                                class_end_line = class_info.ast_node.end_lineno if hasattr(class_info.ast_node, 'end_lineno') else -1
                                
                                if class_end_line > 0:
                                    # Dela koden i rader
                                    lines = current_code.split('\n')
                                    
                                    # Kontrollera indentering för klassen
                                    class_start_line = class_info.ast_node.lineno - 1
                                    indent = len(lines[class_start_line + 1]) - len(lines[class_start_line + 1].lstrip())
                                    
                                    # Indentera metoden korrekt
                                    formatted_lines = formatted_code.split('\n')
                                    indented_method = []
                                    for line in formatted_lines:
                                        indented_method.append(" " * indent + line)
                                    
                                    indented_code = '\n'.join(indented_method)
                                    
                                    # Lägg till metoden
                                    new_lines = lines[:class_end_line] + [indented_code] + lines[class_end_line:]
                                    new_code = '\n'.join(new_lines)
                                    
                                    # Uppdatera koden
                                    self.code_editor.setPlainText(new_code)
                                    
                                    # Visa resultat
                                    self.llm_result_edit.setPlainText(f"Lade till metoden '{method_name}' i klassen '{class_name}'.\n\nResultat:\n{indented_code}")
                                else:
                                    raise Exception(f"Kunde inte hitta slutet på klassen '{class_name}'")
                            else:
                                raise Exception(f"Kunde inte hitta klassen '{class_name}' i AST")
                        else:
                            self.llm_result_edit.setPlainText(f"Operationen avbröts: Metoden '{method_name}' i klassen '{class_name}' hittades inte.")
                else:
                    # Klassen hittades inte
                    raise Exception(f"Klassen '{class_name}' hittades inte.")
        
        elif self.module_data["extension"].lower().endswith('.js'):
            # JavaScript-hantering - simplare eftersom vi använder regex
            if target_type == "funktion":
                # Leta efter funktionsdefinitionen med regex
                patterns = [
                    rf'function\s+{re.escape(target_name)}\s*\([^)]*\)\s*\{{[\s\S]*?\}}',  # Traditionell funktion
                    rf'(?:const|let|var)\s+{re.escape(target_name)}\s*=\s*(?:\([^)]*\)|[a-zA-Z_$][a-zA-Z0-9_$]*)\s*=>\s*\{{[\s\S]*?\}}',  # Arrow function
                    rf'(?:const|let|var)\s+{re.escape(target_name)}\s*=\s*function\s*\([^)]*\)\s*\{{[\s\S]*?\}}'  # Function expression
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, current_code)
                    if match:
                        # Hittade funktionen
                        new_code = current_code[:match.start()] + formatted_code + current_code[match.end():]
                        
                        # Uppdatera koden
                        self.code_editor.setPlainText(new_code)
                        
                        # Visa resultat
                        self.llm_result_edit.setPlainText(f"Uppdaterade funktionen '{target_name}'.\n\nResultat:\n{formatted_code}")
                        break
                else:
                    # Funktionen hittades inte, erbjud att lägga till den
                    reply = QMessageBox.question(
                        self, "Funktion saknas", 
                        f"Funktionen '{target_name}' hittades inte. Vill du lägga till den?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    
                    if reply == QMessageBox.Yes:
                        self.llm_add_function_or_class(formatted_code)
                    else:
                        self.llm_result_edit.setPlainText(f"Operationen avbröts: Funktionen '{target_name}' hittades inte.")
            
            elif target_type == "klass":
                # Leta efter klassdeklarationen med regex
                pattern = rf'class\s+{re.escape(target_name)}\s*(?:extends\s+[a-zA-Z_$][a-zA-Z0-9_$]*)?\s*\{{[\s\S]*?\}}'
                match = re.search(pattern, current_code)
                
                if match:
                    # Hittade klassen
                    new_code = current_code[:match.start()] + formatted_code + current_code[match.end():]
                    
                    # Uppdatera koden
                    self.code_editor.setPlainText(new_code)
                    
                    # Visa resultat
                    self.llm_result_edit.setPlainText(f"Uppdaterade klassen '{target_name}'.\n\nResultat:\n{formatted_code}")
                else:
                    # Klassen hittades inte, erbjud att lägga till den
                    reply = QMessageBox.question(
                        self, "Klass saknas", 
                        f"Klassen '{target_name}' hittades inte. Vill du lägga till den?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    
                    if reply == QMessageBox.Yes:
                        self.llm_add_function_or_class(formatted_code)
                    else:
                        self.llm_result_edit.setPlainText(f"Operationen avbröts: Klassen '{target_name}' hittades inte.")
        
        # Uppdatera strukturen
        self.update_code_structure_cache()
        self.update_structure_tree()
    
    def llm_update_variable(self, target, code):
        """Uppdatera en variabel med nytt värde"""
        # Parsa målsträngen
        target_parts = target.split(':', 1)
        target_type = target_parts[0] if len(target_parts) > 1 else "variabel"
        target_name = target_parts[1] if len(target_parts) > 1 else target
        
        # För klassproperties måste vi hantera format "klass.property"
        if '.' in target_name:
            class_name, property_name = target_name.split('.', 1)
        else:
            class_name = None
            property_name = None
        
        # Hitta variabeln och uppdatera den
        current_code = self.code_editor.toPlainText()
        
        # Validera och formatera koden (kan vara bara värdet eller hela deklarationen)
        formatted_code = code.strip()
        
        if self.module_data["extension"].lower().endswith('.py'):
            # Python-hantering
            if target_type == "variabel" and not class_name:
                # Leta efter global variabel
                if target_name in self.variable_cache:
                    var_info = self.variable_cache[target_name]
                    
                    # Hittar vi variabeln via AST eller behöver vi använda regex?
                    if hasattr(var_info, 'ast_node'):
                        # Via AST
                        start_line = var_info.ast_node.lineno - 1
                        
                        # Dela koden i rader
                        lines = current_code.split('\n')
                        
                        # Hantera beroende på om ny kod är hela deklarationen eller bara värdet
                        if formatted_code.startswith(f"{target_name} = "):
                            # Hela deklarationen
                            lines[start_line] = formatted_code
                        else:
                            # Bara värdet
                            # Hitta positionen för "="
                            pos = lines[start_line].find('=')
                            if pos >= 0:
                                lines[start_line] = lines[start_line][:pos+1] + " " + formatted_code
                            else:
                                lines[start_line] = f"{target_name} = {formatted_code}"
                        
                        new_code = '\n'.join(lines)
                        
                        # Uppdatera koden
                        self.code_editor.setPlainText(new_code)
                        
                        # Visa resultat
                        self.llm_result_edit.setPlainText(f"Uppdaterade variabeln '{target_name}'.")
                    else:
                        # Via regex
                        pattern = rf'{re.escape(target_name)}\s*=\s*[^;#\n]*'
                        match = re.search(pattern, current_code)
                        
                        if match:
                            if formatted_code.startswith(f"{target_name} = "):
                                # Hela deklarationen
                                replacement = formatted_code
                            else:
                                # Bara värdet
                                replacement = f"{target_name} = {formatted_code}"
                            
                            new_code = current_code[:match.start()] + replacement + current_code[match.end():]
                            
                            # Uppdatera koden
                            self.code_editor.setPlainText(new_code)
                            
                            # Visa resultat
                            self.llm_result_edit.setPlainText(f"Uppdaterade variabeln '{target_name}'.")
                        else:
                            # Variabeln hittades inte, erbjud att lägga till den
                            reply = QMessageBox.question(
                                self, "Variabel saknas", 
                                f"Variabeln '{target_name}' hittades inte. Vill du lägga till den?",
                                QMessageBox.Yes | QMessageBox.No
                            )
                            
                            if reply == QMessageBox.Yes:
                                # Lägg till i början av filen
                                if formatted_code.startswith(f"{target_name} = "):
                                    new_var = formatted_code
                                else:
                                    new_var = f"{target_name} = {formatted_code}"
                                
                                new_code = new_var + "\n\n" + current_code
                                
                                # Uppdatera koden
                                
## =======    PART - 4    ======= ##
                                self.code_editor.setPlainText(new_code)
                                
                                # Visa resultat
                                self.llm_result_edit.setPlainText(f"Lade till variabeln '{target_name}'.")
                            else:
                                self.llm_result_edit.setPlainText(f"Operationen avbröts: Variabeln '{target_name}' hittades inte.")
                else:
                    # Variabeln hittades inte, erbjud att lägga till den
                    reply = QMessageBox.question(
                        self, "Variabel saknas", 
                        f"Variabeln '{target_name}' hittades inte. Vill du lägga till den?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    
                    if reply == QMessageBox.Yes:
                        # Lägg till i början av filen
                        if formatted_code.startswith(f"{target_name} = "):
                            new_var = formatted_code
                        else:
                            new_var = f"{target_name} = {formatted_code}"
                        
                        new_code = new_var + "\n\n" + current_code
                        
                        # Uppdatera koden
                        self.code_editor.setPlainText(new_code)
                        
                        # Visa resultat
                        self.llm_result_edit.setPlainText(f"Lade till variabeln '{target_name}'.")
                    else:
                        self.llm_result_edit.setPlainText(f"Operationen avbröts: Variabeln '{target_name}' hittades inte.")
            
            elif target_type == "variabel" and class_name:
                # Klassvariabel/property
                if class_name in self.class_cache:
                    class_info = self.class_cache[class_name]
                    
                    # Kolla om egenskapen finns
                    if property_name in class_info.get("properties", {}):
                        property_info = class_info["properties"][property_name]
                        
                        if hasattr(property_info, 'ast_node'):
                            # Via AST
                            start_line = property_info.ast_node.lineno - 1
                            
                            # Dela koden i rader
                            lines = current_code.split('\n')
                            
                            # Hantera indentering
                            indent = len(lines[start_line]) - len(lines[start_line].lstrip())
                            
                            if formatted_code.strip().startswith("self." + property_name):
                                # Hela deklarationen
                                lines[start_line] = " " * indent + formatted_code.strip()
                            else:
                                # Bara värdet
                                pos = lines[start_line].find('=')
                                if pos >= 0:
                                    lines[start_line] = lines[start_line][:pos+1] + " " + formatted_code.strip()
                                else:
                                    lines[start_line] = " " * indent + f"self.{property_name} = {formatted_code.strip()}"
                            
                            new_code = '\n'.join(lines)
                            
                            # Uppdatera koden
                            self.code_editor.setPlainText(new_code)
                            
                            # Visa resultat
                            self.llm_result_edit.setPlainText(f"Uppdaterade egenskapen '{class_name}.{property_name}'.")
                        else:
                            # Via regex
                            pattern = rf'self\.{re.escape(property_name)}\s*=\s*[^;#\n]*'
                            match = re.search(pattern, current_code)
                            
                            if match:
                                # Hitta indentering
                                line_start = current_code.rfind('\n', 0, match.start()) + 1
                                if line_start > 0:
                                    indent = len(current_code[line_start:match.start()]) - len(current_code[line_start:match.start()].lstrip())
                                else:
                                    indent = 0
                                
                                if formatted_code.strip().startswith("self." + property_name):
                                    # Hela deklarationen
                                    replacement = " " * indent + formatted_code.strip()
                                else:
                                    # Bara värdet
                                    replacement = " " * indent + f"self.{property_name} = {formatted_code.strip()}"
                                
                                # Hitta radslut
                                line_end = current_code.find('\n', match.end())
                                if line_end < 0:
                                    line_end = len(current_code)
                                
                                new_code = current_code[:line_start] + replacement + current_code[line_end:]
                                
                                # Uppdatera koden
                                self.code_editor.setPlainText(new_code)
                                
                                # Visa resultat
                                self.llm_result_edit.setPlainText(f"Uppdaterade egenskapen '{class_name}.{property_name}'.")
                            else:
                                # Egenskapen hittades inte, erbjud att lägga till den i __init__
                                reply = QMessageBox.question(
                                    self, "Egenskap saknas", 
                                    f"Egenskapen '{property_name}' i klassen '{class_name}' hittades inte. Vill du lägga till den i __init__?",
                                    QMessageBox.Yes | QMessageBox.No
                                )
                                
                                if reply == QMessageBox.Yes:
                                    # Hitta __init__ i klassen
                                    if "methods" in class_info and "__init__" in class_info["methods"]:
                                        init_info = class_info["methods"]["__init__"]
                                        
                                        if hasattr(init_info, 'ast_node'):
                                            # Via AST
                                            init_start_line = init_info.ast_node.lineno - 1
                                            
                                            # Hitta första raden i funktionskroppen
                                            lines = current_code.split('\n')
                                            first_body_line = init_start_line + 1
                                            
                                            # Hitta indentering
                                            indent = len(lines[first_body_line]) - len(lines[first_body_line].lstrip())
                                            
                                            # Skapa ny property-rad
                                            if formatted_code.strip().startswith("self." + property_name):
                                                new_property = " " * indent + formatted_code.strip()
                                            else:
                                                new_property = " " * indent + f"self.{property_name} = {formatted_code.strip()}"
                                            
                                            # Lägg till efter första raden i init
                                            new_lines = lines[:first_body_line+1] + [new_property] + lines[first_body_line+1:]
                                            new_code = '\n'.join(new_lines)
                                            
                                            # Uppdatera koden
                                            self.code_editor.setPlainText(new_code)
                                            
                                            # Visa resultat
                                            self.llm_result_edit.setPlainText(f"Lade till egenskapen '{property_name}' i klassen '{class_name}'.")
                                        else:
                                            # Kunde inte hitta __init__-metoden ordentligt
                                            self.llm_result_edit.setPlainText(f"Kunde inte hitta __init__-metodens kropp i klassen '{class_name}'.")
                                    else:
                                        # Hitta slutet av klassen för att lägga till __init__
                                        if hasattr(class_info, 'ast_node'):
                                            # Via AST
                                            class_start_line = class_info.ast_node.lineno - 1
                                            
                                            # Dela koden i rader
                                            lines = current_code.split('\n')
                                            
                                            # Hitta indentering för första raden i klassen
                                            first_body_line = class_start_line + 1
                                            indent = len(lines[first_body_line]) - len(lines[first_body_line].lstrip())
                                            
                                            # Skapa ny __init__-metod med egenskapen
                                            new_init = [
                                                " " * indent + "def __init__(self):",
                                                " " * (indent + 4) + "super().__init__()",
                                                " " * (indent + 4) + f"self.{property_name} = {formatted_code.strip()}"
                                            ]
                                            
                                            # Lägg till efter klassdeklarationen
                                            new_lines = lines[:first_body_line] + new_init + lines[first_body_line:]
                                            new_code = '\n'.join(new_lines)
                                            
                                            # Uppdatera koden
                                            self.code_editor.setPlainText(new_code)
                                            
                                            # Visa resultat
                                            self.llm_result_edit.setPlainText(f"Lade till __init__-metod med egenskapen '{property_name}' i klassen '{class_name}'.")
                                        else:
                                            # Kunde inte hitta klassens struktur ordentligt
                                            self.llm_result_edit.setPlainText(f"Kunde inte hitta klassstrukturen för '{class_name}'.")
                                else:
                                    self.llm_result_edit.setPlainText(f"Operationen avbröts: Egenskapen '{property_name}' i klassen '{class_name}' hittades inte.")
                    else:
                        # Egenskapen hittades inte, erbjud att lägga till den i __init__
                        reply = QMessageBox.question(
                            self, "Egenskap saknas", 
                            f"Egenskapen '{property_name}' i klassen '{class_name}' hittades inte. Vill du lägga till den i __init__?",
                            QMessageBox.Yes | QMessageBox.No
                        )
                        
                        if reply == QMessageBox.Yes:
                            # Försök hitta __init__ och slutföra som ovan...
                            self.llm_result_edit.setPlainText(f"Funktionalitet ännu inte implementerad för att lägga till ny egenskap.")
                        else:
                            self.llm_result_edit.setPlainText(f"Operationen avbröts: Egenskapen '{property_name}' i klassen '{class_name}' hittades inte.")
                else:
                    # Klassen hittades inte
                    self.llm_result_edit.setPlainText(f"Klassen '{class_name}' hittades inte.")
        
        elif self.module_data["extension"].lower().endswith('.js'):
            # JavaScript-hantering
            if target_type == "variabel" and not class_name:
                # Leta efter global variabel
                patterns = [
                    rf'(?:const|let|var)\s+{re.escape(target_name)}\s*=\s*[^;]*;?',  # Full declaration
                    rf'{re.escape(target_name)}\s*=\s*[^;]*;?'  # Assignment
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, current_code)
                    if match:
                        if formatted_code.startswith(f"{target_name} = ") or formatted_code.startswith(f"var {target_name} = "):
                            # Hela deklarationen
                            replacement = formatted_code
                            if not replacement.endswith(';'):
                                replacement += ';'
                        else:
                            # Bara värdet
                            # Behåll variabeldeklarationen (const/let/var) från originalet
                            if re.match(rf'(?:const|let|var)\s+{re.escape(target_name)}', current_code[match.start():match.end()]):
                                decl = re.match(rf'((?:const|let|var)\s+{re.escape(target_name)})\s*=\s*', current_code[match.start():match.end()]).group(1)
                                replacement = f"{decl} = {formatted_code}"
                            else:
                                replacement = f"{target_name} = {formatted_code}"
                            
                            if not replacement.endswith(';'):
                                replacement += ';'
                        
                        new_code = current_code[:match.start()] + replacement + current_code[match.end():]
                        
                        # Uppdatera koden
                        self.code_editor.setPlainText(new_code)
                        
                        # Visa resultat
                        self.llm_result_edit.setPlainText(f"Uppdaterade variabeln '{target_name}'.")
                        break
                else:
                    # Variabeln hittades inte, erbjud att lägga till den
                    reply = QMessageBox.question(
                        self, "Variabel saknas", 
                        f"Variabeln '{target_name}' hittades inte. Vill du lägga till den?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    
                    if reply == QMessageBox.Yes:
                        # Lägg till i början av filen
                        if formatted_code.startswith(f"{target_name} = ") or formatted_code.startswith(f"var {target_name} = "):
                            new_var = formatted_code
                        else:
                            new_var = f"const {target_name} = {formatted_code}"
                        
                        if not new_var.endswith(';'):
                            new_var += ';'
                        
                        new_code = new_var + "\n\n" + current_code
                        
                        # Uppdatera koden
                        self.code_editor.setPlainText(new_code)
                        
                        # Visa resultat
                        self.llm_result_edit.setPlainText(f"Lade till variabeln '{target_name}'.")
                    else:
                        self.llm_result_edit.setPlainText(f"Operationen avbröts: Variabeln '{target_name}' hittades inte.")
        
        # Uppdatera strukturen
        self.update_code_structure_cache()
        self.update_structure_tree()
    
    def llm_suggest_structure(self, code):
        """Föreslå strukturella förbättringar baserat på den aktuella koden"""
        # Här skulle vi använda kod från LLM för att föreslå förbättringar i struktur
        # Eftersom vi inte kan anropa en faktisk LLM direkt, använder vi en enklare analys
        
        # Analysera existerande struktur
        current_code = self.code_editor.toPlainText()
        
        # Visa basic information istället för faktiska förslag
        result = "Struktur-analys:\n\n"
        
        # Räkna funktioner, klasser och variabler
        result += f"Funktioner: {len(self.function_cache)}\n"
        result += f"Klasser: {len(self.class_cache)}\n"
        result += f"Globala variabler: {len(self.variable_cache)}\n\n"
        
        # Visa LLM-förslag (som skulle komma från AI)
        result += "Kodförslag från LLM:\n\n"
        result += code
        
        # Visa resultat
        self.llm_result_edit.setPlainText(result)
        
        # Uppdatera strukturen
        self.update_code_structure_cache()
        self.update_structure_tree()
    
    def validate_llm_code(self):
        """Validera och formatera koden från LLM"""
        code = self.llm_code_edit.toPlainText().strip()
        if not code:
            QMessageBox.warning(self, "Tom kod", "Ingen kod att validera.")
            return
        
        # Försök formatera koden
        try:
            formatted_code = self.format_code(code)
            self.llm_code_edit.setPlainText(formatted_code)
            
            # Validera syntax
            if self.module_data["extension"].lower().endswith('.py'):
                # Python validering
                try:
                    import ast
                    ast.parse(formatted_code)
                    self.llm_result_edit.setPlainText("✅ Koden har korrekt Python-syntax.")
                except SyntaxError as e:
                    self.llm_result_edit.setPlainText(f"❌ Python syntaxfel:\n{str(e)}")
            
            elif self.module_data["extension"].lower().endswith('.js'):
                # JavaScript - enklare validering
                # Här skulle vi egentligen behöva använda en JS-parser som esprima
                # Vi gör en enkel kontroll av matchande paranteser och brackets
                counts = {'(': 0, ')': 0, '{': 0, '}': 0, '[': 0, ']': 0}
                for char in formatted_code:
                    if char in counts:
                        counts[char] += 1
                
                if counts['('] != counts[')'] or counts['{'] != counts['}'] or counts['['] != counts[']']:
                    self.llm_result_edit.setPlainText("❌ JavaScript-validering misslyckades: Omatchade paranteser eller brackets")
                else:
                    self.llm_result_edit.setPlainText("✅ Grundläggande JavaScript-validering OK (kontrollerar bara matchade paranteser)")
        
        except Exception as e:
            self.llm_result_edit.setPlainText(f"❌ Valideringsfel: {str(e)}")
    
    def format_code(self, code):
        """Formatera kod för korrekt indentering och stil"""
        extension = self.module_data["extension"].lower()
        
        if extension.endswith('.py'):
            return self.format_python_code(code)
        elif extension.endswith('.js'):
            return self.format_javascript_code(code)
        else:
            # Standardformateringen 
            return code
    
    def format_python_code(self, code):
        """Formatera Python-kod"""
        try:
            # Försök förbättra indentering
            lines = code.split('\n')
            formatted_lines = []
            indent_level = 0
            
            for line in lines:
                stripped = line.strip()
                
                # Hoppa över tomma rader
                if not stripped:
                    formatted_lines.append("")
                    continue
                
                # Upptäck minskning av indentering före raden bearbetas
                if stripped.startswith(('else:', 'elif ', 'except:', 'finally:', 'except ', 'except(')):
                    indent_level = max(0, indent_level - 1)
                
                # Lägg till rätt indentering
                formatted_lines.append("    " * indent_level + stripped)
                
                # Uppdatera indentering för nästa rad
                if stripped.endswith(':') and not stripped.startswith('#'):
                    indent_level += 1
                elif stripped.startswith('return ') or stripped.startswith('break') or stripped.startswith('continue'):
                    indent_level = max(0, indent_level)
                
                # Specialfall: slut på kodblock med dedent
                if stripped.startswith('pass') or stripped == 'pass':
                    indent_level = max(0, indent_level - 1)
            
            # Försök validera med AST
            try:
                import ast
                formatted_code = '\n'.join(formatted_lines)
                ast.parse(formatted_code)
                return formatted_code
            except SyntaxError:
                # Om AST misslyckas, återgå till originalformateringen
                return code
        
        except Exception:
            # Vid fel, återgå till originalformateringen
            return code
    
    def format_javascript_code(self, code):
        """Formatera JavaScript-kod"""
        try:
            # Enkel JavaScript-formatering
            lines = code.split('\n')
            formatted_lines = []
            indent_level = 0
            
            for line in lines:
                stripped = line.strip()
                
                # Hoppa över tomma rader
                if not stripped:
                    formatted_lines.append("")
                    continue
                
                # Minska indentering för slutande brackets
                if stripped.startswith('}') or stripped.startswith('})') or stripped == '};':
                    indent_level = max(0, indent_level - 1)
                
                # Lägg till rätt indentering
                formatted_lines.append("  " * indent_level + stripped)
                
                # Öka indentering efter öppnande brackets
                if stripped.endswith('{') or stripped.endswith('({') or stripped.endswith('= {'):
                    indent_level += 1
            
            return '\n'.join(formatted_lines)
        
        except Exception:
            # Vid fel, återgå till originalformateringen
            return code
    
    def ensure_correct_indentation(self, code, context="function"):
        """Säkerställ korrekt indentering baserat på kontext"""
        if context == "class_method" and self.module_data["extension"].lower().endswith('.py'):
            # Indentera med 4 mellanslag för klassmetoder i Python
            lines = code.split('\n')
            indented_lines = []
            
            for line in lines:
                indented_lines.append("    " + line)
            
            return '\n'.join(indented_lines)
        
        elif context == "class_method" and self.module_data["extension"].lower().endswith('.js'):
            # Indentera med 2 mellanslag för klassmetoder i JavaScript
            lines = code.split('\n')
            indented_lines = []
            
            for line in lines:
                indented_lines.append("  " + line)
            
            return '\n'.join(indented_lines)
        
        return code  # Ingen ändring om kontexten inte är specificerad
    
    def detect_entity_type(self, code):
        """Detektera typ av kodentitet (funktion, klass, variabel, etc.)"""
        code = code.strip()
        
        if self.module_data["extension"].lower().endswith('.py'):
            # Python-enhetsdetektering
            if code.startswith("def "):
                return "function"
            elif code.startswith("class "):
                return "class"
            elif "=" in code.split("\n")[0] and not code.split("\n")[0].strip().startswith(("def ", "class ", "if ", "for ", "while ")):
                return "variable"
            else:
                return "unknown"
        
        elif self.module_data["extension"].lower().endswith('.js'):
            # JavaScript-enhetsdetektering
            if code.startswith("function ") or "=> {" in code.split("\n")[0]:
                return "function"
            elif code.startswith("class "):
                return "class"
            elif code.startswith(("const ", "let ", "var ")) and "=" in code.split("\n")[0]:
                return "variable"
            else:
                return "unknown"
        
        return "unknown"
    
    def get_llm_system_prompt(self):
        """Generera en systemprompt för LLM för att hantera denna kodmodul"""
        extension = self.module_data["extension"].lower()
        language = "Python" if extension.endswith('.py') else "JavaScript" if extension.endswith('.js') else "okänt språk"
        
        prompt = f"""
# Systemkontext: Kodmodul-assistent

Du hjälper till att hantera och uppdatera en kodmodul med namnet '{self.module_data["name"]}' skriven i {language}.
Filen har filändelsen '{extension}'.

## Strukturinformation

Modulen innehåller:
- {len(self.function_cache)} funktioner
- {len(self.class_cache)} klasser
- {len(self.variable_cache)} globala variabler

## Uppgifter du kan utföra

1. **Lägg till en ny funktion eller klass**
   - Formatera koden korrekt enligt {language}-standard
   - Inkludera dokumentationskommentarer

2. **Uppdatera en befintlig funktion eller klass**
   - Specificera målet som ska uppdateras (namn)
   - Bevara befintlig dokumentation om möjligt
   - Indentera korrekt ({4 if extension.endswith('.py') else 2} mellanslag)

3. **Uppdatera en variabel**
   - För klassattribut, specificera `klass.attribut`
   - För globala variabler, ange bara variabelnamnet

4. **Analys och rekommendationer**
   - Analysera kodstruktur
   - Föreslå förbättringar
   - Identifiera potentiella problem

## Viktigt att tänka på

- Kodblock ska omges av markdown-formatering med språkspecifikation (```{language.lower()})
- För klassmetoder i {language}, säkerställ korrekt indentering och format
- Respektera befintlig kodstil
"""
        
        # Lägg till språkspecifika instruktioner
        if extension.endswith('.py'):
            prompt += """
## Python-specifika riktlinjer

- Använd PEP 8-formatering
- Inkludera docstrings för alla funktioner och klasser
- För klassmetoder, se till att 'self' är första parametern
- Indentera med 4 mellanslag (inte tabbar)
"""
        elif extension.endswith('.js'):
            prompt += """
## JavaScript-specifika riktlinjer

- Använd camelCase för variabler och funktioner
- Avsluta satser med semikolon
- Använd ES6-syntax där möjligt (arrow functions, const/let)
- Indentera med 2 mellanslag (inte tabbar)
"""
        
        # Lägg till exempel baserat på befintlig kod
        prompt += "\n## Exempel baserat på befintlig kod\n\n"
        
        # Ta ett exempelfunktion från koden om det finns någon
        if self.function_cache:
            func_name = next(iter(self.function_cache))
            prompt += f"### Exempel på funktionsuppdatering:\n\n```{language.lower()}\n"
            prompt += f"# Uppdatera funktionen '{func_name}'\n"
            prompt += f"# Observera formatering och indentering\n\n"
            if extension.endswith('.py'):
                prompt += f"def {func_name}({', '.join(self.function_cache[func_name].get('params', []))}):\n"
                prompt += f"    \"\"\"\n    Beskrivning av funktionen\n    \"\"\"\n"
                prompt += f"    # Implementering\n    pass\n"
            elif extension.endswith('.js'):
                prompt += f"function {func_name}({', '.join(self.function_cache[func_name].get('params', []))}) {{\n"
                prompt += f"  // Implementering\n  return null;\n}}\n"
            prompt += "```\n\n"
        
        # Ta ett exempel på en klassdefinition från koden om det finns någon
        if self.class_cache:
            class_name = next(iter(self.class_cache))
            prompt += f"### Exempel på klassuppdatering:\n\n```{language.lower()}\n"
            prompt += f"# Uppdatera klassen '{class_name}'\n\n"
            if extension.endswith('.py'):
                prompt += f"class {class_name}:\n"
                prompt += f"    \"\"\"\n    Beskrivning av klassen\n    \"\"\"\n\n"
                prompt += f"    def __init__(self):\n"
                prompt += f"        # Initiera klassen\n        pass\n"
            elif extension.endswith('.js'):
                prompt += f"class {class_name} {{\n"
                prompt += f"  constructor() {{\n    // Initiera klassen\n  }}\n}}\n"
            prompt += "```\n\n"
        
        return prompt
    
    # Hjälpfunktioner för att hitta positioner i koden
    def get_function_code_bounds(self, function_name):
        """Hitta gränserna (start- och slutposition) för en funktion i koden"""
        if function_name in self.function_cache:
            func_info = self.function_cache[function_name]
            
            if hasattr(func_info, 'ast_node'):
                # Via AST
                start_line = func_info.ast_node.lineno - 1
                end_line = func_info.ast_node.end_lineno if hasattr(func_info.ast_node, 'end_lineno') else -1
                
                # Om end_line inte är tillgänglig, försök hitta den manuellt
                if end_line < 0:
                    code = self.code_editor.toPlainText()
                    lines = code.split('\n')
                    
                    # Hitta indentering för funktionsdefinitionen
                    func_indent = len(lines[start_line]) - len(lines[start_line].lstrip())
                    
                    # Sök framåt för att hitta första raden med mindre indentering
                    end_line = start_line
                    for i in range(start_line + 1, len(lines)):
                        line = lines[i]
                        if line.strip() and len(line) - len(line.lstrip()) <= func_indent:
                            # Hittade en rad med samma eller mindre indentering
                            end_line = i - 1
                            break
                        end_line = i
                
                return start_line, end_line
        
        # Om funktionen inte hittades eller bounds inte kunde fastställas
        return -1, -1
    
    def get_class_code_bounds(self, class_name):
        """Hitta gränserna (start- och slutposition) för en klass i koden"""
        if class_name in self.class_cache:
            class_info = self.class_cache[class_name]
            
            if hasattr(class_info, 'ast_node'):
                # Via AST
                start_line = class_info.ast_node.lineno - 1

## =======    PART - 5    ======= ##
                end_line = class_info.ast_node.end_lineno if hasattr(class_info.ast_node, 'end_lineno') else -1
                
                # Om end_line inte är tillgänglig, försök hitta den manuellt
                if end_line < 0:
                    code = self.code_editor.toPlainText()
                    lines = code.split('\n')
                    
                    # Hitta indentering för klassdefinitionen
                    class_indent = len(lines[start_line]) - len(lines[start_line].lstrip())
                    
                    # Sök framåt för att hitta första raden med mindre indentering
                    end_line = start_line
                    for i in range(start_line + 1, len(lines)):
                        line = lines[i]
                        if line.strip() and len(line) - len(line.lstrip()) <= class_indent:
                            # Hittade en rad med samma eller mindre indentering
                            end_line = i - 1
                            break
                        end_line = i
                
                return start_line, end_line
        
        # Om klassen inte hittades eller bounds inte kunde fastställas
        return -1, -1
    
    def get_method_code_bounds(self, class_name, method_name):
        """Hitta gränserna (start- och slutposition) för en metod i en klass"""
        if class_name in self.class_cache:
            class_info = self.class_cache[class_name]
            
            if "methods" in class_info and method_name in class_info["methods"]:
                method_info = class_info["methods"][method_name]
                
                if hasattr(method_info, 'ast_node'):
                    # Via AST
                    start_line = method_info.ast_node.lineno - 1
                    end_line = method_info.ast_node.end_lineno if hasattr(method_info.ast_node, 'end_lineno') else -1
                    
                    # Om end_line inte är tillgänglig, försök hitta den manuellt
                    if end_line < 0:
                        code = self.code_editor.toPlainText()
                        lines = code.split('\n')
                        
                        # Hitta indentering för metoddefinitionen
                        method_indent = len(lines[start_line]) - len(lines[start_line].lstrip())
                        
                        # Sök framåt för att hitta första raden med samma eller mindre indentering
                        end_line = start_line
                        for i in range(start_line + 1, len(lines)):
                            line = lines[i]
                            if line.strip() and len(line) - len(line.lstrip()) <= method_indent:
                                # Hittade en rad med samma eller mindre indentering
                                end_line = i - 1
                                break
                            end_line = i
                    
                    return start_line, end_line
        
        # Om metoden inte hittades eller bounds inte kunde fastställas
        return -1, -1
    
    def get_variable_code_bounds(self, variable_name):
        """Hitta gränserna (start- och slutposition) för en variabel i koden"""
        if variable_name in self.variable_cache:
            var_info = self.variable_cache[variable_name]
            
            if hasattr(var_info, 'ast_node'):
                # Via AST
                start_line = var_info.ast_node.lineno - 1
                
                # Variabler är normalt på en rad, men vi kontrollerar om det finns flerradiga värden
                code = self.code_editor.toPlainText()
                lines = code.split('\n')
                
                # Kolla om tilldelningen fortsätter på nästa rad
                if lines[start_line].rstrip().endswith(('\\', '(', '[', '{')):
                    # Tilldelningen kan fortsätta på flera rader
                    open_brackets = lines[start_line].count('(') - lines[start_line].count(')') \
                                  + lines[start_line].count('[') - lines[start_line].count(']') \
                                  + lines[start_line].count('{') - lines[start_line].count('}')
                    
                    end_line = start_line
                    for i in range(start_line + 1, len(lines)):
                        line = lines[i]
                        open_brackets += line.count('(') - line.count(')') \
                                      + line.count('[') - line.count(']') \
                                      + line.count('{') - line.count('}')
                        end_line = i
                        
                        if open_brackets <= 0 and not line.rstrip().endswith('\\'):
                            # Slutet på flerradig tilldelning
                            break
                else:
                    # En-radstilldelning
                    end_line = start_line
                
                return start_line, end_line
        
        # Om variabeln inte hittades eller bounds inte kunde fastställas
        return -1, -1
    
    def apply_automatic_formatting(self, code):
        """Tillämpa automatisk formatering och indentering på kod"""
        extension = self.module_data["extension"].lower()
        code_type = self.detect_entity_type(code)
        
        # Formatera beroende på kodtyp och språk
        if extension.endswith('.py'):
            # Python-formatering
            if code_type == "function":
                return self.format_python_function(code)
            elif code_type == "class":
                return self.format_python_class(code)
            elif code_type == "class_method":
                return self.format_python_method(code)
            else:
                return self.format_python_code(code)
        
        elif extension.endswith('.js'):
            # JavaScript-formatering
            if code_type == "function":
                return self.format_javascript_function(code)
            elif code_type == "class":
                return self.format_javascript_class(code)
            elif code_type == "class_method":
                return self.format_javascript_method(code)
            else:
                return self.format_javascript_code(code)
        
        return code  # Standardfall utan formatering
    
    def format_python_function(self, code):
        """Formatera Python-funktion specifikt"""
        lines = code.split('\n')
        formatted_lines = []
        
        # Identifiera indentering för funktionsdefinitionen
        if lines and lines[0].strip().startswith("def "):
            base_indent = ""  # Ingen indrag för global funktion
            formatted_lines.append(lines[0].strip())  # Första raden (def ...)
            
            # Sätt funktionskroppsindentering
            body_indent = "    "  # 4 mellanslag
            
            # Formatera resten av funktionen
            for i in range(1, len(lines)):
                line = lines[i].strip()
                if line:
                    formatted_lines.append(body_indent + line)
                else:
                    formatted_lines.append("")
        else:
            # Om det inte är en välformaterad funktion, använd standardformatering
            return self.format_python_code(code)
        
        return '\n'.join(formatted_lines)
    
    def format_python_class(self, code):
        """Formatera Python-klass specifikt"""
        lines = code.split('\n')
        formatted_lines = []
        
        # Identifiera klassdefinitionen
        if lines and lines[0].strip().startswith("class "):
            base_indent = ""  # Ingen indrag för global klass
            formatted_lines.append(lines[0].strip())  # Första raden (class ...)
            
            # Formatera resten av klassen, med indentering
            in_method = False
            method_name = ""
            
            for i in range(1, len(lines)):
                line = lines[i].strip()
                
                if not line:
                    formatted_lines.append("")
                    continue
                
                # Ny metod startar
                if line.startswith("def "):
                    in_method = True
                    method_name = line.split("(")[0].replace("def ", "").strip()
                    formatted_lines.append("    " + line)  # En nivås indrag för metoder
                elif in_method:
                    # Vi är inne i en metod
                    formatted_lines.append("        " + line)  # Två nivåers indrag
                else:
                    # Klassattribut eller andra klassdeklarationer
                    formatted_lines.append("    " + line)  # En nivås indrag
        else:
            # Om det inte är en välformaterad klass, använd standardformatering
            return self.format_python_code(code)
        
        return '\n'.join(formatted_lines)
    
    def format_python_method(self, code):
        """Formatera Python-metod specifikt"""
        lines = code.split('\n')
        formatted_lines = []
        
        # Identifiera metoddefinitionen
        if lines and lines[0].strip().startswith("def "):
            # Metoder ska ha en nivås indrag
            base_indent = "    "  # 4 mellanslag
            formatted_lines.append(base_indent + lines[0].strip())  # Första raden (def ...)
            
            # Formatera metodkroppen
            body_indent = base_indent + "    "  # 8 mellanslag totalt
            
            for i in range(1, len(lines)):
                line = lines[i].strip()
                if line:
                    formatted_lines.append(body_indent + line)
                else:
                    formatted_lines.append("")
        else:
            # Om det inte är en välformaterad metod, indentera hela koden
            for line in lines:
                if line.strip():
                    formatted_lines.append("    " + line.strip())
                else:
                    formatted_lines.append("")
        
        return '\n'.join(formatted_lines)
    
    def format_javascript_function(self, code):
        """Formatera JavaScript-funktion specifikt"""
        lines = code.split('\n')
        formatted_lines = []
        
        # Identifiera funktionsdefinitionen
        is_function_line = False
        if lines:
            first_line = lines[0].strip()
            is_function_line = (
                first_line.startswith("function ") or  # Traditionell funktion
                re.match(r'(?:const|let|var)\s+[a-zA-Z_$][a-zA-Z0-9_$]*\s*=\s*function', first_line) or  # Funktionsuttryck
                re.match(r'(?:const|let|var)\s+[a-zA-Z_$][a-zA-Z0-9_$]*\s*=\s*\(.*\)\s*=>', first_line)  # Arrow function
            )
        
        if is_function_line:
            base_indent = ""  # Ingen indrag för global funktion
            formatted_lines.append(lines[0].strip())  # Första raden
            
            # Sätt funktionskroppsindentering
            body_indent = "  "  # 2 mellanslag
            
            # Formatera resten av funktionen
            inside_brackets = 0
            for i in range(1, len(lines)):
                line = lines[i].strip()
                
                if not line:
                    formatted_lines.append("")
                    continue
                
                # Räkna öppna brackets för att hantera nästlade block
                inside_brackets += line.count('{') - line.count('}')
                
                # Justera indentering baserat på om raden börjar med en stängande bracket
                if line.startswith('}'):
                    indent_level = max(0, inside_brackets)
                    formatted_lines.append(body_indent * indent_level + line)
                else:
                    indent_level = max(0, inside_brackets + (1 if '{' in line else 0))
                    formatted_lines.append(body_indent * indent_level + line)
        else:
            # Om det inte är en välformaterad funktion, använd standardformatering
            return self.format_javascript_code(code)
        
        return '\n'.join(formatted_lines)
    
    def format_javascript_class(self, code):
        """Formatera JavaScript-klass specifikt"""
        lines = code.split('\n')
        formatted_lines = []
        
        # Identifiera klassdefinitionen
        if lines and lines[0].strip().startswith("class "):
            base_indent = ""  # Ingen indrag för global klass
            formatted_lines.append(lines[0].strip())  # Första raden (class ...)
            
            # Formatera resten av klassen, med indentering
            inside_braces = 0
            in_method = False
            
            for i in range(1, len(lines)):
                line = lines[i].strip()
                
                if not line:
                    formatted_lines.append("")
                    continue
                
                # Räkna brackets för att hålla reda på nästling
                inside_braces += line.count('{') - line.count('}')
                
                # Ny metod startar
                if (re.match(r'[a-zA-Z_$][a-zA-Z0-9_$]*\s*\(', line) or 
                    line.startswith('get ') or 
                    line.startswith('set ') or 
                    line.startswith('async ')):
                    in_method = True
                    formatted_lines.append("  " + line)  # En nivås indrag för metoder
                elif line.startswith('}'):
                    # Slutet på ett block
                    if inside_braces == 0:
                        # Slutet på klassen
                        formatted_lines.append(line)
                    else:
                        # Slutet på metod eller inre block
                        indent_level = max(1, inside_braces + 1)
                        formatted_lines.append("  " * indent_level + line)
                else:
                    # Klassattribut eller metodinnehåll
                    indent_level = max(1, inside_braces + (0 if in_method else 1))
                    formatted_lines.append("  " * indent_level + line)
        else:
            # Om det inte är en välformaterad klass, använd standardformatering
            return self.format_javascript_code(code)
        
        return '\n'.join(formatted_lines)
    
    def format_javascript_method(self, code):
        """Formatera JavaScript-metod specifikt"""
        lines = code.split('\n')
        formatted_lines = []
        
        # Identifiera metoddefinitionen
        is_method = False
        if lines:
            first_line = lines[0].strip()
            is_method = (
                re.match(r'[a-zA-Z_$][a-zA-Z0-9_$]*\s*\(', first_line) or
                first_line.startswith('get ') or
                first_line.startswith('set ') or
                first_line.startswith('async ')
            )
        
        if is_method:
            # Metoder ska ha en nivås indrag i klasser
            base_indent = "  "  # 2 mellanslag
            formatted_lines.append(base_indent + lines[0].strip())  # Första raden
            
            # Formatera metodkroppen
            body_indent = "    "  # 4 mellanslag totalt för metodkropp
            
            inside_brackets = 0
            for i in range(1, len(lines)):
                line = lines[i].strip()
                
                if not line:
                    formatted_lines.append("")
                    continue
                
                # Räkna bracket för att hålla reda på nästlingsnivå
                inside_brackets += line.count('{') - line.count('}')
                
                # Justera indentering
                if line.startswith('}'):
                    indent = base_indent + "  " * max(0, inside_brackets)
                    formatted_lines.append(indent + line)
                else:
                    indent = base_indent + "  " * max(0, inside_brackets + (1 if '{' in line else 0))
                    formatted_lines.append(indent + line)
        else:
            # Om det inte är en välformaterad metod, indentera hela koden
            for line in lines:
                if line.strip():
                    formatted_lines.append("  " + line.strip())
                else:
                    formatted_lines.append("")
        
        return '\n'.join(formatted_lines)
    
    # API för extern åtkomst (för AI-integrering)
    def get_code(self):
        """Hämta hela modulkoden"""
        return self.code_editor.toPlainText()
    
    def set_code(self, code):
        """Sätt hela modulkoden"""
        self.code_editor.setPlainText(code)
        return True
    
    def get_function(self, function_name):
        """Hämta koden för en specifik funktion"""
        start, end = self.get_function_code_bounds(function_name)
        if start >= 0 and end >= start:
            lines = self.code_editor.toPlainText().split('\n')
            return '\n'.join(lines[start:end+1])
        return None
    
    def update_function(self, function_name, new_code):
        """Uppdatera en befintlig funktion"""
        start, end = self.get_function_code_bounds(function_name)
        if start >= 0 and end >= start:
            # Formatera den nya koden
            formatted_code = self.format_code(new_code)
            
            # Uppdatera koden
            lines = self.code_editor.toPlainText().split('\n')
            new_lines = lines[:start] + formatted_code.split('\n') + lines[end+1:]
            
            self.code_editor.setPlainText('\n'.join(new_lines))
            self.update_code_structure_cache()
            self.update_structure_tree()
            return True
        return False
    
    def add_function(self, function_name, code):
        """Lägg till en ny funktion i modulen"""
        # Kontrollera om funktionen redan finns
        if function_name in self.function_cache:
            return False
        
        # Formatera koden
        formatted_code = self.format_code(code)
        
        # Lägg till i slutet av filen
        current_code = self.code_editor.toPlainText()
        
        if current_code.strip():
            new_code = current_code + "\n\n" + formatted_code
        else:
            new_code = formatted_code
        
        self.code_editor.setPlainText(new_code)
        self.update_code_structure_cache()
        self.update_structure_tree()
        return True
    
    def get_class(self, class_name):
        """Hämta koden för en specifik klass"""
        start, end = self.get_class_code_bounds(class_name)
        if start >= 0 and end >= start:
            lines = self.code_editor.toPlainText().split('\n')
            return '\n'.join(lines[start:end+1])
        return None
    
    def update_class(self, class_name, new_code):
        """Uppdatera en befintlig klass"""
        start, end = self.get_class_code_bounds(class_name)
        if start >= 0 and end >= start:
            # Formatera den nya koden
            formatted_code = self.format_code(new_code)
            
            # Uppdatera koden
            lines = self.code_editor.toPlainText().split('\n')
            new_lines = lines[:start] + formatted_code.split('\n') + lines[end+1:]
            
            self.code_editor.setPlainText('\n'.join(new_lines))
            self.update_code_structure_cache()
            self.update_structure_tree()
            return True
        return False
    
    def add_class(self, class_name, code):
        """Lägg till en ny klass i modulen"""
        # Kontrollera om klassen redan finns
        if class_name in self.class_cache:
            return False
        
        # Formatera koden
        formatted_code = self.format_code(code)
        
        # Lägg till i slutet av filen
        current_code = self.code_editor.toPlainText()
        
        if current_code.strip():
            new_code = current_code + "\n\n" + formatted_code
        else:
            new_code = formatted_code
        
        self.code_editor.setPlainText(new_code)
        self.update_code_structure_cache()
        self.update_structure_tree()
        return True
    
    def get_method(self, class_name, method_name):
        """Hämta koden för en specifik metod"""
        start, end = self.get_method_code_bounds(class_name, method_name)
        if start >= 0 and end >= start:
            lines = self.code_editor.toPlainText().split('\n')
            return '\n'.join(lines[start:end+1])
        return None
    
    def update_method(self, class_name, method_name, new_code):
        """Uppdatera en befintlig metod"""
        start, end = self.get_method_code_bounds(class_name, method_name)
        if start >= 0 and end >= start:
            # Formatera koden för metodkontext
            formatted_code = self.ensure_correct_indentation(
                self.format_code(new_code), 
                "class_method"
            )
            
            # Uppdatera koden
            lines = self.code_editor.toPlainText().split('\n')
            new_lines = lines[:start] + formatted_code.split('\n') + lines[end+1:]
            
            self.code_editor.setPlainText('\n'.join(new_lines))
            self.update_code_structure_cache()
            self.update_structure_tree()
            return True
        return False
    
    def add_method(self, class_name, method_name, code):
        """Lägg till en ny metod i en klass"""
        # Kontrollera om klassen finns
        if class_name not in self.class_cache:
            return False
        
        class_info = self.class_cache[class_name]
        
        # Kontrollera om metoden redan finns
        if "methods" in class_info and method_name in class_info["methods"]:
            return False
        
        # Formatera koden för metodkontext
        formatted_code = self.ensure_correct_indentation(
            self.format_code(code), 
            "class_method"
        )
        
        # Hitta slutet av klassen
        start, end = self.get_class_code_bounds(class_name)
        if start < 0 or end < start:
            return False
        
        # Lägg till metoden i slutet av klassen
        lines = self.code_editor.toPlainText().split('\n')
        new_lines = lines[:end] + formatted_code.split('\n') + lines[end:]
        
        self.code_editor.setPlainText('\n'.join(new_lines))
        self.update_code_structure_cache()
        self.update_structure_tree()
        return True
    
    def get_variable(self, variable_name):
        """Hämta värdet för en global variabel"""
        if variable_name in self.variable_cache:
            start, end = self.get_variable_code_bounds(variable_name)
            if start >= 0 and end >= start:
                lines = self.code_editor.toPlainText().split('\n')
                var_code = '\n'.join(lines[start:end+1])
                
                # Försök extrahera bara värdet
                match = re.search(rf'{re.escape(variable_name)}\s*=\s*(.*)', var_code)
                if match:
                    return match.group(1)
                return var_code
        return None
    
    def update_variable(self, variable_name, new_value):
        """Uppdatera en befintlig variabel"""
        start, end = self.get_variable_code_bounds(variable_name)
        if start >= 0 and end >= start:
            lines = self.code_editor.toPlainText().split('\n')
            var_line = lines[start]
            
            # Hitta positionen för "="
            pos = var_line.find('=')
            if pos >= 0:
                # Behåll variabeldeklarationen, uppdatera bara värdet
                new_line = var_line[:pos+1] + " " + new_value
                
                # Uppdatera koden
                new_lines = lines[:start] + [new_line] + lines[end+1:]
                
                self.code_editor.setPlainText('\n'.join(new_lines))
                self.update_code_structure_cache()
                self.update_structure_tree()
                return True
        return False
    
    def add_variable(self, variable_name, value):
        """Lägg till en ny global variabel"""
        # Kontrollera om variabeln redan finns
        if variable_name in self.variable_cache:
            return False
        
        # Skapa variabeldeklarationen
        if self.module_data["extension"].lower().endswith('.py'):
            var_declaration = f"{variable_name} = {value}"
        elif self.module_data["extension"].lower().endswith('.js'):
            var_declaration = f"const {variable_name} = {value};"
        else:
            var_declaration = f"{variable_name} = {value}"
        
        # Lägg till i början av filen
        current_code = self.code_editor.toPlainText()
        
        if current_code.strip():
            new_code = var_declaration + "\n\n" + current_code
        else:
            new_code = var_declaration
        
        self.code_editor.setPlainText(new_code)
        self.update_code_structure_cache()
        self.update_structure_tree()
        return True

    @property
    def tags(self):
        return self.module_data.get("tags", [])