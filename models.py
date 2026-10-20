from dataclasses import dataclass
from abc import ABC, abstractmethod

class InventoryEntity(ABC):
    """Абстрактный базовый класс для демонстрации полиморфизма."""
    
    @abstractmethod
    def get_summary(self) -> str:
        """Возвращает краткую текстовую сводку по сущности."""
        pass


@dataclass
class Item(InventoryEntity):
    """Предмет инвентаря на складе."""
    item_id: str
    title: str
    category: str
    _quantity: int
    min_limit: int

    @property
    def quantity(self) -> int:
        return self._quantity

    @quantity.setter
    def quantity(self, value: int) -> None:
        if value < 0:
            raise ValueError("Количество предмета на складе не может быть отрицательным.")
        self._quantity = value

    def get_summary(self) -> str:
        status = " [ДЕФИЦИТ]" if self._quantity <= self.min_limit else ""
        return f"[{self.item_id}] {self.title} ({self.category}) — Остаток: {self._quantity}{status}"


@dataclass
class Checkout(InventoryEntity):
    """Запись о выдаче инструмента сотруднику."""
    checkout_id: str
    item_id: str
    employee: str
    date_issued: str
    is_returned: bool = False

    def get_summary(self) -> str:
        state = "Возвращено" if self.is_returned else "На руках"
        return f"Выдача {self.checkout_id}: Предмет {self.item_id} у {self.employee} от {self.date_issued} ({state})"


@dataclass
class Request(InventoryEntity):
    """Заявка на ремонт или закупку."""
    request_id: str
    item_id: str
    reason: str
    priority: str
    status: str = "Новая"

    def get_summary(self) -> str:
        return f"Заявка {self.request_id} [Приоритет: {self.priority}]: {self.reason} (Статус: {self.status})"


class InventoryError(Exception):
    """Базовое исключение предметной области учета инвентаря."""
    pass


class ItemNotFoundError(InventoryError):
    """Вызывается, если предмет не найден в базе."""
    pass


class InsufficientStockError(InventoryError):
    """Вызывается при попытке выдать больше предметов, чем есть на складе."""
    pass
