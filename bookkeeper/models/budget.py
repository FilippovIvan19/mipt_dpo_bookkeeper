"""
Описан класс, представляющий бюджет
"""

from dataclasses import dataclass


@dataclass
class Budget:
    """
    Бюджет
    хранит срок (duration),
    категорию расходов (category)
    и сумму (amount)
    """
    duration: int
    category: int
    amount: int
