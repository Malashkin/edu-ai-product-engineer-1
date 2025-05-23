#!/usr/bin/env python3
"""
Скрипт для тестирования интеграции с Telegram
"""

import os
from telegram_notifier import TelegramNotifier, test_telegram_connection

def test_basic_message():
    """Тестирует отправку простого сообщения"""
    print("\n🧪 Тест 1: Отправка простого сообщения...")
    try:
        notifier = TelegramNotifier()
        response = notifier.send_message("🧪 Тестовое сообщение из анализатора отзывов")
        if response and response.get('ok'):
            print("✅ Простое сообщение отправлено успешно")
        else:
            print("❌ Ошибка отправки простого сообщения")
    except Exception as e:
        print(f"❌ Ошибка в тесте простого сообщения: {str(e)}")

def test_bug_report():
    """Тестирует отправку баг-репорта"""
    print("\n🐛 Тест 2: Отправка тестового баг-репорта...")
    
    sample_bug_report = """# 1. Заголовок
Приложение крашится при запуске

# 2. Описание
Приложение неожиданно закрывается сразу после запуска, не показывая основной экран

# 3. Шаги для воспроизведения
1. Открыть приложение
2. Подождать 2-3 секунды
3. Приложение закрывается

# 4. Ожидаемый результат
Приложение должно открыться и показать главный экран

# 5. Фактический результат
Приложение закрывается без сообщения об ошибке

# 6. Окружение
- Устройство: iPhone 14
- iOS: 17.2.1
- Версия приложения: 2.1.0

# 7. Вложения
Логи crash report приложены

# 8. Дополнительно
Проблема появилась после обновления до последней версии"""

    try:
        notifier = TelegramNotifier()
        response = notifier.send_bug_report(sample_bug_report, bug_index=1)
        if response and response.get('ok'):
            print("✅ Баг-репорт отправлен успешно")
        else:
            print("❌ Ошибка отправки баг-репорта")
    except Exception as e:
        print(f"❌ Ошибка в тесте баг-репорта: {str(e)}")

def test_summary_report():
    """Тестирует отправку резюме дискуссии"""
    print("\n📊 Тест 3: Отправка резюме дискуссии...")
    
    sample_summary = """# Резюме дискуссии о багах

## Основные проблемы:
1. **Крашы при запуске** - критическая проблема, затрагивает 30% пользователей
2. **Медленная загрузка** - влияет на UX, время загрузки превышает 10 секунд
3. **Проблемы с синхронизацией** - данные не сохраняются между сессиями

## Рекомендации по приоритетам:
- **Высокий приоритет**: Исправить крашы при запуске
- **Средний приоритет**: Оптимизировать время загрузки
- **Низкий приоритет**: Улучшить синхронизацию данных

## Влияние на пользователей:
Проблемы серьезно влияют на retention rate и общий пользовательский опыт"""

    try:
        notifier = TelegramNotifier()
        response = notifier.send_summary_report(sample_summary, "bugs")
        if response and response.get('ok'):
            print("✅ Резюме дискуссии отправлено успешно")
        else:
            print("❌ Ошибка отправки резюме")
    except Exception as e:
        print(f"❌ Ошибка в тесте резюме: {str(e)}")

def test_feature_summary():
    """Тестирует отправку резюме о функциях"""
    print("\n✨ Тест 4: Отправка резюме о запросах функций...")
    
    sample_feature_summary = """# Резюме дискуссии о новых функциях

## Топ запрашиваемых функций:
1. **Темная тема** - запрашивают 45% пользователей
2. **Напоминания и уведомления** - важно для мотивации пользователей
3. **Статистика и графики** - визуализация прогресса

## Анализ осуществимости:
- **Темная тема**: Легко реализуемо, высокий impact
- **Напоминания**: Средняя сложность, требует работы с push notifications
- **Статистика**: Высокая сложность, нужна аналитическая система

## Рекомендации:
Начать с темной темы как quick win, затем заняться напоминаниями"""

    try:
        notifier = TelegramNotifier()
        response = notifier.send_summary_report(sample_feature_summary, "features")
        if response and response.get('ok'):
            print("✅ Резюме о функциях отправлено успешно")
        else:
            print("❌ Ошибка отправки резюме о функциях")
    except Exception as e:
        print(f"❌ Ошибка в тесте резюме о функциях: {str(e)}")

def main():
    """Основная функция тестирования"""
    print("🔧 Тестирование интеграции с Telegram")
    print("=" * 50)
    
    # Проверяем переменные окружения
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN не найден в переменных окружения")
        print("Добавьте в файл .env:")
        print("TELEGRAM_BOT_TOKEN=your_bot_token_here")
        return
    
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID не найден в переменных окружения")
        print("Добавьте в файл .env:")
        print("TELEGRAM_CHAT_ID=your_chat_id_here")
        return
    
    print(f"✅ Найден токен бота: {bot_token[:10]}...")
    print(f"✅ Найден Chat ID: {chat_id}")
    
    # Запуск тестов
    if test_telegram_connection():
        test_basic_message()
        test_bug_report()
        test_summary_report()
        test_feature_summary()
        
        print("\n" + "=" * 50)
        print("🎉 Все тесты завершены!")
        print("Проверьте ваш Telegram чат на наличие тестовых сообщений")
    else:
        print("\n❌ Базовое подключение не работает. Проверьте настройки.")

if __name__ == "__main__":
    main() 