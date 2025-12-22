from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QPushButton, QLabel,
                            QMessageBox, QHeaderView, QDoubleSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from ..core.discrete_random_variable import DiscreteRandomVariable


class VariableEditor(QWidget):
    """Редактор дискретной случайной величины"""
    
    # Сигнал об изменении переменной
    variable_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.drv = DiscreteRandomVariable()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Увеличенный шрифт для меток
        label_font = QFont()
        label_font.setPointSize(11)
        
        # Таблица значений
        table_label = QLabel("Таблица распределения:")
        table_label.setFont(label_font)
        layout.addWidget(table_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['Значение', 'Вероятность'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Увеличиваем шрифт в таблице
        table_font = QFont()
        table_font.setPointSize(10)
        self.table.setFont(table_font)
        layout.addWidget(self.table)
        
        # Панель добавления значений
        input_group = QVBoxLayout()
        input_group.setSpacing(8)
        
        # Ввод значений
        input_row = QHBoxLayout()
        input_row.setSpacing(10)
        
        value_label = QLabel("Значение:")
        value_label.setFont(label_font)
        input_row.addWidget(value_label)
        
        self.value_input = QDoubleSpinBox()
        self.value_input.setRange(-1000000, 1000000)
        self.value_input.setDecimals(4)
        input_font = QFont()
        input_font.setPointSize(10)
        self.value_input.setFont(input_font)
        input_row.addWidget(self.value_input)
        
        prob_label = QLabel("Вероятность:")
        prob_label.setFont(label_font)
        input_row.addWidget(prob_label)
        
        self.prob_input = QDoubleSpinBox()
        self.prob_input.setRange(0, 1)
        self.prob_input.setSingleStep(0.01)
        self.prob_input.setDecimals(4)
        self.prob_input.setFont(input_font)
        input_row.addWidget(self.prob_input)
        input_group.addLayout(input_row)
        
        # Кнопки управления - делаем их больше и удобнее
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(10)
        
        button_font = QFont()
        button_font.setPointSize(11)
        
        self.add_btn = QPushButton("➕ Добавить")
        self.add_btn.setMinimumHeight(45)
        self.add_btn.setFont(button_font)
        self.add_btn.clicked.connect(self.add_value)
        buttons_row.addWidget(self.add_btn)
        
        self.delete_btn = QPushButton("➖ Удалить выделенное")
        self.delete_btn.setMinimumHeight(45)
        self.delete_btn.setFont(button_font)
        self.delete_btn.clicked.connect(self.delete_value)
        buttons_row.addWidget(self.delete_btn)
        
        self.clear_all_btn = QPushButton("🗑️ Очистить все")
        self.clear_all_btn.setMinimumHeight(45)
        self.clear_all_btn.setFont(button_font)
        self.clear_all_btn.clicked.connect(self.clear_all)
        buttons_row.addWidget(self.clear_all_btn)
        
        input_group.addLayout(buttons_row)
        layout.addLayout(input_group)
        
        # Информация
        self.info_label = QLabel("Добавьте значения и вероятности")
        info_font = QFont()
        info_font.setPointSize(10)
        self.info_label.setFont(info_font)
        layout.addWidget(self.info_label)
        
        self.setLayout(layout)
        
        # Подключаем обработчик изменений в таблице
        self.table.itemChanged.connect(self.on_table_item_changed)
        
        self.update_info()
    
    def add_value(self):
        value = self.value_input.value()
        prob = self.prob_input.value()
        
        try:
            self.drv.add_value(value, prob)
            self.update_table()
            self.update_info()
            # Отправляем сигнал об изменении переменной
            self.variable_changed.emit()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
    
    def delete_value(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            # Блокируем сигналы, чтобы избежать двойной обработки
            self.table.blockSignals(True)
            self.table.removeRow(current_row)
            self.table.blockSignals(False)
            self.recreate_from_table()
        else:
            QMessageBox.information(self, "Информация", "Выберите строку для удаления")
    
    def clear_all(self):
        """Удаление всех данных"""
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "Информация", "Таблица уже пуста")
            return
        
        # Подтверждение удаления
        reply = QMessageBox.question(
            self, 
            "Подтверждение", 
            "Вы уверены, что хотите удалить все данные?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Блокируем сигналы
            self.table.blockSignals(True)
            self.table.setRowCount(0)
            self.table.blockSignals(False)
            
            # Создаем пустую переменную
            self.drv = DiscreteRandomVariable()
            self.update_info()
            # Отправляем сигнал об изменении переменной
            self.variable_changed.emit()
    
    def on_table_item_changed(self, item):
        """Обработка изменений в таблице вручную"""
        if item is None:
            return
        
        # Блокируем сигналы, чтобы избежать рекурсии
        self.table.blockSignals(True)
        try:
            self.recreate_from_table()
        finally:
            self.table.blockSignals(False)
    
    def recreate_from_table(self):
        """Пересоздание DRV из данных таблицы"""
        values_probs = []
        for row in range(self.table.rowCount()):
            value_item = self.table.item(row, 0)
            prob_item = self.table.item(row, 1)
            if value_item and prob_item:
                try:
                    value_str = value_item.text().strip()
                    prob_str = prob_item.text().strip()
                    
                    if not value_str or not prob_str:
                        continue
                    
                    value = float(value_str)
                    prob = float(prob_str)
                    
                    if prob < 0:
                        QMessageBox.warning(self, "Ошибка", 
                                          f"Вероятность в строке {row + 1} не может быть отрицательной")
                        # Восстанавливаем предыдущее состояние
                        self.update_table()
                        return
                    
                    values_probs.append((value, prob))
                except ValueError:
                    QMessageBox.warning(self, "Ошибка", 
                                      f"Неверный формат данных в строке {row + 1}")
                    # Восстанавливаем предыдущее состояние
                    self.update_table()
                    return
        
        # Если нет значений, создаем пустой DRV
        if not values_probs:
            self.drv = DiscreteRandomVariable()
            self.update_info()
            return
        
        # Нормализуем вероятности перед созданием DRV
        total_prob = sum(prob for _, prob in values_probs)
        if total_prob <= 0:
            QMessageBox.warning(self, "Ошибка", 
                              "Сумма вероятностей должна быть больше нуля")
            self.update_table()
            return
        
        normalized_values_probs = [(value, prob / total_prob) for value, prob in values_probs]
        
        try:
            old_drv = self.drv
            self.drv = DiscreteRandomVariable(normalized_values_probs)
            self.update_info()
            self.update_table()
            self.variable_changed.emit()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
            self.drv = old_drv
            self.update_table()
    
    def update_table(self):
        """Обновление таблицы из DRV (без вызова сигналов)"""
        # Блокируем сигналы, чтобы избежать рекурсии
        self.table.blockSignals(True)
        try:
            self.table.setRowCount(0)
            for value, prob in self.drv.get_pmf():
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(f"{value:.4f}"))
                self.table.setItem(row, 1, QTableWidgetItem(f"{prob:.4f}"))
        finally:
            self.table.blockSignals(False)
    
    def update_info(self):
        total_prob = sum(self.drv.probabilities)
        count = len(self.drv.values)
        self.info_label.setText(f"Количество значений: {count}, Сумма вероятностей: {total_prob:.4f}")
    
    def get_variable(self) -> DiscreteRandomVariable:
        return self.drv
    
    def set_variable(self, drv: DiscreteRandomVariable):
        self.drv = drv
        self.update_table()
        self.update_info()
        # Отправляем сигнал об изменении переменной
        self.variable_changed.emit()