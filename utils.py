from typing import List, Set
from collections import deque
from models import Item, Checkout, Request, ItemNotFoundError, InsufficientStockError

class WorkshopInventory:
    """Основной класс управления складом мастерской (композиция моделей)."""

    def __init__(self) -> None:
        self.items: List[Item] = []
        self.checkouts: List[Checkout] = []
        self.requests: List[Request] = []
        self.request_queue: deque = deque() # Очередь заявок (FIFO)

    def add_item(self, item: Item) -> None:
        """Добавление нового предмета или обновление существующего."""
        for existing in self.items:
            if existing.item_id == item.item_id:
                existing.quantity += item.quantity
                return
        self.items.append(item)
        self.request_queue.append(item)

    def get_categories(self) -> Set[str]:
        """Возвращает множество уникальных категорий (использование set)."""
        return {item.category for item in self.items}

    def custom_linear_search_by_id(self, item_id: str) -> Item:
        """
        Собственный поиск предмета по ID.
        Сложность: O(N) по времени, O(1) по памяти.
        """
        for item in self.items:
            if item.item_id.lower() == item_id.lower():
                return item
        raise ItemNotFoundError(f"Предмет с ID '{item_id}' не найден.")

    def custom_comb_sort_by_title(self) -> None:
        """
        Собственная сортировка предметов по названию (Алгоритм: Сортировка расческой - Comb Sort).
        Сложность: O(N log N) в среднем, O(N^2) в худшем случае, O(1) по памяти.
        """
        n = len(self.items)
        gap = n
        shrink = 1.3
        sorted_flag = False

        while not sorted_flag:
            gap = int(gap / shrink)
            if gap > 1:
                sorted_flag = False
            else:
                gap = 1
                sorted_flag = True

            i = 0
            while i + gap < n:
                if self.items[i].title.lower() > self.items[i + gap].title.lower():
                    self.items[i], self.items[i + gap] = self.items[i + gap], self.items[i]
                    sorted_flag = False
                i += 1

    def issue_item(self, checkout_id: str, item_id: str, employee: str, date: str) -> None:
        """Выдача инструмента сотруднику с проверкой остатков."""
        item = self.custom_linear_search_by_id(item_id)
        if item.quantity <= 0:
            raise InsufficientStockError(f"Товар '{item.title}' отсутствует на складе.")
        
        item.quantity -= 1
        checkout = Checkout(checkout_id=checkout_id, item_id=item_id, employee=employee, date_issued=date)
        self.checkouts.append(checkout)

    def get_low_stock_items(self) -> List[Item]:
        """Возвращает список предметов с дефицитом (остаток <= минимального порога)."""
        return [item for item in self.items if item.quantity <= item.min_limit]
