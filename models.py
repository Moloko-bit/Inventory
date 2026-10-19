# #ПАТТЕРН_КОМАНДА: Базовый класс-интерфейс для всех команд управления состоянием (Undo/Redo)
class Command:
    def execute(self):
        # #ИНТЕРФЕЙС: Метод выполнения действия должен быть переопределен в потомках
        raise NotImplementedError

    def undo(self):
        # #ИНТЕРФЕЙС: Метод отмены действия должен быть переопределен в потомках
        raise NotImplementedError


# #БАЗОВЫЙ_КЛАСС: Родительский класс для всех типов контактов
class Contact:
    extra_fields = ()       # Кортеж для хранения имен уникальных полей дочерних классов
    validation_rules = {}   # Словарь lambda-правил для проверки атрибутов

    # Универсальный конструктор с поддержкой поля is_favorite (по умолчанию False)
    def __init__(self, name, phone, is_favorite=False, **specific_fields):
        self.name = name                 # Сохраняем имя контакта
        self.phone = phone               # Сохраняем телефон (может быть строкой или списком)
        self.is_favorite = is_favorite   # Статус избранного (булево значение)[cite: 6]
        
        # Автоматически перебираем и сохраняем уникальные поля подкласса
        for field in self.extra_fields:
            # Проверяем, передано ли поле в аргументах
            if field in specific_fields:
                # Динамически устанавливаем атрибут объекта через setattr
                setattr(self, field, specific_fields[field])
            else:
                # Если поле отсутствует, записываем пустую строку по умолчанию
                setattr(self, field, "")

    # Полиморфный метод поиска по подстроке (имя или телефон)
    def matches(self, text):
        # Переводим поисковый текст в нижний регистр для регистронезависимости
        search_str = text.lower()
        # Превращаем телефон в строку, если это список, для безопасного поиска
        phones_str = " ".join(self.phone) if isinstance(self.phone, list) else str(self.phone)
        # Возвращаем True, если строка найдена в имени или телефонах
        return search_str in self.name.lower() or search_str in phones_str.lower()

    # Универсальная валидация полей через лямбда-функции
    def validate(self):
        # Перебираем все поля и правила из словаря
        for field, rule in self.validation_rules.items():
            # Получаем значение атрибута из объекта
            value = getattr(self, field, None)
            # Проверяем значение через правило
            if not rule(value):
                # Если проверка не прошла, вызываем ошибку
                raise ValueError(f"Некорректное значение для поля '{field}': {value}")
        # Возвращаем True, если все проверки успешны
        return True

    # Метод для полного вывода обычного базового контакта
    def display(self):
        # Добавляем звездочку, если контакт в избранном
        fav_mark = "⭐ " if self.is_favorite else ""
        # Красиво форматируем телефоны через запятую, если их несколько
        phones = ", ".join(self.phone) if isinstance(self.phone, list) else self.phone
        # Возвращаем готовую строку для вывода
        return f"{fav_mark}{self.name} - {phones}"

    # Метод для краткой сводки обычного базового контакта
    def summary(self):
        # Добавляем отметку избранного в сводку
        fav_mark = "⭐ " if self.is_favorite else ""
        return f"[Контакт] {fav_mark}{self.name}"

    # Метод сериализации: превращает объект в словарь для JSON и CSV
    def to_dict(self):
        # Создаем базовый словарь с основными полями и статусом избранного
        data = {
            "type": self.__class__.__name__,
            "name": self.name,
            "phone": self.phone,
            "is_favorite": self.is_favorite  # Сохраняем состояние избранного[cite: 6]
        }
        # Проходим по всем уникальным полям подкласса
        for field in self.extra_fields:
            # Записываем специфичное поле в словарь
            data[field] = getattr(self, field, "")
        # Возвращаем итоговый словарь
        return data

    # Фабричный метод класса для восстановления объекта из словаря при загрузке
    @classmethod
    def from_dict(cls, data):
        # Извлекаем тип класса, по умолчанию Contact
        contact_type = data.pop("type", "Contact")
        # Находим класс в глобальной области видимости по имени
        target_class = globals().get(contact_type, cls)
        
        # Извлекаем базовые поля
        name = data.pop("name", "")
        phone = data.pop("phone", "")
        # Безопасно извлекаем статус избранного для старых файлов (по умолчанию False)[cite: 6]
        is_favorite = data.pop("is_favorite", False)
        
        # Создаем и возвращаем объект нужного подкласса с оставшимися данными
        return target_class(name=name, phone=phone, is_favorite=is_favorite, **data)


# Дочерний класс для личных контактов
class PersonalContact(Contact):
    # Указываем уникальное поле для личного контакта
    extra_fields = ("birthday",)
    validation_rules = {
        "birthday": lambda val: isinstance(val, str) and len(val) > 0
    }

    # Переопределяем метод полного вывода
    def display(self):
        fav_mark = "⭐ " if self.is_favorite else ""
        birthday = getattr(self, "birthday", "Не указано")
        phones = ", ".join(self.phone) if isinstance(self.phone, list) else self.phone
        return f"{fav_mark}{self.name} - {phones} | ДР: {birthday}"

    # Переопределяем метод краткой сводки
    def summary(self):
        fav_mark = "⭐ " if self.is_favorite else ""
        return f"[Личный] {fav_mark}{self.name}"


# Дочерний класс для рабочих контактов
class WorkContact(Contact):
    extra_fields = ("company", "job_title")
    validation_rules = {
        "company": lambda val: isinstance(val, str) and len(val) > 0,
        "job_title": lambda val: isinstance(val, str) and len(val) > 0
    }

    def display(self):
        fav_mark = "⭐ " if self.is_favorite else ""
        company = getattr(self, "company", "Не указано")
        job_title = getattr(self, "job_title", "Не указано")
        phones = ", ".join(self.phone) if isinstance(self.phone, list) else self.phone
        return f"{fav_mark}{self.name} - {phones} | Работа: {company} ({job_title})"

    def summary(self):
        fav_mark = "⭐ " if self.is_favorite else ""
        return f"[Рабочий] {fav_mark}{self.name} - {getattr(self, 'company', '')}"


# Дочерний класс для экстренных контактов
class EmergencyContact(Contact):
    extra_fields = ("relationship", "priority")
    validation_rules = {
        "relationship": lambda val: isinstance(val, str) and len(val) > 0,
        "priority": lambda val: isinstance(val, bool)
    }

    def display(self):
        fav_mark = "⭐ " if self.is_favorite else ""
        relationship = getattr(self, "relationship", "Не указано")
        priority = getattr(self, "priority", False)
        status = "Срочный" if priority else "Обычный"
        phones = ", ".join(self.phone) if isinstance(self.phone, list) else self.phone
        return f"{fav_mark}{self.name} - {phones} | Родство: {relationship} [{status}]"

    def summary(self):
        fav_mark = "⭐ " if self.is_favorite else ""
        return f"[Экстренный] {fav_mark}{self.name} ({getattr(self, 'relationship', '')})"


# Дочерний класс для семейных контактов
class FamilyContact(Contact):
    extra_fields = ("family_role",)
    validation_rules = {
        "family_role": lambda val: isinstance(val, str) and len(val) > 0
    }

    def display(self):
        fav_mark = "⭐ " if self.is_favorite else ""
        role = getattr(self, "family_role", "Не указано")
        phones = ", ".join(self.phone) if isinstance(self.phone, list) else self.phone
        return f"{fav_mark}{self.name} - {phones} | Роль в семье: {role}"

    def summary(self):
        fav_mark = "⭐ " if self.is_favorite else ""
        return f"[Семья] {fav_mark}{self.name} ({getattr(self, 'family_role', '')})"


# ==========================================
# КЛАССЫ КОМАНД ДЛЯ ИСТОРИИ (UNDO / REDO)
# ==========================================

# Команда добавления нового контакта[cite: 16]
class AddContactCommand(Command):
    def __init__(self, contacts_list, contact_obj):
        self.contacts_list = contacts_list
        self.contact_obj = contact_obj

    def execute(self):
        # Добавляем контакт в общий список
        self.contacts_list.append(self.contact_obj)

    def undo(self):
        # Удаляем именно этот контакт при отмене
        if self.contact_obj in self.contacts_list:
            self.contacts_list.remove(self.contact_obj)


# Команда добавления номера к существующему контакту[cite: 17]
class AddPhoneCommand(Command):
    def __init__(self, contact, phone):
        self.contact = contact
        self.phone = phone

    def execute(self):
        # Превращаем телефон в список, если это была строка
        if isinstance(self.contact.phone, str):
            self.contact.phone = [self.contact.phone]
        # Добавляем новый номер, если его еще нет
        if self.phone not in self.contact.phone:
            self.contact.phone.append(self.phone)

    def undo(self):
        # Удаляем добавленный номер при отмене
        if isinstance(self.contact.phone, list) and self.phone in self.contact.phone:
            self.contact.phone.remove(self.phone)


# Команда удаления контакта[cite: 18]
class DeleteContactCommand(Command):
    def __init__(self, contacts_list, contact_obj):
        self.contacts_list = contacts_list
        self.contact_obj = contact_obj
        # Запоминаем индекс удаляемого элемента для точного восстановления
        self.index = contacts_list.index(contact_obj) if contact_obj in contacts_list else 0

    def execute(self):
        # Удаляем контакт из списка
        if self.contact_obj in self.contacts_list:
            self.index = self.contacts_list.index(self.contact_obj)
            self.contacts_list.remove(self.contact_obj)

    def undo(self):
        # Возвращаем контакт на его прежнюю позицию при отмене
        self.contacts_list.insert(self.index, self.contact_obj)


# Команда переключения статуса избранного[cite: 20]
class ToggleFavoriteCommand(Command):
    def __init__(self, contact):
        self.contact = contact
        self.old_state = contact.is_favorite

    def execute(self):
        # Запоминаем старое состояние и меняем на противоположное
        self.old_state = self.contact.is_favorite
        self.contact.is_favorite = not self.old_state

    def undo(self):
        # Восстанавливаем прежнее состояние при отмене
        self.contact.is_favorite = self.old_state