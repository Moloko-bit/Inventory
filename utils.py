import re

def validate_phone(phone: str) -> bool:
    """
    Подсказка: Проверяет, что номер телефона содержит от 7 до 15 цифр 
    и допустимые символы (+, -, пробелы, скобки).
    """
    # Удаляем всё, кроме цифр и плюса, для проверки количества цифр
    digits_only = re.sub(r'\D', '', phone)
    if not (7 <= len(digits_only) <= 15):
        return False
    
    # Регулярное выражение для допустимых символов в телефоне
    pattern = r'^[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]*$'
    return bool(re.match(pattern, phone))

def validate_email(email: str) -> bool:
    """
    Подсказка: Базовая проверка email — проверяет наличие '@' и точки после неё.
    """
    if not email:
        return True  # Email может быть необязательным полем (если разрешено)
    
    parts = email.split('@')
    if len(parts) != 2:
        return False
    
    local_part, domain_part = parts
    if not local_part or not domain_part:
        return False
        
    # Проверяем, что в доменной части есть хотя бы одна точка и она не в начале/конце
    if '.' not in domain_part or domain_part.startswith('.') or domain_part.endswith('.'):
        return False
        
    return True