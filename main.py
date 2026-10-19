# Импортируем классы моделей и конкретные команды из models.py
from models import (
    Contact, PersonalContact, WorkContact, EmergencyContact, FamilyContact,
    AddContactCommand, AddPhoneCommand, DeleteContactCommand, ToggleFavoriteCommand
)
# Импортируем функции сохранения, загрузки и экспорт из storage.py
from storage import save_to_json, load_from_json, export_to_csv
# Импортируем валидаторы из utils.py
from utils import validate_phone, validate_email

def main():
    # Загружаем существующие контакты из JSON при старте программы
    contacts = load_from_json()
    
    # Создаем стеки истории для Undo и Redo[cite: 14]
    undo_stack = []
    redo_stack = []

    # Вспомогательная функция для выполнения команд по паттерну Command
    def execute_command(cmd):
        # Выполняем действие команды
        cmd.execute()
        # Добавляем команду в стек отмен
        undo_stack.append(cmd)
        # Очищаем стек повторов при новом действии[cite: 5, 14]
        redo_stack.clear()
        # Автоматически сохраняем изменения в JSON
        save_to_json(contacts)

    # Запускаем основной цикл интерфейса программы
    while True:
        # Выводим шапку меню
        print("\n" + "="*30)
        print("    КНИГА КОНТАКТОВ (Избранное & Команды)")
        print("="*30)
        # Выводим статистику записей и размеры стеков истории
        print(f"📊 Всего записей: {len(contacts)} | Undo: {len(undo_stack)} | Redo: {len(redo_stack)}")
        print("--------------------------------")
        # Выводим пункты меню
        print("1. Показать все контакты (сортировка + избранное сверху)")
        print("2. Добавить контакт / номер (правило имени)")
        print("3. Найти контакт")
        print("4. Показать краткую сводку")
        print("5. Переключить статус «Избранное»")
        print("6. Удалить контакт")
        print("7. Отменить действие (Undo)")
        print("8. Повторить действие (Redo)")
        print("9. Сохранить / Экспортировать в CSV")
        print("0. Выход")
        print("--------------------------------")
        
        # Считываем выбор пункта меню
        choice = input("Выберите пункт меню: ").strip()
        
        # Обработка пункта 1: Просмотр списка с сортировкой и избранным сверху[cite: 8]
        if choice == "1":
            if not contacts:
                print("📭 Книга контактов пуста.")
            else:
                print("\nВыберите вариант сортировки:")
                print("1. По имени (алфавит)")
                print("2. По телефону")
                sort_choice = input("Ваш выбор (1-2) [1]: ").strip()
                
                # Разделяем контакты на избранные и остальные[cite: 8]
                favorites = [c for c in contacts if c.is_favorite]
                others = [c for c in contacts if not c.is_favorite]
                
                # Применяем выбранный порядок сортировки внутри каждой группы[cite: 8]
                if sort_choice == "2":
                    fav_sorted = sorted(favorites, key=lambda x: str(x.phone))
                    oth_sorted = sorted(others, key=lambda x: str(x.phone))
                else:
                    fav_sorted = sorted(favorites, key=lambda x: x.name.lower())
                    oth_sorted = sorted(others, key=lambda x: x.name.lower())
                
                # Объединяем списки: избранные всегда идут первыми[cite: 8]
                sorted_contacts = fav_sorted + oth_sorted
                
                print(f"\n--- СПИСОК КОНТАКТОВ ---")
                for i, c in enumerate(sorted_contacts, 1):
                    print(f"{i}. {c.display()}")
                    
        # Обработка пункта 2: Добавление с правилом совпадения имен[cite: 10, 11]
        elif choice == "2":
            raw_name = input("Введите имя контакта: ").strip()
            if not raw_name:
                print("❌ Имя не может быть пустым!")
                continue
                
            # Нормализуем имя для сравнения (регистр и лишние пробелы)[cite: 10]
            norm_name = " ".join(raw_name.split()).lower()
            
            # Проверяем, существует ли уже контакт с таким именем[cite: 11]
            existing_contact = next((c for c in contacts if " ".join(c.name.split()).lower() == norm_name), None)
            
            phone = input("Введите номер телефона: ").strip()
            if phone and not validate_phone(phone):
                print("⚠️ Неверный формат телефона, но поле сохранено.")
            
            # Если имя уже есть — добавляем новый номер к существующему контакту[cite: 10, 11]
            if existing_contact:
                if phone:
                    current_phones = existing_contact.phone if isinstance(existing_contact.phone, list) else [existing_contact.phone]
                    # Проверяем, нет ли уже такого номера у контакта[cite: 11]
                    if phone in current_phones:
                        print(f"ℹ️ У контакта '{existing_contact.name}' уже есть такой номер телефона.")
                    else:
                        # Создаем и выполняем команду добавления номера через менеджер[cite: 16, 17]
                        cmd = AddPhoneCommand(existing_contact, phone)
                        execute_command(cmd)
                        print(f"✅ Номер '{phone}' успешно добавлен к существующему контакту '{existing_contact.name}'!")
                else:
                    print("❌ Телефон не введен, данные не изменены.")
            else:
                # Если имя новое — создаем полноценный новый контакт[cite: 10, 16]
                print("\nВыберите тип контакта:")
                print("1. Личный (PersonalContact)")
                print("2. Рабочий (WorkContact)")
                print("3. Экстренный (EmergencyContact)")
                print("4. Семейный (FamilyContact)")
                print("5. Обычный базовый контакт")
                
                type_choice = input("Ваш выбор (1-5) [5]: ").strip()
                
                try:
                    # Инстанцируем нужный подкласс в зависимости от выбора
                    if type_choice == "1":
                        birthday = input("Введите дату рождения: ").strip()
                        new_contact = PersonalContact(name=raw_name, phone=phone, birthday=birthday)
                    elif type_choice == "2":
                        company = input("Введите компанию: ").strip()
                        job_title = input("Введите должность: ").strip()
                        new_contact = WorkContact(name=raw_name, phone=phone, company=company, job_title=job_title)
                    elif type_choice == "3":
                        relationship = input("Введите степень родства: ").strip()
                        priority_input = input("Срочный приоритет? (д/н) [н]: ").strip().lower()
                        priority = priority_input in ('д', 'да', 'y', 'yes')
                        new_contact = EmergencyContact(name=raw_name, phone=phone, relationship=relationship, priority=priority)
                    elif type_choice == "4":
                        family_role = input("Введите роль в семье: ").strip()
                        new_contact = FamilyContact(name=raw_name, phone=phone, family_role=family_role)
                    else:
                        new_contact = Contact(name=raw_name, phone=phone)
                    
                    # Проверяем валидность полей
                    new_contact.validate()
                    
                    # Оборачиваем в команду создания и запускаем через историю[cite: 16]
                    cmd = AddContactCommand(contacts, new_contact)
                    execute_command(cmd)
                    print(f"✅ Новый контакт '{raw_name}' успешно создан!")
                    
                except ValueError as e:
                    print(f"❌ Ошибка валидации: {e}")
                
        # Обработка пункта 3: Поиск контактов
        elif choice == "3":
            query = input("Введите имя или телефон для поиска: ").strip()
            if not query:
                print("❌ Поисковый запрос не может быть пустым.")
                continue
                
            # Ищем совпадения через полиморфный метод matches()
            found = [c for c in contacts if c.matches(query)]
            if found:
                print(f"\n🔍 Найдено совпадений: {len(found)}")
                for i, c in enumerate(found, 1):
                    print(f"{i}. {c.display()}")
            else:
                print("🔍 По вашему запросу ничего не найдено.")
                
        # Обработка пункта 4: Краткая сводка
        elif choice == "4":
            if not contacts:
                print("📭 Книга контактов пуста.")
                continue
                
            print("\n--- КРАТКАЯ СВОДКА ---")
            for i, c in enumerate(contacts, start=1):
                print(f"{i}. {c.summary()}")
                
        # Обработка пункта 5: Переключение статуса «Избранное»[cite: 7, 20]
        elif choice == "5":
            name = input("Введите точное имя контакта для переключения избранного: ").strip()
            target = next((c for c in contacts if c.name.lower() == name.lower()), None)
            
            if not target:
                print("❌ Контакт не найден.")
                continue
                
            # Создаем и выполняем команду переключения через историю[cite: 20]
            cmd = ToggleFavoriteCommand(target)
            execute_command(cmd)
            print(f"✅ Статус контакта '{target.name}' изменен. Текущий статус: {target.is_favorite}")
            
        # Обработка пункта 6: Удаление контакта[cite: 18]
        elif choice == "6":
            name = input("Введите имя контакта для удаления: ").strip()
            target = next((c for c in contacts if c.name.lower() == name.lower()), None)
            
            if not target:
                print("❌ Контакт не найден.")
                continue
                
            # Создаем и выполняем команду удаления с сохранением позиции[cite: 18]
            cmd = DeleteContactCommand(contacts, target)
            execute_command(cmd)
            print(f"🗑️ Контакт '{name}' успешно удален.")
            
        # Обработка пункта 7: Отмена действия (Undo)[cite: 14, 15]
        elif choice == "7":
            if not undo_stack:
                print("⚠️ История отмен пуста.")
            else:
                # Извлекаем последнюю команду из стека отмен
                cmd = undo_stack.pop()
                # Вызываем метод отмены
                cmd.undo()
                # Переносим команду в стек повторов (Redo)
                redo_stack.append(cmd)
                # Сохраняем обновленное состояние
                save_to_json(contacts)
                print("↩️ Последнее действие отменено.")
                
        # Обработка пункта 8: Повтор действия (Redo)[cite: 14, 15]
        elif choice == "8":
            if not redo_stack:
                print("⚠️ История повторов пуста.")
            else:
                # Извлекаем команду из стека повторов
                cmd = redo_stack.pop()
                # Снова выполняем её
                cmd.execute()
                # Возвращаем в стек отмен
                undo_stack.append(cmd)
                # Сохраняем состояние
                save_to_json(contacts)
                print("🔁 Действие повторено.")
                
        # Обработка пункта 9: Сохранение и экспорт в CSV
        elif choice == "9":
            save_to_json(contacts)
            export_to_csv(contacts)
            print("💾 Данные сохранены и экспортированы.")
            
        # Обработка пункта 0: Выход из программы
        elif choice == "0":
            save_to_json(contacts)
            print("💾 Все изменения сохранены. До свидания!")
            break
        else:
            print("❌ Неверный выбор! Введите цифру от 0 до 9.")

# Проверяем запуск скрипта как главного модуля
if __name__ == "__main__":
    main()