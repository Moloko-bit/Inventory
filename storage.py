import csv
import json
import os
from models import Contact

DATA_FILE = "contacts.json"
CSV_FILE = "contacts.csv"

def save_to_json(contacts):
    """Сохраняет список контактов в JSON файл с помощью to_dict()."""
    data = [contact.to_dict() for contact in contacts]
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_from_json():
    """Загружает контакты из JSON файла с помощью from_dict()."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Восстанавливаем каждый объект через класс Contact
            return [Contact.from_dict(item) for item in data]
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return []

def export_to_csv(contacts):
    """
    #ЭКСПОРТ_В_CSV: Автоматически собирает все возможные ключи (поля) из всех 
    контактов и записывает их в таблицу CSV, избегая ошибок отсутствия ключей.
    """
    if not contacts:
        print("📭 Нет данных для экспорта в CSV.")
        return

    # Превращаем все контакты в словари
    dicts_data = [c.to_dict() for c in contacts]

    # Собираем абсолютно все уникальные поля со всех объектов (name, phone, birthday, company и т.д.)
    fieldnames = set()
    for item in dicts_data:
        fieldnames.update(item.keys())
    
    # Превращаем во фрейм-список, гарантируя, что первыми пойдут type, name, phone
    priority_fields = ["type", "name", "phone"]
    other_fields = sorted([f for f in fieldnames if f not in priority_fields])
    final_fieldnames = [f for f in priority_fields if f in fieldnames] + other_fields

    try:
        with open(CSV_FILE, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=final_fieldnames)
            writer.writeheader()  # Записываем шапку таблицы
            for row in dicts_data:
                writer.writerow(row)  # Записываем строки с данными
        print(f"📁 Успешно экспортировано в файл: {CSV_FILE}")
    except Exception as e:
        print(f"❌ Ошибка при экспорте в CSV: {e}")