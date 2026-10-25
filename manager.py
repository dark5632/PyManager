import sys
import os
import json
import shutil
import codecs
import html
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QPushButton, QListWidget, 
                               QTextEdit, QSplitter, QMessageBox, QListWidgetItem,
                               QPlainTextEdit, QToolButton, QFrame, QCheckBox, 
                               QSpinBox, QDialog, QLineEdit, QStackedWidget, QMenu, QFileDialog)
from PySide6.QtCore import Qt, QProcess, QSize, QRegularExpression, QPoint
from PySide6.QtGui import (QFont, QIcon, QPixmap, QSyntaxHighlighter, QTextCharFormat, 
                           QColor, QShortcut, QKeySequence, QPalette)

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- ПОДСВЕТКА СИНТАКСИСА ---
class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setFontWeight(QFont.Weight.Bold)
        self.string_format = QTextCharFormat()
        self.comment_format = QTextCharFormat()

        keywords = ["False", "None", "True", "and", "as", "assert", "async", "await",
                    "break", "class", "continue", "def", "del", "elif", "else", "except",
                    "finally", "for", "from", "global", "if", "import", "in", "is", "lambda",
                    "nonlocal", "not", "or", "pass", "raise", "return", "try", "while", "with", "yield"]
        for word in keywords:
            pattern = QRegularExpression(r"\b" + word + r"\b")
            self.highlighting_rules.append((pattern, self.keyword_format))

        self.highlighting_rules.append((QRegularExpression(r"\".*\""), self.string_format))
        self.highlighting_rules.append((QRegularExpression(r"'.*'"), self.string_format))
        self.highlighting_rules.append((QRegularExpression(r"#[^\n]*"), self.comment_format))
        self.set_theme("dark")

    def set_theme(self, theme):
        if theme == "dark":
            self.keyword_format.setForeground(QColor("#569cd6"))
            self.string_format.setForeground(QColor("#ce9178"))
            self.comment_format.setForeground(QColor("#6a9955"))
        else:
            self.keyword_format.setForeground(QColor("#0000ff"))
            self.string_format.setForeground(QColor("#a31515"))
            self.comment_format.setForeground(QColor("#008000"))
        self.rehighlight()

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

# --- SVG ИКОНКИ ---
def get_svg_icon(svg_str, color="#cccccc"):
    svg_str = svg_str.replace("currentColor", color)
    pixmap = QPixmap()
    pixmap.loadFromData(svg_str.encode('utf-8'))
    return QIcon(pixmap)

ICON_FILE = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path><polyline points="13 2 13 9 20 9"></polyline></svg>"""
ICON_PLUS = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>"""
ICON_IMPORT = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>"""
ICON_PLAY = """<svg viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"><path d="M7 4.5v15a1 1 0 0 0 1.5.86l12-7.5a1 1 0 0 0 0-1.72l-12-7.5A1 1 0 0 0 7 4.5z"/></svg>"""
ICON_STOP = """<svg viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="6" y="6" width="12" height="12" rx="2" ry="2"></rect></svg>"""
ICON_BOX = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="16.5" y1="9.4" x2="7.5" y2="4.21"></line><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>"""
ICON_SAVE = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>"""
ICON_SETTINGS = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>"""

# --- ДИАЛОГИ ---
class StyledDialog(QDialog):
    def __init__(self, parent, title_text):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.container = QFrame()
        self.container.setObjectName("dialogContainer")
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        self.title_label = QLabel(title_text)
        self.title_label.setObjectName("dialogTitle")
        self.title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.layout.addWidget(self.title_label)
        
        self.main_layout.addWidget(self.container)
        self.apply_style(parent.current_theme if parent else "dark")

    def apply_style(self, theme):
        if theme == "dark":
            bg, border, text, input_bg, btn_bg = "#252526", "#333333", "#cccccc", "#1e1e1e", "#007acc"
        else:
            bg, border, text, input_bg, btn_bg = "#ececec", "#d4d4d4", "#000000", "#ffffff", "#007acc"

        self.setStyleSheet(f"""
            QFrame#dialogContainer {{ background-color: {bg}; border: 1px solid {border}; border-radius: 8px; }}
            QLabel#dialogTitle {{ color: {text}; }}
            QLabel#dialogText {{ color: {text}; font-size: 13px; }}
            QLineEdit#dialogInput {{ background-color: {input_bg}; color: {text}; border: 1px solid {border}; border-radius: 4px; padding: 0 10px; font-size: 13px; }}
            QPushButton {{ border-radius: 4px; padding: 8px; font-weight: bold; }}
            QPushButton#dialogBtnCancel {{ background-color: transparent; color: {text}; border: 1px solid {border}; }}
            QPushButton#dialogBtnCancel:hover {{ background-color: {border}; }}
            QPushButton#dialogBtnAction {{ background-color: {btn_bg}; color: white; border: 1px solid {btn_bg}; }}
            QPushButton#dialogBtnAction:hover {{ background-color: #1d4ed8; }}
            QPushButton#dialogBtnDanger {{ background-color: #e11d48; color: white; border: 1px solid #e11d48; }}
            QPushButton#dialogBtnDanger:hover {{ background-color: #be123c; }}
            QLabel#settingLabel {{ color: {text}; font-size: 13px; }}
            QCheckBox#settingSwitch {{ color: {text}; font-size: 14px; spacing: 10px; }}
            QCheckBox#settingSwitch::indicator {{ width: 18px; height: 18px; border-radius: 4px; border: 1px solid {border}; background-color: {input_bg}; }}
            QCheckBox#settingSwitch::indicator:checked {{ background-color: #007acc; border: 1px solid #007acc; }}
            QSpinBox#settingSpin {{ background-color: {input_bg}; color: {text}; border: 1px solid {border}; border-radius: 4px; padding: 4px; font-size: 13px; }}
        """)

class NewFileDialog(StyledDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Новый проект")
        self.setFixedSize(320, 170)
        self.input = QLineEdit()
        self.input.setPlaceholderText("например: my_project")
        self.input.setObjectName("dialogInput")
        self.input.setFixedHeight(38)
        self.layout.addWidget(self.input)
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Отмена")
        btn_cancel.setObjectName("dialogBtnCancel")
        btn_cancel.clicked.connect(self.reject)
        btn_create = QPushButton("Создать")
        btn_create.setObjectName("dialogBtnAction")
        btn_create.clicked.connect(self.accept)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_create)
        self.layout.addLayout(btn_layout)

class RenameFileDialog(StyledDialog):
    def __init__(self, parent=None, current_name=""):
        super().__init__(parent, "Переименовать")
        self.setFixedSize(320, 170)
        self.input = QLineEdit()
        self.input.setText(current_name)
        self.input.setObjectName("dialogInput")
        self.input.setFixedHeight(38)
        self.layout.addWidget(self.input)
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Отмена")
        btn_cancel.setObjectName("dialogBtnCancel")
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("Сохранить")
        btn_save.setObjectName("dialogBtnAction")
        btn_save.clicked.connect(self.accept)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        self.layout.addLayout(btn_layout)

class DeleteFileDialog(StyledDialog):
    def __init__(self, parent=None, filename="", action_text="удалить"):
        super().__init__(parent, "Подтверждение")
        self.setFixedSize(350, 180)
        lbl = QLabel(f"Вы точно хотите {action_text} файл\n<b>{filename}</b>?")
        lbl.setObjectName("dialogText")
        lbl.setWordWrap(True)
        # Убрали выравнивание по центру, теперь по левому краю
        self.layout.addWidget(lbl)
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Нет")
        btn_cancel.setObjectName("dialogBtnCancel")
        btn_cancel.clicked.connect(self.reject)
        btn_yes = QPushButton("Да")
        btn_yes.setObjectName("dialogBtnDanger")
        btn_yes.clicked.connect(self.accept)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_yes)
        self.layout.addLayout(btn_layout)

class SettingsDialog(StyledDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Настройки")
        self.setFixedSize(520, 400) 
        
        self.check_theme = QCheckBox("Темная тема")
        self.check_theme.setChecked(parent.current_theme == "dark")
        self.check_theme.setObjectName("settingSwitch")
        # Изменено на внутренний метод для обновления стиля
        self.check_theme.toggled.connect(self.toggle_theme_local) 
        self.layout.addWidget(self.check_theme)
        
        self.check_autosave = QCheckBox("Автосохранение")
        self.check_autosave.setChecked(parent.auto_save_enabled)
        self.check_autosave.setObjectName("settingSwitch")
        self.check_autosave.toggled.connect(self.toggle_autosave)
        self.layout.addWidget(self.check_autosave)
        
        font_layout = QHBoxLayout()
        lbl_font = QLabel("Размер шрифта:")
        lbl_font.setObjectName("settingLabel")
        self.spin_font = QSpinBox()
        self.spin_font.setRange(8, 24)
        self.spin_font.setValue(parent.font_size)
        self.spin_font.setObjectName("settingSpin")
        self.spin_font.valueChanged.connect(parent.change_font_size)
        font_layout.addWidget(lbl_font)
        font_layout.addWidget(self.spin_font)
        font_layout.addStretch()
        self.layout.addLayout(font_layout)
        
        lbl_cmd = QLabel("Команда запуска (файл добавится в конец):")
        lbl_cmd.setObjectName("settingLabel")
        self.layout.addWidget(lbl_cmd)
        
        self.input_run_cmd = QLineEdit()
        self.input_run_cmd.setText(parent.custom_run_cmd)
        self.input_run_cmd.setObjectName("dialogInput")
        self.input_run_cmd.setFixedHeight(38)
        self.input_run_cmd.textChanged.connect(self.save_run_cmd)
        self.layout.addWidget(self.input_run_cmd)

        self.layout.addStretch()
        btn_close = QPushButton("Закрыть")
        btn_close.setObjectName("dialogBtnAction")
        btn_close.clicked.connect(self.accept)
        self.layout.addWidget(btn_close)

    def toggle_theme_local(self, checked):
        # Сначала сообщаем главному окну
        self.parent_window.toggle_theme(checked)
        # Затем применяем стиль к самим настройкам, используя актуальную тему главного окна
        self.apply_style(self.parent_window.current_theme)

    def toggle_autosave(self, checked):
        self.parent_window.auto_save_enabled = checked
        
    def save_run_cmd(self, text):
        self.parent_window.custom_run_cmd = text

class CompileMethodDialog(StyledDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Сборка проекта")
        self.setFixedSize(400, 260)
        
        lbl = QLabel("Каким способом вы хотите собрать программу?")
        lbl.setObjectName("dialogText")
        lbl.setWordWrap(True)
        # Убрали выравнивание по центру
        self.layout.addWidget(lbl)
        
        self.choice = None
        
        btn_layout = QVBoxLayout()
        btn_std = QPushButton("Стандартным (PyInstaller)")
        btn_std.setObjectName("dialogBtnAction")
        btn_std.clicked.connect(self.choose_std)
        
        btn_custom = QPushButton("Выбрать свою команду")
        btn_custom.setObjectName("dialogBtnCancel")
        btn_custom.clicked.connect(self.choose_custom)
        
        btn_cancel = QPushButton("Закрыть")
        btn_cancel.setObjectName("dialogBtnCancel")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_std)
        btn_layout.addWidget(btn_custom)
        btn_layout.addWidget(btn_cancel)
        self.layout.addLayout(btn_layout)

    def choose_std(self):
        self.choice = "std"
        self.accept()
        
    def choose_custom(self):
        self.choice = "custom"
        self.accept()

class CustomCompileDialog(StyledDialog):
    def __init__(self, parent=None, current_cmd=""):
        super().__init__(parent, "Укажите команду .py")
        self.setFixedSize(480, 200)
        
        lbl = QLabel("Введите команду (файл .py добавится в конец автоматически):")
        lbl.setObjectName("dialogText")
        lbl.setWordWrap(True)
        # Убрали выравнивание по центру
        self.layout.addWidget(lbl)
        
        self.input = QLineEdit()
        self.input.setText(current_cmd)
        self.input.setObjectName("dialogInput")
        self.input.setFixedHeight(38)
        self.layout.addWidget(self.input)
        
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Отмена")
        btn_cancel.setObjectName("dialogBtnCancel")
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("Собрать")
        btn_ok.setObjectName("dialogBtnAction")
        btn_ok.clicked.connect(self.accept)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        self.layout.addLayout(btn_layout)

# --- ГЛАВНОЕ ОКНО ---
class PythonManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyManager")
        self.resize(1200, 800)
        
        icon_path_ico = get_resource_path("app_icon.ico")
        icon_path_png = get_resource_path("app_icon.png")
        if os.path.exists(icon_path_ico):
            self.setWindowIcon(QIcon(icon_path_ico))
        elif os.path.exists(icon_path_png):
            self.setWindowIcon(QIcon(icon_path_png))
        
        if getattr(sys, 'frozen', False):
            self.base_dir = Path.home() / "PyManager"
        else:
            self.base_dir = Path(__file__).parent.resolve()

        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.project_dir = self.base_dir / "project"
        self.project_dir.mkdir(exist_ok=True)
        
        self.config_file = self.base_dir / "workspace.json"
        self.active_files = [] 
        self.load_workspace() 
        
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)
        
        self.stdout_decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
        self.stderr_decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
        
        self.current_theme = "dark"
        self.font_size = 11
        self.auto_save_enabled = True
        
        self.custom_run_cmd = 'python -X utf8'
        self.last_custom_compile_cmd = 'python -m PyInstaller --noconfirm --onefile --windowed'
        
        self.file_logs = {} 
        self.active_file_path = None

        self.init_ui()
        self.apply_styles()
        self.refresh_list()

        QShortcut(QKeySequence("Ctrl+S"), self, self.save_current_file)
        QShortcut(QKeySequence("F5"), self, self.run_script)

    def load_workspace(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.active_files = json.load(f)
                self.active_files = [f for f in self.active_files if Path(f).exists()]
            except Exception:
                self.active_files = []

    def save_workspace(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.active_files, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения workspace: {e}")

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10) 
        main_layout.setSpacing(10)

        self.sidebar_container = QFrame()
        self.sidebar_container.setObjectName("sidebarContainer")
        self.sidebar_container.setFixedWidth(300)
        sidebar_layout = QHBoxLayout(self.sidebar_container)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        self.activity_bar = QFrame()
        self.activity_bar.setObjectName("activityBar")
        self.activity_bar.setFixedWidth(50)
        activity_layout = QVBoxLayout(self.activity_bar)
        activity_layout.setContentsMargins(0, 10, 0, 10)
        activity_layout.setSpacing(10)

        self.btn_run = QToolButton()
        self.btn_run.setIconSize(QSize(24, 24))
        self.btn_run.setToolTip("Запустить скрипт (F5)")
        self.btn_run.setObjectName("activityBtn")
        self.btn_run.clicked.connect(self.run_script)
        activity_layout.addWidget(self.btn_run, alignment=Qt.AlignHCenter)

        self.btn_stop = QToolButton()
        self.btn_stop.setIconSize(QSize(24, 24))
        self.btn_stop.setToolTip("Остановить процесс")
        self.btn_stop.setObjectName("activityBtn")
        self.btn_stop.clicked.connect(self.stop_script)
        self.btn_stop.hide()
        activity_layout.addWidget(self.btn_stop, alignment=Qt.AlignHCenter)

        self.btn_compile = QToolButton()
        self.btn_compile.setIconSize(QSize(24, 24))
        self.btn_compile.setToolTip("Собрать в .exe")
        self.btn_compile.setObjectName("activityBtn")
        self.btn_compile.clicked.connect(self.compile_script)
        activity_layout.addWidget(self.btn_compile, alignment=Qt.AlignHCenter)

        activity_layout.addStretch() 

        self.btn_save = QToolButton()
        self.btn_save.setIconSize(QSize(22, 22))
        self.btn_save.setToolTip("Сохранить (Ctrl+S)")
        self.btn_save.setObjectName("activityBtn")
        self.btn_save.clicked.connect(self.save_current_file)
        activity_layout.addWidget(self.btn_save, alignment=Qt.AlignHCenter)

        self.btn_settings = QToolButton()
        self.btn_settings.setIconSize(QSize(22, 22))
        self.btn_settings.setToolTip("Настройки")
        self.btn_settings.setObjectName("activityBtn")
        self.btn_settings.clicked.connect(self.open_settings)
        activity_layout.addWidget(self.btn_settings, alignment=Qt.AlignHCenter)

        sidebar_layout.addWidget(self.activity_bar)

        self.explorer_panel = QFrame()
        self.explorer_panel.setObjectName("explorerPanel")
        explorer_layout = QVBoxLayout(self.explorer_panel)
        explorer_layout.setContentsMargins(10, 10, 10, 10)
        explorer_layout.setSpacing(5)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(5, 0, 5, 0)
        title = QLabel("PyManager")
        title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title.setObjectName("panelTitle")
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.btn_import = QToolButton()
        self.btn_import.setIconSize(QSize(16, 16))
        self.btn_import.setToolTip("Загрузить .py файл с компьютера")
        self.btn_import.setObjectName("explorerBtn")
        self.btn_import.clicked.connect(self.import_file)
        header_layout.addWidget(self.btn_import)

        self.btn_new_file = QToolButton()
        self.btn_new_file.setIconSize(QSize(16, 16))
        self.btn_new_file.setToolTip("Создать новый проект")
        self.btn_new_file.setObjectName("explorerBtn")
        self.btn_new_file.clicked.connect(self.create_new_file)
        header_layout.addWidget(self.btn_new_file)

        explorer_layout.addLayout(header_layout)

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("fileList")
        self.list_widget.setIconSize(QSize(16, 16))
        self.list_widget.currentItemChanged.connect(self.load_file_to_editor)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        explorer_layout.addWidget(self.list_widget, 1)

        sidebar_layout.addWidget(self.explorer_panel)
        main_layout.addWidget(self.sidebar_container)

        self.work_area = QWidget()
        self.work_area.setObjectName("workArea")
        work_layout = QVBoxLayout(self.work_area)
        work_layout.setContentsMargins(0, 0, 0, 0)
        work_layout.setSpacing(0)

        self.work_stack = QStackedWidget()
        
        self.welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(self.welcome_widget)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_label = QLabel()
        welcome_logo_path = get_resource_path("welcome_logo.png")
        if os.path.exists(welcome_logo_path):
            pixmap = QPixmap(welcome_logo_path).scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        else:
            logo_label.setText("Логотип не найден")
            logo_label.setStyleSheet("color: #555555;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(logo_label)
        welcome_layout.addSpacing(20)

        title_welcome = QLabel("Добро пожаловать в PyManager")
        title_welcome.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title_welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_welcome.setObjectName("welcomeTitle")
        welcome_layout.addWidget(title_welcome)
        welcome_layout.addSpacing(10)

        subtitle_welcome = QLabel("Создайте проект или загрузите .py файл с компьютера")
        subtitle_welcome.setFont(QFont("Segoe UI", 13))
        subtitle_welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_welcome.setObjectName("welcomeSubtitle")
        welcome_layout.addWidget(subtitle_welcome)

        self.work_stack.addWidget(self.welcome_widget)

        self.right_splitter = QSplitter(Qt.Orientation.Vertical)
        self.right_splitter.setObjectName("rightSplitter")

        self.editor = QPlainTextEdit()
        self.editor.setObjectName("codeEditor")
        font = QFont("Consolas", self.font_size)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.editor.setFont(font)
        self.editor.setTabStopDistance(40)
        self.editor.setPlaceholderText("Начните писать здесь свой код на Python!")
        self.highlighter = PythonHighlighter(self.editor.document())
        self.right_splitter.addWidget(self.editor)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setObjectName("console")
        self.console.setFont(QFont("Consolas", 10))
        self.console.setPlaceholderText("Логи...")
        self.right_splitter.addWidget(self.console)

        self.right_splitter.setSizes([600, 200])
        self.work_stack.addWidget(self.right_splitter)

        work_layout.addWidget(self.work_stack)
        main_layout.addWidget(self.work_area, 1)

    def import_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите Python файл", "", "Python Files (*.py)")
        if file_path:
            file_path = str(Path(file_path).resolve()) 
            if file_path not in self.active_files:
                self.active_files.append(file_path)
                self.save_workspace()
                self.refresh_list()
                self.select_file_in_list(file_path)

    def create_new_file(self):
        dialog = NewFileDialog(self)
        geo = self.geometry()
        dialog.move(geo.center() - dialog.rect().center())
        
        if dialog.exec():
            proj_name = dialog.input.text().strip()
            if not proj_name: return
            
            proj_folder = self.project_dir / proj_name
            if proj_folder.exists():
                QMessageBox.warning(self, "Внимание", "Проект с таким именем уже существует!")
                return
                
            try:
                proj_folder.mkdir()
                file_path = proj_folder / f"{proj_name}.py"
                file_path.touch()
                
                self.active_files.append(str(file_path))
                self.save_workspace()
                self.refresh_list()
                self.select_file_in_list(str(file_path))
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось создать проект: {e}")

    def select_file_in_list(self, file_path):
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).data(Qt.ItemDataRole.UserRole) == file_path:
                self.list_widget.setCurrentRow(i)
                break

    def show_context_menu(self, pos: QPoint):
        item = self.list_widget.itemAt(pos)
        if not item or not item.data(Qt.ItemDataRole.UserRole): return
            
        menu = QMenu(self)
        self.style_menu(menu)
        
        action_rename = menu.addAction("Переименовать")
        action_remove = menu.addAction("Убрать из меню")
        action_delete = menu.addAction("Удалить с диска")
        
        action = menu.exec(self.list_widget.mapToGlobal(pos))
        file_path = item.data(Qt.ItemDataRole.UserRole)
        
        if action == action_rename:
            self.rename_file(file_path)
        elif action == action_remove:
            current_row = self.list_widget.currentRow()
            self.active_files.remove(file_path)
            self.save_workspace()
            self.refresh_list()
            
            if self.active_files:
                new_row = min(current_row, len(self.active_files) - 1)
                self.list_widget.setCurrentRow(new_row)
            else:
                self.work_stack.setCurrentIndex(0)
                
        elif action == action_delete:
            self.delete_file(file_path)

    def rename_file(self, old_path):
        old_name = Path(old_path).name
        dialog = RenameFileDialog(self, old_name)
        geo = self.geometry()
        dialog.move(geo.center() - dialog.rect().center())
        
        if dialog.exec():
            new_name = dialog.input.text().strip()
            if not new_name or new_name == old_name: return
            if not new_name.endswith(".py"): new_name += ".py"
            
            new_path = Path(old_path).parent / new_name
            
            try:
                os.rename(old_path, str(new_path))
                idx = self.active_files.index(old_path)
                self.active_files[idx] = str(new_path)
                self.save_workspace()
                
                if old_path in self.file_logs:
                    self.file_logs[str(new_path)] = self.file_logs.pop(old_path)
                if self.active_file_path == old_path:
                    self.active_file_path = str(new_path)
                    
                self.refresh_list()
                self.select_file_in_list(str(new_path))
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось переименовать: {e}")

    def delete_file(self, file_path):
        filename = Path(file_path).name
        dialog = DeleteFileDialog(self, filename, "удалить с диска")
        geo = self.geometry()
        dialog.move(geo.center() - dialog.rect().center())
        
        if dialog.exec():
            try:
                os.remove(file_path)
                current_row = self.list_widget.currentRow()
                if file_path in self.active_files:
                    self.active_files.remove(file_path)
                    self.save_workspace()
                if file_path in self.file_logs:
                    del self.file_logs[file_path]
                if self.active_file_path == file_path:
                    self.active_file_path = None
                self.refresh_list()
                
                if self.active_files:
                    new_row = min(current_row, len(self.active_files) - 1)
                    self.list_widget.setCurrentRow(new_row)
                else:
                    self.work_stack.setCurrentIndex(0)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить: {e}")

    def style_menu(self, menu):
        if self.current_theme == "dark":
            menu.setStyleSheet("""
                QMenu { background-color: #252526; color: #cccccc; border: 1px solid #333333; border-radius: 4px; padding: 5px; }
                QMenu::item { padding: 6px 20px; border-radius: 4px; }
                QMenu::item:selected { background-color: #37373d; color: white; }
            """)
        else:
            menu.setStyleSheet("""
                QMenu { background-color: #ececec; color: #333333; border: 1px solid #d4d4d4; border-radius: 4px; padding: 5px; }
                QMenu::item { padding: 6px 20px; border-radius: 4px; }
                QMenu::item:selected { background-color: #d6ebff; color: black; }
            """)

    def open_settings(self):
        dialog = SettingsDialog(self)
        geo = self.geometry()
        dialog.move(geo.center() - dialog.rect().center())
        dialog.exec()

    def toggle_theme(self, checked):
        self.current_theme = "dark" if checked else "light"
        self.highlighter.set_theme(self.current_theme)
        self.apply_styles()
        self.refresh_list()

    def change_font_size(self, value):
        self.font_size = value
        font = QFont("Consolas", self.font_size)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.editor.setFont(font)

    def load_file_to_editor(self, current, previous):
        if previous and previous.data(Qt.ItemDataRole.UserRole):
            prev_path = previous.data(Qt.ItemDataRole.UserRole)
            self.save_file_by_path(prev_path, silent=True)
            self.file_logs[prev_path] = self.console.toHtml()

        if not current or not current.data(Qt.ItemDataRole.UserRole):
            self.work_stack.setCurrentIndex(0) 
            self.active_file_path = None
            return
        
        self.work_stack.setCurrentIndex(1) 
        file_path = current.data(Qt.ItemDataRole.UserRole)
        self.active_file_path = file_path
        self.console.setHtml(self.file_logs.get(file_path, ""))

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.editor.setPlainText(f.read())
        except Exception as e:
            self.append_console(f"<span style='color:#f44747;'>Ошибка чтения: {e}</span>")

    def append_console(self, html_text):
        self.console.append(html_text)
        if self.active_file_path:
            self.file_logs[self.active_file_path] = self.console.toHtml()

    def save_file_by_path(self, file_path, silent=False):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            if not silent:
                self.append_console(f"<span style='color:#89d185;'>[СОХРАНЕНИЕ] Файл {Path(file_path).name} записан.</span>")
            return True
        except Exception as e:
            self.append_console(f"<span style='color:#f44747;'>[ОШИБКА] Не удалось сохранить: {e}</span>")
            return False

    def save_current_file(self):
        item = self.list_widget.currentItem()
        if not item or not item.data(Qt.ItemDataRole.UserRole): return False
        file_path = item.data(Qt.ItemDataRole.UserRole)
        return self.save_file_by_path(file_path, silent=False)

    def refresh_list(self):
        current_path = self.active_file_path
        self.list_widget.clear()
        
        icon_color = "#cccccc" if self.current_theme == "dark" else "#333333"
        file_icon = get_svg_icon(ICON_FILE, icon_color)

        if not self.active_files:
            item = QListWidgetItem("Файлов не найдено")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.list_widget.addItem(item)
            self.work_stack.setCurrentIndex(0)
            return

        for file_path in self.active_files:
            p = Path(file_path)
            display_name = p.name
                
            item = QListWidgetItem(f" {display_name}")
            item.setIcon(file_icon)
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            self.list_widget.addItem(item)
            
        if current_path:
            self.select_file_in_list(current_path)
        elif self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def run_script(self):
        item = self.list_widget.currentItem()
        if not item or not item.data(Qt.ItemDataRole.UserRole): return
        if self.auto_save_enabled: self.save_current_file() 
            
        file_path = item.data(Qt.ItemDataRole.UserRole)
        file_name = Path(file_path).name

        self.console.clear()
        if self.active_file_path: self.file_logs[self.active_file_path] = ""

        self.append_console(f"<br><span style='color:#007acc;'>========================================</span>")
        self.append_console(f"<span style='color:#007acc;'>ЗАПУСК: {file_name} [{datetime.now().strftime('%H:%M:%S')}]</span>")
        self.append_console(f"<span style='color:#007acc;'>========================================</span><br>")
        
        self.set_process_running(True)
        
        cmd_str = f'{self.custom_run_cmd} "{file_path}"'
        
        self.stdout_decoder.reset()
        self.stderr_decoder.reset()
        self.process.start(cmd_str)

    def stop_script(self):
        if self.process.state() == QProcess.ProcessState.Running:
            self.append_console(f"<br><span style='color:#e11d48;'>[ОСТАНОВКА] Процесс принудительно завершен.</span>")
            self.process.kill()

    def set_process_running(self, running):
        self.btn_run.setVisible(not running)
        self.btn_stop.setVisible(running)
        self.btn_compile.setEnabled(not running)
        self.btn_save.setEnabled(not running)
        self.btn_import.setEnabled(not running)
        self.btn_new_file.setEnabled(not running)

    def compile_script(self):
        item = self.list_widget.currentItem()
        if not item or not item.data(Qt.ItemDataRole.UserRole): return
        self.save_current_file()
        
        file_path = Path(item.data(Qt.ItemDataRole.UserRole))
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            compile(source_code, str(file_path), 'exec')
        except SyntaxError as e:
            self.console.clear()
            if self.active_file_path: self.file_logs[self.active_file_path] = ""
            self.append_console(f"<span style='color:#f44747;'>[ОШИБКА СИНТАКСИСА] Не удалось собрать проект.</span>")
            self.append_console(f"<span style='color:#f44747;'>Строка {e.lineno}, позиция {e.offset}: {e.msg}</span>")
            self.append_console(f"<span style='color:#f44747;'>{e.text.strip() if e.text else ''}</span>")
            return

        if self.project_dir not in file_path.parents:
            out_dir = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения .exe")
            if not out_dir: return
        else:
            out_dir = str(file_path.parent)

        method_dialog = CompileMethodDialog(self)
        
        while True:
            geo = self.geometry()
            method_dialog.move(geo.center() - method_dialog.rect().center())
            
            if not method_dialog.exec():
                return 
                
            if method_dialog.choice == "std":
                self.console.clear()
                if self.active_file_path: self.file_logs[self.active_file_path] = ""
                self.append_console(f"<br><span style='color:#d7ba7d;'>========================================</span>")
                self.append_console(f"<span style='color:#d7ba7d;'>СБОРКА (Стандарт): {file_path.name}</span>")
                self.append_console(f"<span style='color:#d7ba7d;'>Папка: {out_dir}</span>")
                self.append_console(f"<span style='color:#d7ba7d;'>========================================</span><br>")
                
                self.set_process_running(True)
                self.stdout_decoder.reset()
                self.stderr_decoder.reset()
                cmd_str = f'python -m PyInstaller --noconfirm --onefile --distpath "{out_dir}" "{file_path}"'
                self.process.start(cmd_str)
                break
                
            elif method_dialog.choice == "custom":
                cmd_dialog = CustomCompileDialog(self, self.last_custom_compile_cmd)
                cmd_dialog.move(geo.center() - cmd_dialog.rect().center())
                
                if cmd_dialog.exec():
                    cmd_template = cmd_dialog.input.text().strip()
                    self.last_custom_compile_cmd = cmd_template 
                    
                    cmd_str = f'{cmd_template} "{file_path}"'
                    
                    self.console.clear()
                    if self.active_file_path: self.file_logs[self.active_file_path] = ""
                    self.append_console(f"<br><span style='color:#d7ba7d;'>========================================</span>")
                    self.append_console(f"<span style='color:#d7ba7d;'>СБОРКА (Своя команда): {file_path.name}</span>")
                    self.append_console(f"<span style='color:#d7ba7d;'>Команда: {cmd_str}</span>")
                    self.append_console(f"<span style='color:#d7ba7d;'>========================================</span><br>")
                    
                    self.set_process_running(True)
                    self.stdout_decoder.reset()
                    self.stderr_decoder.reset()
                    self.process.start(cmd_str)
                    break
                else:
                    method_dialog = CompileMethodDialog(self)

    def handle_stdout(self):
        raw_data = self.process.readAllStandardOutput().data()
        text = self.stdout_decoder.decode(raw_data)
        if text:
            safe_text = html.escape(text).replace("\n", "<br>")
            self.append_console(safe_text)
            self.console.ensureCursorVisible()

    def handle_stderr(self):
        raw_data = self.process.readAllStandardError().data()
        text = self.stderr_decoder.decode(raw_data)
        if text:
            safe_text = html.escape(text).replace("\n", "<br>")
            self.append_console(f"<span style='color:#f44747;'>{safe_text}</span>")
            self.console.ensureCursorVisible()

    def process_finished(self, exit_code, exit_status):
        self.set_process_running(False)
        color = "#89d185" if exit_code == 0 else "#f44747"
        status = "УСПЕШНО" if exit_code == 0 else f"С ОШИБКОЙ (Код {exit_code})"
        self.append_console(f"<br><span style='color:{color};'>[ЗАВЕРШЕНО] Процесс {status}.</span>")

    def apply_styles(self):
        icon_color = "#cccccc" if self.current_theme == "dark" else "#333333"

        self.btn_run.setIcon(get_svg_icon(ICON_PLAY, icon_color))
        self.btn_stop.setIcon(get_svg_icon(ICON_STOP, "#e11d48"))
        self.btn_compile.setIcon(get_svg_icon(ICON_BOX, icon_color))
        self.btn_save.setIcon(get_svg_icon(ICON_SAVE, icon_color))
        self.btn_settings.setIcon(get_svg_icon(ICON_SETTINGS, icon_color))
        self.btn_new_file.setIcon(get_svg_icon(ICON_PLUS, icon_color))
        self.btn_import.setIcon(get_svg_icon(ICON_IMPORT, icon_color))

        if self.current_theme == "dark":
            bg_main, bg_sidebar, bg_activity = "#1e1e1e", "#252526", "#222222"
            border_color, text_color, text_placeholder = "#333333", "#cccccc", "#555555"
            hover_bg, selected_bg, editor_bg, pressed_bg = "#2a2d2e", "#37373d", "#1e1e1e", "#3e3e42"
            welcome_title, welcome_sub = "#cccccc", "#71717a"
            cursor_color = "#ffffff"
        else:
            bg_main, bg_sidebar, bg_activity = "#f3f3f3", "#ececec", "#e0e0e0"
            border_color, text_color, text_placeholder = "#d4d4d4", "#000000", "#999999"
            hover_bg, selected_bg, editor_bg, pressed_bg = "#e5e5e5", "#d6ebff", "#ffffff", "#cccccc"
            welcome_title, welcome_sub = "#333333", "#555555"
            cursor_color = "#000000"

        palette = self.editor.palette()
        palette.setColor(QPalette.ColorRole.Text, QColor(cursor_color))
        self.editor.setPalette(palette)

        style = f"""
        QMainWindow {{ background-color: {bg_main}; color: {text_color}; }}
        QFrame#sidebarContainer {{ background-color: {bg_sidebar}; border-radius: 8px; border: 1px solid {border_color}; }}
        QFrame#activityBar {{ background-color: {bg_activity}; border-top-left-radius: 8px; border-bottom-left-radius: 8px; border-right: 1px solid {border_color}; }}
        QFrame#explorerPanel {{ background-color: transparent; }}
        QLabel#panelTitle {{ color: {text_color}; padding-left: 5px; }}
        
        QToolButton#activityBtn {{ background-color: transparent; border: none; border-radius: 6px; padding: 8px; margin: 2px; }}
        QToolButton#activityBtn:hover {{ background-color: {hover_bg}; }}
        QToolButton#activityBtn:pressed {{ background-color: {pressed_bg}; }}
        QToolButton#explorerBtn {{ background-color: transparent; border: none; border-radius: 4px; padding: 4px; }}
        QToolButton#explorerBtn:hover {{ background-color: {hover_bg}; }}
        
        QListWidget#fileList {{ background-color: transparent; border: none; outline: none; font-size: 13px; color: {text_color}; }}
        QListWidget#fileList::item {{ padding: 8px; border-radius: 4px; margin-bottom: 2px; }}
        QListWidget#fileList::item:hover {{ background-color: {hover_bg}; }}
        QListWidget#fileList::item:selected {{ background-color: {selected_bg}; color: {"#ffffff" if self.current_theme == "dark" else "#000000"}; }}
        
        QWidget#workArea {{ background-color: {bg_main}; }}
        QLabel#welcomeTitle {{ color: {welcome_title}; }}
        QLabel#welcomeSubtitle {{ color: {welcome_sub}; }}
        
        QPlainTextEdit#codeEditor {{ 
            background-color: {editor_bg}; border: 1px solid {border_color}; border-radius: 8px; padding: 10px; 
            color: {text_color}; selection-background-color: #264f78; placeholder-text-color: {text_placeholder}; 
        }}
        QTextEdit#console {{ background-color: {editor_bg}; border: 1px solid {border_color}; border-radius: 8px; padding: 10px; color: {text_color}; selection-background-color: #264f78; placeholder-text-color: {text_placeholder}; }}
        
        QSplitter::handle {{ background-color: transparent; }}
        QSplitter::handle:vertical {{ height: 10px; }}
        
        QScrollBar:vertical {{ border: none; background: {bg_main}; width: 12px; margin: 0px; }}
        QScrollBar::handle:vertical {{ background: {border_color}; min-height: 20px; border-radius: 6px; }}
        QScrollBar::handle:vertical:hover {{ background: {text_placeholder}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ border: none; background: none; height: 0px; }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}

        QScrollBar:horizontal {{ border: none; background: {bg_main}; height: 12px; margin: 0px; }}
        QScrollBar::handle:horizontal {{ background: {border_color}; min-width: 20px; border-radius: 6px; }}
        QScrollBar::handle:horizontal:hover {{ background: {text_placeholder}; }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ border: none; background: none; width: 0px; }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: none; }}

        QPushButton:disabled {{ background-color: {border_color}; color: {text_placeholder}; }}
        """
        self.setStyleSheet(style)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = PythonManager()
    window.show()
    sys.exit(app.exec())