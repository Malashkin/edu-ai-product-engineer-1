import os
import json
from datetime import datetime
from scraper import ReviewScraper
from summarization import summarize_reviews
from persona_generator import PersonaGenerator
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Список URL для парсинга
URLS_TO_SCRAPE = [
    "https://www.parfum-lider.ru/catalog/makiyazh/glaza_makiyazh/tush_dlya_resnits/13953/",
    "https://www.podrygka.ru/catalog/makiyazh/glaza/tush/24454-tush_dlya_resnits_loreal_telescopic_chernaya_udlinyayushchaya/",
    "https://rivegauche.ru/product/loreal-paris-volume-million-lashes-panorama-mascara/reviews"
]

def save_results(results, raw_filename, reviews_filename):
    """Save results in two files: raw data and extracted reviews"""
    # Сохраняем сырые данные
    with open(raw_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    
    # Формируем структуру для отзывов
    reviews_by_site = {}
    total_reviews = 0
    
    for result in results:
        site_url = result['url']
        site_name = site_url.split('/')[2]  # Получаем домен сайта
        
        reviews_by_site[site_name] = {
            'url': site_url,
            'reviews_count': result['reviews_count'],
            'reviews': result['reviews']
        }
        total_reviews += result['reviews_count']
    
    reviews_data = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'total_sites': len(results),
        'total_reviews': total_reviews,
        'sites': reviews_by_site
    }
    
    # Сохраняем структурированные отзывы
    with open(reviews_filename, 'w', encoding='utf-8') as f:
        json.dump(reviews_data, f, ensure_ascii=False, indent=4)

def process_urls(urls):
    """Process multiple URLs and return combined results"""
    all_results = []
    scraper = ReviewScraper()
    
    for url in urls:
        print(f"\nScraping reviews from {url}...")
        result = scraper.get_reviews(url)
        
        if result:
            print(f"Successfully scraped content from {url}")
            print(f"Found {result['reviews_count']} reviews")
            all_results.append(result)
        else:
            print(f"Failed to scrape content from {url}")
    
    return all_results if all_results else None

def chunk_list(lst, n):
    """Разбивает список на подсписки размером n"""
    return [lst[i:i + n] for i in range(0, len(lst), n)]

def split_list_in_half(lst):
    """Разделяет список на две равные части"""
    half = len(lst) // 2
    return lst[:half], lst[half:]

def process_site_reviews(site_name, reviews, timestamp):
    """Обработка отзывов одного сайта"""
    print(f"\nProcessing reviews from {site_name}...")
    
    # Разделяем отзывы на две части
    reviews_part1, reviews_part2 = split_list_in_half(reviews)
    
    # Обрабатываем каждую часть отдельно
    all_summaries = []
    all_personas = []
    
    for part_num, reviews_part in enumerate([reviews_part1, reviews_part2], 1):
        print(f"\nProcessing part {part_num} ({len(reviews_part)} reviews)...")
        
        # Создаем группы по 3 отзыва для суммаризации
        review_groups = chunk_list(reviews_part, 3)
        summaries = []
        
        for i, group in enumerate(review_groups, 1):
            print(f"Summarizing group {i}/{len(review_groups)}...")
            summary = summarize_reviews(group)
            if summary:
                summaries.append(summary)
        
        all_summaries.extend(summaries)
        
        # Генерируем персону на основе всех саммари этой части
        print(f"Generating persona for part {part_num}...")
        generator = PersonaGenerator()
        reviews_for_persona = [{'text': s['summary']} for s in summaries]
        persona = generator.generate_persona(reviews_for_persona)
        
        if persona:
            all_personas.append({
                'site': site_name,
                'part': part_num,
                'based_on_reviews': len(reviews_part),
                'based_on_summaries': len(summaries),
                'persona': persona
            })
    
    return all_summaries, all_personas

def main():
    """Main entry point for the project."""
    print("Starting the review analysis pipeline...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Шаг 1: Скрапинг отзывов
    print("\n1. Scraping reviews...")
    if URLS_TO_SCRAPE:
        results = process_urls(URLS_TO_SCRAPE)
        if results:
            raw_file = f"raw_scraping_{timestamp}.json"
            reviews_file = f"reviews_{timestamp}.json"
            save_results(results, raw_file, reviews_file)
            print(f"Raw scraping data saved to: {raw_file}")
            print(f"Extracted reviews saved to: {reviews_file}")
        else:
            print("No content was scraped.")
            return
    else:
        print("No URLs provided for scraping.")
        return

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
    
    print("\nPipeline completed successfully!")
    print("\nGenerated files:")
    print(f"1. Raw scraping data: {raw_file}")
    print(f"2. Extracted reviews: {reviews_file}")
    print(f"3. Summaries: {summaries_file}")
    print(f"4. Personas (2 per site): {personas_file}")

if __name__ == "__main__":
    main() 