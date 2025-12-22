"""
Модуль gui - графический интерфейс
"""

from .main_window import MainWindow
from .variable_editor import VariableEditor
from .plot_widget import PlotWidget
from .random_walk_widget import RandomWalkWidget

__all__ = ['MainWindow', 'VariableEditor', 'PlotWidget', 'RandomWalkWidget']