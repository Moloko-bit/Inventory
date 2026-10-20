import logging
import os
from models import Item, Request, InventoryError
from storage import read_csv_items, save_state_to_json, load_state_from_json
from services import WorkshopInventory

# Настройка логирования
logging.basicConfig(
    filename="workshop_inventory.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

DATA_JSON = "inventory_state.json"
IMPORT_CSV = "inventory_import.csv"


def create_sample_csv_if_not_exists() -> None:
    """Создает пример CSV-файла для тестирования импорта."""
    if not os.path.exists(IMPORT_CSV):
        with open(IMPORT_CSV, mode="w", encoding="utf-8", newline="") as f:
            f.write("item_id,title,category,quantity,min_limit\n")
            f.write("TL-001,Дрель аккумуляторная,Инструмент,3,1\n")
            f.write("TL-002,Набор ключей рожковых,Инструмент,5,2\n")
            f.write("MS-101,Диск отрезной 125мм,Расходник,2,4\n")


def main() -> None:
    """Главная функция запуска консольного приложения."""
    create_sample_csv_if_not_exists()
    inventory = WorkshopInventory()
    
    # Загрузка при старте из JSON
    state = load_state_from_json(DATA_JSON)
    inventory.items = state["items"]
    inventory.checkouts = state["checkouts"]
    inventory.requests = state["requests"]
    logger.info("Приложение запущенно. Данные загружены.")

    while True:
        print("\n--- СИСТЕМА УЧЕТА ИНВЕНТАРЯ МАСТЕРСКОЙ ---")
        print("1. Показать весь инвентарь")
        print("2. Импортировать товары из CSV")
        print("3. Найти предмет по ID (Свой поиск O(N))")
        print("4. Отсортировать предметы по названию (Своя сортировка)")
        print("5. Выдать инструмент сотруднику")
        print("6. Отчет по дефициту (остаткам)")
        print("7. Сохранить и выйти")

        choice = input("Выберите пункт меню (1-7): ").strip()

        try:
            if choice == "1":
                if not inventory.items:
                    print("\nСклад пуст.")
                else:
                    print("\n--- СПИСОК ИНВЕНТАРЯ ---")
                    for item in inventory.items:
                        print(item.get_summary())

            elif choice == "2":
                print(f"\nИмпорт данных из файла {IMPORT_CSV}...")
                count = 0
                for row in read_csv_items(IMPORT_CSV):
                    item = Item(
                        item_id=row["item_id"],
                        title=row["title"],
                        category=row["category"],
                        _quantity=int(row["quantity"]),
                        min_limit=int(row["min_limit"])
                    )
                    inventory.add_item(item)
                    count += 1
                print(f"Успешно импортировано/обновлено записей: {count}")
                logger.info(f"Импортировано {count} записей из CSV.")

            elif choice == "3":
                target_id = input("Введите ID предмета (например, TL-001): ").strip()
                item = inventory.custom_linear_search_by_id(target_id)
                print("\nНайден предмет:")
                print(item.get_summary())

            elif choice == "4":
                inventory.custom_comb_sort_by_title()
                print("\nИнвентарь успешно отсортирован по названию.")
                for item in inventory.items:
                    print(item.get_summary())

            elif choice == "5":
                ch_id = input("Введите ID выдачи (например, CO-101): ").strip()
                item_id = input("Введите ID предмета: ").strip()
                employee = input("ФИО сотрудника: ").strip()
                date = input("Дата выдачи (ГГГГ-ММ-ДД): ").strip()
                inventory.issue_item(ch_id, item_id, employee, date)
                print("Инструмент успешно выдан, остаток уменьшен.")
                logger.info(f"Выдан предмет {item_id сотруднику {employee}")

            elif choice == "6":
                low_stock = inventory.get_low_stock_items()
                print("\n--- ОТЧЕТ ПО ДЕФИЦИТУ ---")
                if not low_stock:
                    print("Дефицита на складе нет.")
                else:
                    for item in low_stock:
                        print(item.get_summary())

            elif choice == "7":
                save_state_to_json(DATA_JSON, {
                    "items": inventory.items,
                    "checkouts": inventory.checkouts,
                    "requests": inventory.requests
                })
                print("\nДанные сохранены. Работа завершена.")
                logger.info("Работа приложения завершена пользователем.")
                break
            else:
                print("Неверный выбор. Введите число от 1 до 7.")

        except InventoryError as ie:
            print(f"\n[Ошибка предметной области]: {ie}")
            logger.warning(f"Ошибка предметной области: {ie}")
        except ValueError as ve:
            print(f"\n[Ошибка ввода данных]: {ve}")
            logger.error(f"Ошибка ввода: {ve}")
        except Exception as ex:
            print(f"\n[Непредвиденная ошибка]: {ex}")
            logger.critical(f"Критическая ошибка: {ex}")


if __name__ == "__main__":
    main()
