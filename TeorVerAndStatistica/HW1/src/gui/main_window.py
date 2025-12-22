import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QMessageBox, QFileDialog,
                            QSplitter, QTabWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from .variable_editor import VariableEditor
from .plot_widget import PlotWidget
from .random_walk_widget import RandomWalkWidget
from ..core.discrete_random_variable import DiscreteRandomVariable
from ..core.statistics import StatisticsCalculator
from ..io.serialization import DRVSerializer


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Дискретные случайные величины")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        # Создаем вкладки
        self.tabs = QTabWidget()
        
        # === ВКЛАДКА 1: Работа с дискретными случайными величинами ===
        drv_widget = QWidget()
        drv_layout = QHBoxLayout()
        
        # Левая панель - редактор
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Редактор переменной
        self.editor = VariableEditor()
        left_layout.addWidget(self.editor)
        
        # Панель операций - делаем кнопки больше и удобнее
        operations_layout = QVBoxLayout()
        operations_layout.setSpacing(12)
        
        button_font = QFont()
        button_font.setPointSize(11)
        
        self.load_btn = QPushButton("📂 Загрузить из файла")
        self.load_btn.setMinimumHeight(50)
        self.load_btn.setFont(button_font)
        self.load_btn.clicked.connect(self.load_variable)
        operations_layout.addWidget(self.load_btn)
        
        self.save_btn = QPushButton("💾 Сохранить в файл")
        self.save_btn.setMinimumHeight(50)
        self.save_btn.setFont(button_font)
        self.save_btn.clicked.connect(self.save_variable)
        operations_layout.addWidget(self.save_btn)
        
        self.stats_btn = QPushButton("📊 Показать статистику")
        self.stats_btn.setMinimumHeight(50)
        self.stats_btn.setFont(button_font)
        self.stats_btn.clicked.connect(self.show_statistics)
        operations_layout.addWidget(self.stats_btn)
        
        left_layout.addLayout(operations_layout)
        
        left_panel.setLayout(left_layout)
        
        # Правая панель - графики
        self.plot_widget = PlotWidget()
        
        # Разделитель
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(self.plot_widget)
        splitter.setSizes([500, 900])
        
        drv_layout.addWidget(splitter)
        drv_widget.setLayout(drv_layout)
        
        # === ВКЛАДКА 2: Случайное блуждание ===
        self.random_walk_widget = RandomWalkWidget()
        
        # Добавляем вкладки
        self.tabs.addTab(drv_widget, "Дискретные случайные величины")
        self.tabs.addTab(self.random_walk_widget, "Случайное блуждание")
        
        main_layout.addWidget(self.tabs)
        central_widget.setLayout(main_layout)
        
        # Меню
        self.create_menu()
        
        # Обновляем графики при изменении переменной
        # Подключаем сигнал от редактора об изменении переменной
        self.editor.variable_changed.connect(self.on_variable_changed)
        # Также подключаем сигнал изменения ячеек таблицы (для ручного редактирования)
        self.editor.table.itemChanged.connect(self.on_variable_changed)
        
        # Синхронизация данных между вкладками
        # Когда изменяется переменная в редакторе, обновляем в случайном блуждании
        self.editor.variable_changed.connect(self.sync_to_random_walk)
        # Когда загружается файл в случайном блуждании, обновляем редактор
        self.random_walk_widget.distribution_loaded.connect(self.sync_from_random_walk)
    
    def create_menu(self):
        menubar = self.menuBar()
        
        # Меню Файл
        file_menu = menubar.addMenu('Файл')
        
        new_action = file_menu.addAction('Новая')
        new_action.triggered.connect(self.new_variable)
        
        load_action = file_menu.addAction('Загрузить')
        load_action.triggered.connect(self.load_variable)
        
        save_action = file_menu.addAction('Сохранить')
        save_action.triggered.connect(self.save_variable)
        
        save_as_action = file_menu.addAction('Сохранить как')
        save_as_action.triggered.connect(self.save_variable_as)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction('Выход')
        exit_action.triggered.connect(self.close)
        
        # Меню Операции
        ops_menu = menubar.addMenu('Операции')
        
        stats_action = ops_menu.addAction('Статистика')
        stats_action.triggered.connect(self.show_statistics)
        
        random_walk_action = ops_menu.addAction('Случайное блуждание')
        random_walk_action.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
    
    def on_variable_changed(self):
        """Обновление графиков при изменении переменной"""
        try:
            drv = self.editor.get_variable()
            if drv.values:
                self.plot_widget.plot_variable(drv)
        except Exception as e:
            print(f"Ошибка при обновлении графиков: {e}")
    
    def new_variable(self):
        """Создание новой переменной"""
        new_drv = DiscreteRandomVariable()
        self.editor.set_variable(new_drv)
        self.current_file = None
        self.setWindowTitle("Дискретные случайные величины - Новая")
        # Синхронизируем с случайным блужданием
        self.random_walk_widget.set_distribution(new_drv)
    
    def load_variable(self):
        """Загрузка переменной из файла"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Загрузить переменную", "", "JSON Files (*.json)"
        )
        
        if filepath:
            try:
                drv = DRVSerializer.load_from_file(filepath)
                self.editor.set_variable(drv)
                self.current_file = filepath
                self.setWindowTitle(f"Дискретные случайные величины - {os.path.basename(filepath)}")
                # Графики обновятся автоматически через сигнал variable_changed
                # Синхронизируем с случайным блужданием
                self.random_walk_widget.set_distribution(drv)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {e}")
    
    def save_variable(self):
        """Сохранение переменной"""
        if self.current_file:
            try:
                drv = self.editor.get_variable()
                DRVSerializer.save_to_file(drv, self.current_file)
                QMessageBox.information(self, "Успех", "Файл сохранен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {e}")
        else:
            self.save_variable_as()
    
    def save_variable_as(self):
        """Сохранение переменной как..."""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Сохранить переменную", "", "JSON Files (*.json)"
        )
        
        if filepath:
            try:
                drv = self.editor.get_variable()
                DRVSerializer.save_to_file(drv, filepath)
                self.current_file = filepath
                self.setWindowTitle(f"Дискретные случайные величины - {os.path.basename(filepath)}")
                QMessageBox.information(self, "Успех", "Файл сохранен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {e}")
    
    def show_statistics(self):
        """Показать статистические характеристики"""
        try:
            drv = self.editor.get_variable()
            if not drv.values:
                QMessageBox.warning(self, "Предупреждение", "Добавьте значения для расчета статистики")
                return
            
            stats = StatisticsCalculator.get_all_statistics(drv)
            
            stats_text = f"""
            Статистические характеристики:
            
            Математическое ожидание: {stats['expectation']:.4f}
            Дисперсия: {stats['variance']:.4f}
            Стандартное отклонение: {stats['standard_deviation']:.4f}
            Коэффициент асимметрии: {stats['skewness']:.4f}
            Коэффициент эксцесса: {stats['kurtosis']:.4f}
            """
            
            QMessageBox.information(self, "Статистика", stats_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось рассчитать статистику: {e}")
    
    def sync_to_random_walk(self):
        """Синхронизация данных из редактора в случайное блуждание"""
        try:
            drv = self.editor.get_variable()
            if drv and drv.values:
                self.random_walk_widget.set_distribution(drv)
        except Exception as e:
            print(f"Ошибка синхронизации в случайное блуждание: {e}")
    
    def sync_from_random_walk(self, drv: DiscreteRandomVariable, filepath: str):
        """Синхронизация данных из случайного блуждания в редактор"""
        try:
            self.editor.set_variable(drv)
            self.current_file = filepath
            self.setWindowTitle(f"Дискретные случайные величины - {os.path.basename(filepath)}")
        except Exception as e:
            print(f"Ошибка синхронизации в редактор: {e}")