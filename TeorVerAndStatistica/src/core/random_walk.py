"""
Модуль для моделирования случайного блуждания
"""
from typing import Dict, List, Tuple
import math
from .discrete_random_variable import DiscreteRandomVariable


class RandomWalkSimulator:
    """Класс для моделирования случайного блуждания"""
    
    @staticmethod
    def compute_final_positions_distribution(
        initial_position: float,
        step_distribution: DiscreteRandomVariable,
        n_steps: int
    ) -> DiscreteRandomVariable:
        if n_steps == 0:
            # Если шагов нет, возвращаем дельта-функцию в начальной позиции
            return DiscreteRandomVariable([(initial_position, 1.0)])
        
        current_distribution = DiscreteRandomVariable([(initial_position, 1.0)])
        
        # Выполняем n шагов, каждый раз складывая текущее распределение с распределением шага
        for _ in range(n_steps):
            current_distribution = current_distribution + step_distribution
        
        return current_distribution
    
    @staticmethod
    def simulate_walk(
        initial_position: float,
        step_distribution: DiscreteRandomVariable,
        n_steps: int
    ) -> List[float]:
        positions = [initial_position]
        current_position = initial_position
        
        for _ in range(n_steps):
            step = step_distribution.sample()
            current_position += step
            positions.append(current_position)
        
        return positions

