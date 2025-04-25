import asyncio
import json
import os
from datetime import datetime
from scraper import ReviewScraper
from persona_generator import PersonaGenerator
from examples.group_discussion import run_group_discussion
from summarizer import DiscussionSummarizer
from dotenv import load_dotenv
from product_improvements import ProductImprovements

# Загружаем переменные окружения
load_dotenv()

# Список URL для парсинга
URLS_TO_SCRAPE = [
    "https://www.parfum-lider.ru/catalog/makiyazh/glaza_makiyazh/tush_dlya_resnits/13953/",
    "https://www.podrygka.ru/catalog/makiyazh/glaza/tush/24454-tush_dlya_resnits_loreal_telescopic_chernaya_udlinyayushchaya/",
    "https://rivegauche.ru/product/loreal-paris-volume-million-lashes-panorama-mascara/reviews"
]

def process_urls(urls):
    """Process multiple URLs and return combined results"""
    results = {}
    scraper = ReviewScraper()
    
    for url in urls:
        print(f"\nScraping reviews from {url}...")
        site_name = url.split('/')[2]  # Получаем домен сайта
        result = scraper.get_reviews(url)
        
        if result:
            print(f"Successfully scraped content from {url}")
            print(f"Found {len(result['reviews'])} reviews")
            results[site_name] = result
        else:
            print(f"Failed to scrape content from {url}")
    
    scraper.cleanup()
    return results if results else None

def save_results(results, raw_file, reviews_file):
    """Save scraping results to files."""
    # Сохраняем сырые данные
    with open(raw_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    
    # Извлекаем и сохраняем только отзывы
    reviews = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'sites': {}
    }
    
    for site_name, site_data in results.items():
        reviews['sites'][site_name] = {
            'total_reviews': len(site_data['reviews']),
            'reviews': site_data['reviews']
        }
    
    with open(reviews_file, 'w', encoding='utf-8') as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)

def process_site_reviews(site_name, reviews, timestamp):
    """Process reviews for a single site."""
    print(f"\nProcessing reviews for {site_name}...")
    
    # Создаем генератор персон для сайта
    persona_gen = PersonaGenerator()
    
    # Разбиваем отзывы на две части
    mid = len(reviews) // 2
    reviews_part1 = reviews[:mid]
    reviews_part2 = reviews[mid:]
    
    # Обрабатываем каждую часть
    summaries = []
    personas = []
    
    for part, part_reviews in enumerate([reviews_part1, reviews_part2], 1):
        print(f"Processing part {part}...")
        
        # Генерируем саммари для части отзывов
        summary = persona_gen.generate_reviews_summary(part_reviews)
        summaries.append({
            'site': site_name,
            'part': part,
            'based_on_reviews': len(part_reviews),
            'summary': summary
        })
        
        # Генерируем персону на основе отзывов
        persona = persona_gen.generate_persona(part_reviews)
        personas.append({
            'site': site_name,
            'part': part,
            'based_on_reviews': len(part_reviews),
            'based_on_summaries': 1,
            'persona': persona
        })
    
    return summaries, personas

def use_test_personas():
    """Использовать тестовые персоны, если скрапинг не удался"""
    # Проверяем существует ли файл тестовых персон
    if not os.path.exists("personas_test.json"):
        from test_discussion import create_test_personas
        create_test_personas()
        
    with open("personas_test.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    personas_file = f"personas_{timestamp}.json"
        
    # Копируем данные в новый файл с текущим timestamp
    with open(personas_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"\nИспользуем тестовые персоны. Сохранено в файл: {personas_file}")
    return data["personas"]

async def run_pipeline():
    """Main entry point for the project."""
    print("Starting the review analysis pipeline...")
    
    # Текущий timestamp для именования файлов
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    use_test_data = False
    
    # Шаг 1: Скрапинг отзывов
    print("\n1. Scraping reviews...")
    results = process_urls(URLS_TO_SCRAPE)
    
    if not results:
        print("No content was scraped.")
        print("Используем тестовые данные...")
        use_test_data = True
        all_personas = use_test_personas()
    else:
        raw_file = f"raw_scraping_{timestamp}.json"
        reviews_file = f"reviews_{timestamp}.json"
        save_results(results, raw_file, reviews_file)
        print(f"Raw scraping data saved to: {raw_file}")
        print(f"Extracted reviews saved to: {reviews_file}")
        
        # Загружаем отзывы для обработки
        with open(reviews_file, 'r', encoding='utf-8') as f:
            reviews_data = json.load(f)
        
        all_summaries = []
        all_personas = []
        
        # Обрабатываем каждый сайт отдельно
        for site_name, site_data in reviews_data['sites'].items():
            site_summaries, site_personas = process_site_reviews(
                site_name, 
                site_data['reviews'],
                timestamp
            )
            all_summaries.extend(site_summaries)
            all_personas.extend(site_personas)
        
        # Сохраняем все саммари
        summaries_file = f"summaries_{timestamp}.json"
        with open(summaries_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'total_summaries': len(all_summaries),
                'summaries_by_site': all_summaries
            }, f, ensure_ascii=False, indent=4)
    
        # Сохраняем все персоны
        personas_file = f"personas_{timestamp}.json"
        with open(personas_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'total_personas': len(all_personas),
                'personas': all_personas
            }, f, ensure_ascii=False, indent=4)
    
    # Шаг 2: Проведение групповой дискуссии
    print("\n2. Запуск групповой дискуссии...")
    discussion_file = run_group_discussion()
    
    # Шаг 3: Создание абстрактного резюме дискуссии
    print("\n3. Создание резюме с ключевыми предложениями...")
    summarizer = DiscussionSummarizer()
    summary = summarizer.summarize_discussion()
    
    # Шаг 4: Генерация рекомендаций по улучшению продукта
    print("\n4. Генерация рекомендаций по улучшению продукта...")
    try:
        analyzer = ProductImprovements()
        result_file = analyzer.analyze_discussion()
        
        if result_file:
            print(f"Рекомендации сохранены в файл: {result_file}")
        else:
            print("Не удалось сгенерировать рекомендации")
            
    except Exception as e:
        print(f"Ошибка при генерации рекомендаций: {str(e)}")
    
    print("\nПайплайн завершен успешно!")
    print("\nСгенерированные файлы:")
    if not use_test_data:
        print(f"1. Raw scraping data: raw_scraping_{timestamp}.json")
        print(f"2. Extracted reviews: reviews_{timestamp}.json")
        print(f"3. Summaries: summaries_{timestamp}.json")
    print(f"4. Personas: personas_{timestamp}.json")
    print(f"5. Discussion results: mascara_discussion_{timestamp}.json")
    if result_file:
        print(f"6. Product improvements: {result_file}")

if __name__ == "__main__":
    # Проверяем наличие API ключа
    if not os.getenv("OPENAI_API_KEY"):
        print("Ошибка: OPENAI_API_KEY не найден в переменных окружения")
    else:
        asyncio.run(run_pipeline()) 