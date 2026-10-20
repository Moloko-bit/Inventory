import csv
import json
import logging
from typing import Generator, List, Dict, Any
from models import Item, Checkout, Request, InventoryError

logger = logging.getLogger(__name__)


def read_csv_items(file_path: str) -> Generator[Dict[str, str], None, None]:
    """Генератор для построчного чтения CSV-файла без загрузки всего файла в память."""
    try:
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield row
    except FileNotFoundError:
        logger.error(f"CSV файл не найден: {file_path}")
        raise InventoryError(f"Файл {file_path} не обнаружен.")
    except Exception as e:
        logger.error(f"Ошибка при чтении CSV: {e}")
        raise InventoryError(f"Ошибка чтения файла: {e}")


def save_state_to_json(file_path: str, data: Dict[str, List[Any]]) -> None:
    """Сохранение текущего состояния системы в JSON."""
    try:
        serializable_data = {
            "items": [vars(item) for item in data.get("items", [])],
            "checkouts": [vars(ch) for ch in data.get("checkouts", [])],
            "requests": [vars(req) for req in data.get("requests", [])]
        }
        with open(file_path, mode="w", encoding="utf-8") as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=4)
        logger.info(f"Состояние успешно сохранено в {file_path}")
    except Exception as e:
        logger.error(f"Не удалось сохранить JSON: {e}")
        raise InventoryError(f"Ошибка сохранения данных: {e}")


def load_state_from_json(file_path: str) -> Dict[str, list]:
    """Загрузка состояния системы из JSON при запуске."""
    try:
        with open(file_path, mode="r", encoding="utf-8") as f:
            data = json.load(f)
            items = [Item(**i) for i in data.get("items", [])]
            checkouts = [Checkout(**c) for c in data.get("checkouts", [])]
            requests = [Request(**r) for r in data.get("requests", [])]
            return {"items": items, "checkouts": checkouts, "requests": requests}
    except FileNotFoundError:
        logger.warning(f"Файл состояния {file_path} не найден. Начинаем с пустыми данными.")
        return {"items": [], "checkouts": [], "requests": []}
    except Exception as e:
        logger.error(f"Ошибка загрузки JSON: {e}")
        return {"items": [], "checkouts": [], "requests": []}
