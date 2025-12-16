"""
Виджет для моделирования случайного блуждания
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QDoubleSpinBox, QSpinBox, QMessageBox,
                            QFileDialog, QGroupBox, QTableWidget, QTableWidgetItem,
                            QHeaderView, QSplitter)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QElapsedTimer
from PyQt6.QtGui import QFont
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from ..core.discrete_random_variable import DiscreteRandomVariable
from ..core.random_walk import RandomWalkSimulator
from ..io.serialization import DRVSerializer


class RandomWalkWidget(QWidget):
    """Виджет для моделирования случайного блуждания"""
    
    # Сигнал о загрузке распределения (для синхронизации с редактором)
    distribution_loaded = pyqtSignal(object, str)  # drv, filepath
    
    def __init__(self):
        super().__init__()
        self.step_distribution = None
        self.is_running = False
        self.current_step = 0
        self.total_steps = 0
        self.positions = []
        self.steps = []  # Храним шаги для плавной анимации
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.step_elapsed_timer = QElapsedTimer()  # Таймер для измерения времени шага
        self.animation_update_timer = QTimer()
        self.animation_update_timer.timeout.connect(self.update_animation_frame)
        self.animation_update_timer.setInterval(50)  # Обновление каждые 50 мс для плавности
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Увеличенные шрифты
        label_font = QFont()
        label_font.setPointSize(11)
        
        input_font = QFont()
        input_font.setPointSize(10)
        
        button_font = QFont()
        button_font.setPointSize(11)
        
        # Панель параметров
        params_group = QGroupBox("Параметры моделирования")
        params_group.setFont(label_font)
        params_layout = QVBoxLayout()
        params_layout.setSpacing(10)
        
        # Начальное положение
        initial_pos_layout = QHBoxLayout()
        initial_pos_layout.setSpacing(10)
        initial_label = QLabel("Начальное положение:")
        initial_label.setFont(label_font)
        initial_pos_layout.addWidget(initial_label)
        self.initial_pos_input = QDoubleSpinBox()
        self.initial_pos_input.setRange(-10000, 10000)
        self.initial_pos_input.setValue(0.0)
        self.initial_pos_input.setDecimals(2)
        self.initial_pos_input.setFont(input_font)
        initial_pos_layout.addWidget(self.initial_pos_input)
        params_layout.addLayout(initial_pos_layout)
        
        # Количество шагов
        steps_layout = QHBoxLayout()
        steps_layout.setSpacing(10)
        steps_label = QLabel("Количество шагов:")
        steps_label.setFont(label_font)
        steps_layout.addWidget(steps_label)
        self.steps_input = QSpinBox()
        self.steps_input.setRange(1, 1000)
        self.steps_input.setValue(10)
        self.steps_input.setFont(input_font)
        steps_layout.addWidget(self.steps_input)
        params_layout.addLayout(steps_layout)
        
        # Закон перемещения
        distribution_layout = QVBoxLayout()
        distribution_layout.setSpacing(8)
        dist_label = QLabel("Закон перемещения:")
        dist_label.setFont(label_font)
        distribution_layout.addWidget(dist_label)
        
        distribution_info_layout = QHBoxLayout()
        self.distribution_label = QLabel("Не задан")
        self.distribution_label.setFont(label_font)
        distribution_info_layout.addWidget(self.distribution_label)
        distribution_info_layout.addStretch()
        params_layout.addLayout(distribution_info_layout)
        
        self.load_distribution_btn = QPushButton("📂 Загрузить из файла")
        self.load_distribution_btn.setMinimumHeight(45)
        self.load_distribution_btn.setFont(button_font)
        self.load_distribution_btn.clicked.connect(self.load_distribution)
        distribution_layout.addWidget(self.load_distribution_btn)
        params_layout.addLayout(distribution_layout)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Панель управления - делаем кнопки больше и удобнее
        control_layout = QHBoxLayout()
        control_layout.setSpacing(12)
        
        self.start_btn = QPushButton("▶️ Запустить")
        self.start_btn.setMinimumHeight(55)
        self.start_btn.setMinimumWidth(160)
        self.start_btn.setFont(button_font)
        self.start_btn.clicked.connect(self.start_simulation)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏸️ Остановить")
        self.stop_btn.setMinimumHeight(55)
        self.stop_btn.setMinimumWidth(160)
        self.stop_btn.setFont(button_font)
        self.stop_btn.clicked.connect(self.stop_simulation)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        self.reset_btn = QPushButton("🔄 Сброс")
        self.reset_btn.setMinimumHeight(55)
        self.reset_btn.setMinimumWidth(160)
        self.reset_btn.setFont(button_font)
        self.reset_btn.clicked.connect(self.reset_simulation)
        control_layout.addWidget(self.reset_btn)
        
        layout.addLayout(control_layout)
        
        # Разделитель для анимации и результатов
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель - анимация
        animation_widget = QWidget()
        animation_layout = QVBoxLayout()
        animation_layout.setSpacing(8)
        animation_layout.setContentsMargins(5, 5, 5, 5)
        
        animation_label = QLabel("Анимация перемещения:")
        animation_label.setFont(label_font)
        animation_layout.addWidget(animation_label)
        
        # График для анимации
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        
        # График траектории
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel("Время (шаг)", fontsize=11)
        self.ax.set_ylabel("Позиция", fontsize=11)
        self.ax.set_title("Случайное блуждание", fontsize=12, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        
        # Настраиваем отступы, чтобы график не залезал под интерфейс
        self.figure.tight_layout(pad=3.0, rect=[0.05, 0.05, 0.95, 0.95])
        
        animation_layout.addWidget(self.canvas)
        
        animation_widget.setLayout(animation_layout)
        splitter.addWidget(animation_widget)
        
        # Правая панель - результаты
        results_widget = QWidget()
        results_layout = QVBoxLayout()
        results_layout.setSpacing(8)
        results_layout.setContentsMargins(5, 5, 5, 5)
        results_label = QLabel("Распределение конечных позиций:")
        results_label.setFont(label_font)
        results_layout.addWidget(results_label)
        
        # Пояснение
        info_label = QLabel("Значения показывают координаты точки в одномерном пространстве ℝ.\n"
                           "Каждое значение - это возможная конечная позиция точки после n шагов.\n"
                           "Вероятность показывает, с какой вероятностью точка окажется в этой позиции.")
        info_label.setWordWrap(True)
        info_font = QFont()
        info_font.setPointSize(9)
        info_label.setFont(info_font)
        info_label.setStyleSheet("color: gray;")
        results_layout.addWidget(info_label)
        
        # Таблица результатов
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(['Конечная позиция', 'Вероятность'])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.setFont(input_font)
        results_layout.addWidget(self.results_table)
        
        results_widget.setLayout(results_layout)
        splitter.addWidget(results_widget)
        
        splitter.setSizes([600, 400])
        layout.addWidget(splitter)
        
        self.setLayout(layout)
    
    def load_distribution(self):
        """Загрузка закона перемещения из файла"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Загрузить закон перемещения", "", "JSON Files (*.json)"
        )
        
        if filepath:
            try:
                drv = DRVSerializer.load_from_file(filepath)
                self.set_distribution(drv)
                # Сигнализируем главному окну о загрузке
                if hasattr(self, 'distribution_loaded'):
                    self.distribution_loaded.emit(drv, filepath)
                QMessageBox.information(self, "Успех", "Закон перемещения загружен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {e}")
    
    def set_distribution(self, drv: DiscreteRandomVariable):
        """Установка закона перемещения"""
        self.step_distribution = drv
        if drv and hasattr(drv, 'values') and drv.values:
            self.distribution_label.setText(f"Загружен: {len(drv.values)} значений")
        else:
            self.distribution_label.setText("Не задан")
            self.step_distribution = None
    
    def start_simulation(self):
        """Запуск моделирования"""
        if self.step_distribution is None:
            QMessageBox.warning(self, "Предупреждение", "Сначала загрузите закон перемещения")
            return
        
        if not self.step_distribution.values:
            QMessageBox.warning(self, "Предупреждение", "Закон перемещения пуст")
            return
        
        self.total_steps = self.steps_input.value()
        initial_position = self.initial_pos_input.value()
        
        # Генерируем последовательность шагов
        self.positions = [initial_position]
        self.steps = []
        current_position = initial_position
        
        for _ in range(self.total_steps):
            step = self.step_distribution.sample()
            self.steps.append(step)
            current_position += step
            self.positions.append(current_position)
        
        # Вычисляем распределение конечных позиций
        final_distribution = RandomWalkSimulator.compute_final_positions_distribution(
            initial_position, self.step_distribution, self.total_steps
        )
        
        # Отображаем результаты
        self.display_results(final_distribution)
        
        # Запускаем анимацию
        self.is_running = True
        self.current_step = 0
        self.step_elapsed_timer.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Настраиваем график
        self.ax.clear()
        self.ax.set_xlabel("Время (шаг)", fontsize=11)
        self.ax.set_ylabel("Позиция", fontsize=11)
        self.ax.set_title("Случайное блуждание", fontsize=12, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        self.figure.tight_layout(pad=3.0, rect=[0.05, 0.05, 0.95, 0.95])
        
        # Устанавливаем границы графика
        if self.positions:
            margin = (max(self.positions) - min(self.positions)) * 0.1 if max(self.positions) != min(self.positions) else 1
            self.ax.set_xlim(-0.5, self.total_steps + 0.5)
            self.ax.set_ylim(min(self.positions) - margin, max(self.positions) + margin)
        
        # Запускаем таймер для перехода к следующему шагу
        self.animation_timer.start(1000)
        self.animation_update_timer.start()
        self.update_animation_frame()
    
    def stop_simulation(self):
        """Остановка моделирования"""
        self.is_running = False
        self.animation_timer.stop()
        self.animation_update_timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def reset_simulation(self):
        """Сброс моделирования"""
        self.stop_simulation()
        self.current_step = 0
        self.positions = []
        self.steps = []
        self.ax.clear()
        self.ax.set_xlabel("Время (шаг)", fontsize=11)
        self.ax.set_ylabel("Позиция", fontsize=11)
        self.ax.set_title("Случайное блуждание", fontsize=12, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        self.figure.tight_layout(pad=3.0, rect=[0.05, 0.05, 0.95, 0.95])
        self.canvas.draw()
        self.results_table.setRowCount(0)
    
    def update_animation(self):
        """Переход к следующему шагу (вызывается каждую секунду)"""
        if not self.is_running:
            return
        
        if self.current_step >= len(self.steps):
            self.stop_simulation()
            return
        
        self.current_step += 1
        self.step_elapsed_timer.restart()
    
    def update_animation_frame(self):
        """Плавное обновление кадра анимации"""
        if not self.is_running:
            return
        
        if self.current_step > len(self.steps):
            return
        
        # Вычисляем текущую позицию с учетом плавного перемещения
        elapsed_ms = self.step_elapsed_timer.elapsed()
        
        # Позиция после завершенных шагов
        completed_steps = min(self.current_step, len(self.steps))
        base_position = self.positions[completed_steps] if completed_steps < len(self.positions) else self.positions[-1]
        
        # Если есть текущий шаг, вычисляем промежуточную позицию
        current_position = base_position
        if self.current_step < len(self.steps) and elapsed_ms < 1000:
            progress = min(elapsed_ms / 1000.0, 1.0)
            step = self.steps[self.current_step]
            start_pos = self.positions[self.current_step]
            end_pos = self.positions[self.current_step + 1]
            current_position = start_pos + (end_pos - start_pos) * progress

        self.ax.clear()
        
        # Настройка графика
        self.ax.set_xlabel("Время (шаг)", fontsize=11)
        self.ax.set_ylabel("Позиция", fontsize=11)
        
        if self.current_step <= len(self.steps):
            step_num = self.current_step if self.current_step < len(self.steps) else len(self.steps)
            self.ax.set_title(f"Случайное блуждание (шаг {step_num}/{self.total_steps})", 
                            fontsize=12, fontweight='bold')
        else:
            self.ax.set_title(f"Случайное блуждание (завершено)", 
                            fontsize=12, fontweight='bold')
        
        self.ax.grid(True, alpha=0.3)
        
        if self.positions:
            margin = (max(self.positions) - min(self.positions)) * 0.1 if max(self.positions) != min(self.positions) else 1
            self.ax.set_xlim(-0.5, self.total_steps + 0.5)
            self.ax.set_ylim(min(self.positions) - margin, max(self.positions) + margin)
        
        # Вычисляем текущую позицию по X (время) с учетом прогресса
        current_time_x = None
        if self.current_step < len(self.steps):
            elapsed_ms = self.step_elapsed_timer.elapsed()
            progress = min(elapsed_ms / 1000.0, 1.0) if elapsed_ms < 1000 else 1.0
            current_time_x = self.current_step + progress
        
        # Рисуем полный путь до текущей позиции
        # Собираем все точки: завершенные позиции + текущая позиция
        all_steps = []
        all_positions = []
        
        # Добавляем завершенные позиции
        if self.current_step > 0:
            completed_steps = list(range(self.current_step + 1))
            completed_positions = self.positions[:self.current_step + 1]
            all_steps.extend(completed_steps)
            all_positions.extend(completed_positions)
        
        # Добавляем текущую позицию
        if self.current_step < len(self.steps) and current_time_x is not None:
            all_steps.append(current_time_x)
            all_positions.append(current_position)
        elif self.current_step == len(self.steps):
            all_steps = list(range(len(self.positions)))
            all_positions = self.positions
        
        # Рисуем линию, если есть хотя бы 2 точки
        if len(all_steps) > 1:
            self.ax.plot(all_steps, all_positions, 'b-', linewidth=2, alpha=0.7)
        
        # Рисуем текущую точку (на той же позиции, где заканчивается линия)
        if self.current_step < len(self.steps) and current_time_x is not None:
            self.ax.plot(current_time_x, current_position, 'ro', markersize=10, label='Текущая позиция')
        elif self.current_step == len(self.steps) and len(self.positions) > 0:
            # Рисуем полный путь, если анимация завершена
            all_steps = list(range(len(self.positions)))
            self.ax.plot(all_steps, self.positions, 'b-', linewidth=2, alpha=0.7)
            self.ax.plot(len(self.positions) - 1, self.positions[-1], 'ro', markersize=10, label='Финальная позиция')
        
        # Рисуем начальную точку
        if len(self.positions) > 0:
            self.ax.plot(0, self.positions[0], 'go', markersize=10, label='Начальная позиция')
        
        self.ax.legend(fontsize=10)
        # Применяем tight_layout после всех изменений
        self.figure.tight_layout(pad=3.0, rect=[0.05, 0.05, 0.95, 0.95])
        self.canvas.draw()
    
    def display_results(self, distribution: DiscreteRandomVariable):
        """Отображение результатов в таблице"""
        pmf = distribution.get_pmf()
        self.results_table.setRowCount(len(pmf))
        
        # Сортируем по позиции
        sorted_pmf = sorted(pmf, key=lambda x: x[0])
        
        for row, (value, prob) in enumerate(sorted_pmf):
            self.results_table.setItem(row, 0, QTableWidgetItem(f"{value:.4f}"))
            self.results_table.setItem(row, 1, QTableWidgetItem(f"{prob:.6f}"))

