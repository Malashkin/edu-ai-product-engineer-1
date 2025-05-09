import asyncio
import json
import os
from datetime import datetime
from app_reviews_scraper import AppReviewsScraper
from persona_generator import PersonaGenerator
from group_discussion import run_group_discussion
from summarizer import DiscussionSummarizer
from recommendations import Recommendations
from review_classifier import ReviewClassifier
from dotenv import load_dotenv
import openai

# Загружаем переменные окружения
load_dotenv()

# Параметры приложения Sober
APP_NAME = "Sober"
GOOGLE_PLAY_ID = "com.osu.cleanandsobertoolboxandroid"  # Корректный ID в Google Play
MONTHS = 12  # Период для анализа - 12 месяцев (1 год)

async def run_sober_analysis():
    """Основная функция для анализа отзывов приложения Sober"""
    print("Начинаем анализ отзывов приложения Sober...")
    
    # Текущий timestamp для именования файлов
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Шаг 1: Сбор отзывов
    print("\n1. Сбор отзывов из Google Play...")
    scraper = AppReviewsScraper()
    reviews_data = scraper.get_app_reviews(
        app_name=APP_NAME,
        google_play_id=GOOGLE_PLAY_ID,
        months=MONTHS
    )
    
    # Сохраняем отзывы в файл
    reviews_file = scraper.save_reviews(reviews_data)
    reviews_path = os.path.join('output', reviews_file)
    
    # Загружаем сохраненные отзывы
    with open(reviews_path, 'r', encoding='utf-8') as f:
        reviews_data = json.load(f)
    
    # Проверяем, что есть отзывы для анализа
    all_reviews = []
    for site_name, site_data in reviews_data['sites'].items():
        all_reviews.extend(site_data['reviews'])
    
    if not all_reviews:
        print("Ошибка: не удалось собрать отзывы для анализа")
        return
    
    # Шаг 2: Определение темы приложения
    print("\n2. Определение темы приложения...")
    category, item_type, item_name = analyze_reviews_topic(all_reviews[:20])
    
    # Если определенное название не содержит имя приложения, добавляем его
    if APP_NAME.lower() not in item_name.lower():
        item_name = f"{APP_NAME} ({item_name})"
    
    print(f"Определена тема: {category}, {item_type}, {item_name}")
    
    # Шаг 3: Классификация отзывов
    print("\n3. Классификация отзывов на категории...")
    classifier = ReviewClassifier()
    classified_reviews = classifier.process_reviews(all_reviews)
    
    # Сохраняем классифицированные отзывы
    classified_file = f"classified_reviews_{timestamp}.json"
    with open(os.path.join('output', classified_file), 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'app_name': APP_NAME,
            'category': category,
            'item_type': item_type,
            'item_name': item_name,
            'categories': classified_reviews
        }, f, ensure_ascii=False, indent=2)
    
    print(f"Классифицированные отзывы сохранены в файл: {classified_file}")

    # Шаг 4: Обработка отчетов о багах
    print("\n4. Обработка отчетов о багах...")
    if classified_reviews['bug_reports']['raw']:
        bug_personas = create_personas(
            classified_reviews['bug_reports']['raw'], 
            'bug_reports', 
            timestamp, 
            category
        )
        
        bug_discussion_file = run_category_discussion(
            bug_personas, 
            f"{item_name} (отчеты о багах)", 
            item_type
        )
        
        print(f"Обсуждение багов сохранено в файл: {bug_discussion_file}")
    else:
        print("Отчеты о багах не найдены")
        bug_discussion_file = None

    # Шаг 5: Обработка запросов функций
    print("\n5. Обработка запросов новых функций...")
    if classified_reviews['feature_requests']['raw']:
        feature_personas = create_personas(
            classified_reviews['feature_requests']['raw'], 
            'feature_requests', 
            timestamp, 
            category
        )
        
        feature_discussion_file = run_category_discussion(
            feature_personas, 
            f"{item_name} (запросы функций)", 
            item_type
        )
        
        print(f"Обсуждение запросов функций сохранено в файл: {feature_discussion_file}")
    else:
        print("Запросы новых функций не найдены")
        feature_discussion_file = None
    
    # Шаг 6: Генерация финальных рекомендаций
    print("\n6. Генерация финальных рекомендаций...")
    recommendations_file = generate_recommendations(
        classified_reviews, bug_discussion_file, feature_discussion_file
    )
    
    print("\nАнализ завершен успешно!")
    print("\nСгенерированные файлы:")
    print(f"1. Отзывы: output/{reviews_file}")
    print(f"2. Классифицированные отзывы: output/{classified_file}")
    
    if bug_discussion_file:
        print(f"3. Обсуждение багов: output/{bug_discussion_file}")
    
    if feature_discussion_file:
        print(f"4. Обсуждение запросов функций: output/{feature_discussion_file}")
    
    if recommendations_file:
        print(f"5. Рекомендации: output/{recommendations_file}")

def analyze_reviews_topic(reviews):
    """Анализирует тему отзывов и определяет категорию товара/услуги и название
    
    Args:
        reviews: Список отзывов для анализа
        
    Returns:
        tuple: (category, item_type, item_name)
    """
    # Объединяем некоторые отзывы для анализа (не все, чтобы экономить токены)
    sample_reviews = reviews[:15]
    
    # Преобразуем словари в строки, если нужно
    review_texts = []
    for review in sample_reviews:
        if isinstance(review, dict) and 'text' in review:
            review_texts.append(review['text'])
        elif isinstance(review, str):
            review_texts.append(review)
    
    review_text = "\n\n".join(review_texts)
    
    # Ограничиваем длину текста
    if len(review_text) > 3000:
        review_text = review_text[:3000] + "..."
    
    prompt = f"""Проанализируй следующие отзывы о приложении и определи:
    1. Категорию приложения (например: health, lifestyle, productivity, social, и т.д.)
    2. Конкретный тип приложения (например: fitness tracker, meditation app, habit tracker и т.д.)
    3. Основное назначение приложения на основе отзывов
    
    Отзывы:
    {review_text}
    
    Верни ответ в формате JSON, строго следуя этой структуре:
    {{"category": "категория", "type": "тип_приложения", "name": "краткое_описание_назначения"}}
    """
    
    try:
        # Устанавливаем API ключ OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Делаем запрос к OpenAI для определения темы
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты - эксперт по анализу отзывов приложений. Всегда отвечай только в формате JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        # Получаем ответ и преобразуем его в JSON
        result_text = response.choices[0].message.content.strip()
        
        # Извлекаем JSON из ответа (иногда модель может добавить лишний текст)
        import re
        json_pattern = r'\{.*\}'
        json_match = re.search(json_pattern, result_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(0)
            result = json.loads(json_str)
        else:
            # Запасной вариант, если регулярное выражение не сработало
            try:
                result = json.loads(result_text)
            except:
                # Если всё ещё ошибка, используем значения по умолчанию
                result = {"category": "app", "type": "health", "name": "Sober App"}
        
        print(f"Определена тема отзывов: категория '{result['category']}', тип '{result['type']}', назначение '{result['name']}'")
        return (result['category'], result['type'], result['name'])
        
    except Exception as e:
        print(f"Ошибка при определении темы отзывов: {str(e)}")
        # Возвращаем значения по умолчанию в случае ошибки
        return ("app", "health", "Sober App")

def create_personas(reviews, category_name, timestamp, app_category="app"):
    """Создает персоны на основе отзывов из конкретной категории
    
    Args:
        reviews: Список отзывов
        category_name: Название категории отзывов
        timestamp: Временная метка для именования файлов
        app_category: Категория приложения
        
    Returns:
        list: Список созданных персон
    """
    print(f"\nСоздание персон на основе отзывов из категории '{category_name}'...")
    
    # Создаем генератор персон
    persona_gen = PersonaGenerator()
    
    # Разбиваем отзывы на две части для создания разных персон
    mid = len(reviews) // 2
    reviews_part1 = reviews[:mid]
    reviews_part2 = reviews[mid:]
    
    # Проверяем, не слишком ли много отзывов для анализа
    max_reviews_per_part = 100
    if len(reviews_part1) > max_reviews_per_part:
        print(f"Слишком много отзывов ({len(reviews_part1)}), ограничиваем до {max_reviews_per_part}")
        reviews_part1 = reviews_part1[:max_reviews_per_part]
    
    if len(reviews_part2) > max_reviews_per_part:
        print(f"Слишком много отзывов ({len(reviews_part2)}), ограничиваем до {max_reviews_per_part}")
        reviews_part2 = reviews_part2[:max_reviews_per_part]
    
    # Обрабатываем каждую часть
    personas = []
    
    for part, part_reviews in enumerate([reviews_part1, reviews_part2], 1):
        print(f"Обработка части {part}...")
        
        # Ограничиваем длину текста отзывов
        max_text_length = 10000
        all_text = ""
        for review in part_reviews:
            if isinstance(review, dict) and 'text' in review:
                all_text += review['text'] + " "
        if len(all_text) > max_text_length:
            print(f"Текст отзывов слишком длинный ({len(all_text)} символов), обрезаем до {max_text_length}")
        
        # Генерируем персону на основе отзывов
        persona = persona_gen.generate_persona(part_reviews, category=app_category)
        if persona:
            personas.append({
                'category': category_name,
                'part': part,
                'based_on_reviews': len(part_reviews),
                'persona': persona
            })
        else:
            print(f"Не удалось сгенерировать персону для категории {category_name}, часть {part}")
    
    # Сохраняем персоны в файл
    personas_file = f"personas_{category_name}_{timestamp}.json"
    with open(os.path.join('output', personas_file), 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'category': category_name,
            'total_personas': len(personas),
            'personas': personas
        }, f, ensure_ascii=False, indent=4)
    
    print(f"Персоны для категории '{category_name}' сохранены в файл: {personas_file}")
    return personas

def run_category_discussion(personas, discussion_topic, item_type):
    """Запускает групповую дискуссию для конкретной категории отзывов
    
    Args:
        personas: Список персон
        discussion_topic: Тема для обсуждения
        item_type: Тип объекта
        
    Returns:
        str: Имя файла с результатами дискуссии
    """
    print(f"\nЗапуск групповой дискуссии по теме '{discussion_topic}'...")
    
    # Преобразуем список персон в формат, ожидаемый функцией run_group_discussion
    personas_for_discussion = []
    for persona_data in personas:
        personas_for_discussion.append(persona_data['persona'])
    
    # Запускаем групповую дискуссию
    discussion_file = run_group_discussion(
        item_type=item_type,
        item_name=discussion_topic,
        custom_personas=personas_for_discussion
    )
    
    # Создаем резюме дискуссии
    summarizer = DiscussionSummarizer()
    summary = summarizer.summarize_discussion()
    
    return discussion_file

def generate_recommendations(classified_reviews, bug_discussion_file, feature_discussion_file):
    """Генерирует итоговые рекомендации на основе всех анализов
    
    Args:
        classified_reviews: Классифицированные отзывы
        bug_discussion_file: Файл с дискуссией по багам
        feature_discussion_file: Файл с дискуссией по функциям
        
    Returns:
        str: Имя файла с рекомендациями
    """
    print("\nГенерация итоговых рекомендаций...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    recommendations_file = f"recommendations_{timestamp}.json"
    
    # Собираем данные для анализа
    analysis_data = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'bug_reports': {
            'count': len(classified_reviews['bug_reports']['raw']),
            'summarized': classified_reviews['bug_reports']['summarized']
        },
        'feature_requests': {
            'count': len(classified_reviews['feature_requests']['raw']),
            'summarized': classified_reviews['feature_requests']['summarized']
        },
        'appreciation': {
            'count': len(classified_reviews['appreciation']['raw'])
        }
    }
    
    # Добавляем данные из дискуссий, если они есть
    bug_summary = None
    feature_summary = None
    
    if bug_discussion_file:
        try:
            # Получаем резюме дискуссии о багах
            with open(os.path.join('output', f"discussion_summary_{bug_discussion_file.split('_')[1].split('.')[0]}.txt"), 'r', encoding='utf-8') as f:
                bug_summary = f.read()
            analysis_data['bug_discussion_summary'] = bug_summary
        except Exception as e:
            print(f"Ошибка при чтении резюме дискуссии о багах: {str(e)}")
    
    if feature_discussion_file:
        try:
            # Получаем резюме дискуссии о функциях
            with open(os.path.join('output', f"discussion_summary_{feature_discussion_file.split('_')[1].split('.')[0]}.txt"), 'r', encoding='utf-8') as f:
                feature_summary = f.read()
            analysis_data['feature_discussion_summary'] = feature_summary
        except Exception as e:
            print(f"Ошибка при чтении резюме дискуссии о функциях: {str(e)}")
    
    # Генерируем рекомендации на основе всех данных
    try:
        analyzer = Recommendations()
        result_file = analyzer.analyze_from_classified_data(analysis_data)
        
        if result_file:
            print(f"Рекомендации сохранены в файл: {result_file}")
        else:
            print("Не удалось сгенерировать рекомендации")
            
        return result_file
            
    except Exception as e:
        print(f"Ошибка при генерации рекомендаций: {str(e)}")
        return None

if __name__ == "__main__":
    # Проверяем наличие API ключа
    if not os.getenv("OPENAI_API_KEY"):
        print("Ошибка: OPENAI_API_KEY не найден в переменных окружения")
    else:
        asyncio.run(run_sober_analysis()) 