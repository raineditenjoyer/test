from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QSlider, QComboBox, QCheckBox, QTabWidget, QWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
                             QRadioButton, QButtonGroup, QSpinBox, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
import datetime

class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Настройки")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Вкладки
        tabs = QTabWidget()
        
        # Звук
        sound_tab = QWidget()
        sound_layout = QVBoxLayout()
        
        sound_enabled = QCheckBox("Звуковые эффекты")
        sound_enabled.setChecked(self.settings.sound_enabled)
        sound_enabled.stateChanged.connect(lambda state: setattr(self.settings, 'sound_enabled', bool(state)))
        
        music_enabled = QCheckBox("Фоновая музыка")
        music_enabled.setChecked(self.settings.music_enabled)
        music_enabled.stateChanged.connect(lambda state: setattr(self.settings, 'music_enabled', bool(state)))
        
        sound_volume = QSlider(Qt.Horizontal)
        sound_volume.setRange(0, 100)
        sound_volume.setValue(int(self.settings.sound_volume * 100))
        sound_volume.valueChanged.connect(lambda value: setattr(self.settings, 'sound_volume', value / 100))
        
        music_volume = QSlider(Qt.Horizontal)
        music_volume.setRange(0, 100)
        music_volume.setValue(int(self.settings.music_volume * 100))
        music_volume.valueChanged.connect(lambda value: setattr(self.settings, 'music_volume', value / 100))
        
        sound_layout.addWidget(sound_enabled)
        sound_layout.addWidget(QLabel("Громкость звуков:"))
        sound_layout.addWidget(sound_volume)
        sound_layout.addWidget(music_enabled)
        sound_layout.addWidget(QLabel("Громкость музыки:"))
        sound_layout.addWidget(music_volume)
        sound_layout.addStretch()
        
        sound_tab.setLayout(sound_layout)
        tabs.addTab(sound_tab, "Звук")
        
        # Графика
        graphics_tab = QWidget()
        graphics_layout = QVBoxLayout()
        
        effects = QCheckBox("Визуальные эффекты")
        effects.setChecked(self.settings.effects_enabled)
        effects.stateChanged.connect(lambda state: setattr(self.settings, 'effects_enabled', bool(state)))
        
        particles = QCheckBox("Частицы")
        particles.setChecked(self.settings.particles_enabled)
        particles.stateChanged.connect(lambda state: setattr(self.settings, 'particles_enabled', bool(state)))
        
        quality_group = QGroupBox("Качество фона")
        quality_layout = QVBoxLayout()
        
        quality_buttons = QButtonGroup()
        qualities = ["Низкое", "Среднее", "Высокое"]
        
        for i, quality in enumerate(qualities):
            radio = QRadioButton(quality)
            radio.setChecked(i == self.settings.background_quality)
            quality_buttons.addButton(radio, i)
            quality_layout.addWidget(radio)
            
        quality_buttons.buttonClicked[int].connect(lambda i: setattr(self.settings, 'background_quality', i))
        
        quality_group.setLayout(quality_layout)
        
        graphics_layout.addWidget(effects)
        graphics_layout.addWidget(particles)
        graphics_layout.addWidget(quality_group)
        graphics_layout.addStretch()
        
        graphics_tab.setLayout(graphics_layout)
        tabs.addTab(graphics_tab, "Графика")
        
        # Управление
        controls_tab = QWidget()
        controls_layout = QVBoxLayout()
        
        # TODO: Добавить настройку клавиш управления
        controls_layout.addWidget(QLabel("Настройка управления будет добавлена позже"))
        controls_layout.addStretch()
        
        controls_tab.setLayout(controls_layout)
        tabs.addTab(controls_tab, "Управление")
        
        layout.addWidget(tabs)
        
        # Кнопки
        buttons = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)
        
        buttons.addStretch()
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        
        layout.addLayout(buttons)
        
        self.setLayout(layout)

class StatisticsDialog(QDialog):
    def __init__(self, stats_manager, parent=None):
        super().__init__(parent)
        self.stats_manager = stats_manager
        self.setWindowTitle("Статистика")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Таблица статистики
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Дата", "Счёт", "Волна", "Сложность",
            "Время", "Убито врагов", "Точность"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        
        layout.addWidget(self.table)
        
        # Кнопка закрытия
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        
        layout.addWidget(close_button)
        
        self.setLayout(layout)
        self.update_statistics()
        
    def update_statistics(self):
        stats = self.stats_manager.get_statistics()
        self.table.setRowCount(len(stats))
        
        for i, stat in enumerate(stats):
            date = datetime.datetime.fromisoformat(stat['date']).strftime("%Y-%m-%d %H:%M")
            self.table.setItem(i, 0, QTableWidgetItem(date))
            self.table.setItem(i, 1, QTableWidgetItem(str(stat['score'])))
            self.table.setItem(i, 2, QTableWidgetItem(str(stat['level'])))
            self.table.setItem(i, 3, QTableWidgetItem(stat['difficulty']))
            self.table.setItem(i, 4, QTableWidgetItem(f"{stat['duration']} сек"))
            self.table.setItem(i, 5, QTableWidgetItem(str(stat['enemies_killed'])))
            self.table.setItem(i, 6, QTableWidgetItem(f"{stat['accuracy']:.1f}%"))