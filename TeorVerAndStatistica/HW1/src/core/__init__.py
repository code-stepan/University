"""
Модуль core - основные классы для работы с дискретными случайными величинами
"""

from .discrete_random_variable import DiscreteRandomVariable
from .statistics import StatisticsCalculator
from .random_walk import RandomWalkSimulator

__all__ = ['DiscreteRandomVariable', 'StatisticsCalculator', 'RandomWalkSimulator']