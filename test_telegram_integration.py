#!/usr/bin/env python3
"""
Тестовый скрипт для проверки интеграции отправки баг-репортов и улучшений в Telegram
"""

import os
import json
from datetime import datetime
from telegram_sender import send_bug_reports_to_telegram, send_improvements_to_telegram

def create_test_bugreport(timestamp: str):
    """Создает тестовый баг-репорт для проверки"""
    test_bug_content = """# Заголовок
Проблема с загрузкой данных в приложении

## Описание
При попытке загрузить данные приложение зависает и не отвечает на действия пользователя.

## Шаги для воспроизведения
1. Открыть приложение
2. Нажать на кнопку "Загрузить данные"
3. Подождать 30 секунд

## Ожидаемый результат
Данные должны загрузиться в течение 5-10 секунд

## Фактический результат
Приложение зависает, индикатор загрузки крутится бесконечно

## Окружение
- iOS 17.2
- Версия приложения: 2.1.0
- Модель устройства: iPhone 14 Pro

## Приоритет
Высокий - блокирует основную функциональность"""

    filename = f"output/bugreport_1_{timestamp}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(test_bug_content)
    
    print(f"✅ Создан тестовый баг-репорт: {filename}")
    return filename

def create_test_improvement(timestamp: str):
    """Создает тестовое предложение по улучшению для проверки"""
    test_improvement_content = """# Название предложения
Добавление темной темы в приложение

## Категория
UX Improvement, Feature

## Описание проблемы
Многие пользователи жалуются на слишком яркий интерфейс приложения при использовании в темное время суток. Это вызывает усталость глаз и неудобство.

## Предлагаемое решение
Добавить возможность переключения между светлой и темной темами в настройках приложения. Темная тема должна автоматически применяться в зависимости от системных настроек устройства.

## Пользовательский эффект (User Impact)
- Улучшение комфорта использования приложения в темное время
- Экономия заряда батареи на OLED-экранах
- Соответствие современным стандартам UX

## Ожидаемый результат
Увеличение времени использования приложения в вечернее время на 25-30%, снижение жалоб на усталость глаз.

## Приоритет
Medium - улучшение пользовательского опыта

## Оценка сложности внедрения
Medium - требует адаптации всех экранов под темную тему"""

    filename = f"output/improvement_proposal_dark_theme_{timestamp}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(test_improvement_content)
    
    print(f"✅ Создано тестовое предложение по улучшению: {filename}")
    return filename

def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование интеграции с Telegram")
    print("=" * 50)
    
    # Создаем временную метку для тестов
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"📅 Timestamp для тестов: {timestamp}")
    
    # Проверяем существование директории output
    os.makedirs('output', exist_ok=True)
    
    print("\n🐛 ТЕСТ 1: Создание и отправка баг-репорта")
    print("-" * 40)
    
    try:
        # Создаем тестовый баг-репорт
        bug_file = create_test_bugreport(timestamp)
        
        # Отправляем в Telegram
        print("📤 Отправка тестового баг-репорта...")
        success = send_bug_reports_to_telegram(timestamp, "@mmalashkin")
        
        if success:
            print("✅ Тест баг-репорта пройден!")
        else:
            print("❌ Тест баг-репорта не пройден")
            
    except Exception as e:
        print(f"❌ Ошибка в тесте баг-репорта: {str(e)}")
    
    print("\n💡 ТЕСТ 2: Создание и отправка предложения по улучшению")
    print("-" * 55)
    
    try:
        # Создаем тестовое предложение
        improvement_file = create_test_improvement(timestamp)
        
        # Отправляем в Telegram
        print("📤 Отправка тестового предложения...")
        success = send_improvements_to_telegram(timestamp, "@mmalashkin")
        
        if success:
            print("✅ Тест предложения по улучшению пройден!")
        else:
            print("❌ Тест предложения по улучшению не пройден")
            
    except Exception as e:
        print(f"❌ Ошибка в тесте предложения: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Тестирование завершено!")
    print(f"📁 Тестовые файлы находятся в папке output/ с timestamp {timestamp}")

if __name__ == "__main__":
    main() 