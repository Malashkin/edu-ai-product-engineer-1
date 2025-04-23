import os
import json
from datetime import datetime
from scraper import ReviewScraper

# Список URL для парсинга
URLS_TO_SCRAPE = [
    "https://www.parfum-lider.ru/catalog/makiyazh/glaza_makiyazh/tush_dlya_resnits/13953/",
    "https://www.podrygka.ru/catalog/ukhod/litso/dlya_snyatiya_makiyazha/139046-mitsellyarnaya_voda_eveline_facemed_3_v_1_gialuronovaya_400_ml/",
    "https://rivegauche.ru/product/payot-nue-lotion-tonique-eclat-200/reviews"
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

def main():
    """Main entry point for the project."""
    print("Starting the scraping project...")
    
    # Если есть URL для парсинга, используем скрапер
    if URLS_TO_SCRAPE:
        results = process_urls(URLS_TO_SCRAPE)
        if results:
            # Генерируем имена файлов с текущей датой и временем
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            raw_file = f"raw_scraping_{timestamp}.json"
            reviews_file = f"reviews_{timestamp}.json"
            
            # Сохраняем результаты
            save_results(results, raw_file, reviews_file)
            
            print(f"\nRaw scraping data saved to: {raw_file}")
            print(f"Extracted reviews saved to: {reviews_file}")
            print(f"Total sites processed successfully: {len(results)}")
        else:
            print("No content was scraped.")
    else:
        print("No URLs provided for scraping.")
    
    print("\nProject completed!")

if __name__ == "__main__":
    main() 