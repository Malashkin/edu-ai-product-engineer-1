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

    # Шаг 2: Суммаризация отзывов (по 3 отзыва)
    print("\n2. Summarizing reviews (5 reviews per summary)...")
    with open(reviews_file, 'r', encoding='utf-8') as f:
        reviews_data = json.load(f)
    
    all_reviews = []
    for site_data in reviews_data['sites'].values():
        all_reviews.extend(site_data['reviews'])
    
    # Разбиваем отзывы на группы по 5
    review_groups = chunk_list(all_reviews, 5)
    summaries = []
    
    for i, group in enumerate(review_groups, 1):
        print(f"Summarizing group {i}/{len(review_groups)}...")
        summary = summarize_reviews(group)
        if summary:
            summaries.append(summary)
    
    # Сохраняем суммаризированные отзывы
    summaries_file = f"summaries_{timestamp}.json"
    with open(summaries_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_summaries': len(summaries),
            'summaries': summaries
        }, f, ensure_ascii=False, indent=4)
    print(f"Summaries saved to: {summaries_file}")
    
    # Шаг 3: Генерация персон (каждые 5 суммаризированных отзывов)
    print("\n3. Generating personas (5 summaries per persona)...")
    summary_groups = chunk_list(summaries, 5)
    personas = []
    generator = PersonaGenerator()
    
    for i, group in enumerate(summary_groups, 1):
        print(f"Generating persona {i}/{len(summary_groups)}...")
        # Создаем список отзывов для генерации персоны
        reviews_for_persona = [{'text': summary['summary']} for summary in group]
        persona = generator.generate_persona(reviews_for_persona)
        if persona:
            personas.append({
                'persona_number': i,
                'based_on_summaries': len(group),
                'persona': persona
            })
    
    # Сохраняем персоны
    personas_file = f"personas_{timestamp}.json"
    with open(personas_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_personas': len(personas),
            'personas': personas
        }, f, ensure_ascii=False, indent=4)
    
    print("\nPipeline completed successfully!")
    print("\nGenerated files:")
    print(f"1. Raw scraping data: {raw_file}")
    print(f"2. Extracted reviews: {reviews_file}")
    print(f"3. Summaries (3 reviews per summary): {summaries_file}")
    print(f"4. Personas (5 summaries per persona): {personas_file}")

if __name__ == "__main__":
    main() 