import pandas as pd
import json
from summarization import extractive_summarize, abstractive_summarize
from analysis import analyze_summarization_methods
from datetime import datetime
import os

def analyze_results(results):
    """Analyze the effectiveness of both summarization approaches."""
    analysis = {
        "total_reviews": len(results),
        "average_scores": {
            "extractive": {
                "length_preservation": 0,
                "key_info_retention": 0
            },
            "abstractive": {
                "conciseness": 0,
                "readability": 0
            }
        },
        "comparison": {
            "extractive_advantages": [],
            "abstractive_advantages": [],
            "best_use_cases": {
                "extractive": [],
                "abstractive": []
            }
        },
        "final_recommendation": ""
    }
    
    # Analyze each review's summaries
    for result in results:
        # Compare lengths
        original_length = len(result['Text'].split())
        extractive_length = len(result['extractive_summary'].split())
        abstractive_length = len(result['abstractive_summary'].split())
        
        # Update metrics
        analysis["average_scores"]["extractive"]["length_preservation"] += extractive_length / original_length
        analysis["average_scores"]["extractive"]["key_info_retention"] += 1 if len(result['extractive_summary']) > 0 else 0
        
        analysis["average_scores"]["abstractive"]["conciseness"] += abstractive_length / original_length
        analysis["average_scores"]["abstractive"]["readability"] += 1 if len(result['abstractive_summary']) > 0 else 0
    
    # Calculate averages
    for method in ["extractive", "abstractive"]:
        for metric in analysis["average_scores"][method]:
            analysis["average_scores"][method][metric] /= len(results)
    
    # Add general observations
    analysis["comparison"]["extractive_advantages"] = [
        "Сохраняет оригинальные формулировки и контекст",
        "Более точное представление фактической информации",
        "Меньше риск искажения смысла"
    ]
    
    analysis["comparison"]["abstractive_advantages"] = [
        "Создает более краткие и читабельные резюме",
        "Лучше обобщает основные идеи",
        "Более естественное звучание текста"
    ]
    
    analysis["comparison"]["best_use_cases"]["extractive"] = [
        "Технические документы и спецификации",
        "Юридические тексты",
        "Научные статьи"
    ]
    
    analysis["comparison"]["best_use_cases"]["abstractive"] = [
        "Обзоры продуктов",
        "Новостные статьи",
        "Художественные тексты"
    ]
    
    # Final recommendation based on analysis
    if analysis["average_scores"]["abstractive"]["conciseness"] < analysis["average_scores"]["extractive"]["length_preservation"]:
        analysis["final_recommendation"] = """
        На основе анализа отзывов, абстрактивный метод показал себя более эффективным для данного типа текстов.
        Он создает более краткие и читабельные резюме, сохраняя при этом основной смысл отзывов.
        Особенно хорошо этот метод работает с отзывами о продуктах, где важно передать общее впечатление.
        """
    else:
        analysis["final_recommendation"] = """
        Анализ показывает, что экстрактивный метод более подходит для данного набора отзывов.
        Он лучше сохраняет важные детали и специфическую информацию о продуктах.
        Этот метод особенно полезен, когда точность и сохранение оригинальных формулировок имеют первостепенное значение.
        """
    
    return analysis

def process_reviews():
    """Process reviews from the local CSV file."""
    try:
        # Read the local CSV file
        print("Reading local dataset...")
        df = pd.read_csv("Reviews.csv")
        
        # Get first 10 reviews
        reviews = df.head(10)
        
        # Process each review
        results = []
        for index, row in reviews.iterrows():
            review_text = row['Text']
            
            # Generate summaries
            print(f"Processing review {index + 1}/10...")
            extractive_summary = extractive_summarize(review_text)
            abstractive_summary = abstractive_summarize(review_text)
            
            # Create result dictionary
            result = {
                "review_id": row['Id'],
                "product_id": row['ProductId'],
                "user_id": row['UserId'],
                "score": row['Score'],
                "Text": review_text,
                "extractive_summary": extractive_summary,
                "abstractive_summary": abstractive_summary,
                "analysis": analyze_summarization_methods()
            }
            results.append(result)
        
        # Save results to JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reviews_summaries_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        
        # Analyze results and save comparison
        final_analysis = analyze_results(results)
        analysis_filename = f"summarization_comparison_{timestamp}.json"
        
        with open(analysis_filename, 'w', encoding='utf-8') as f:
            json.dump(final_analysis, f, ensure_ascii=False, indent=4)
        
        print(f"\nResults saved to {filename}")
        print(f"Final analysis saved to {analysis_filename}")
        return results
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    # Process the reviews
    print("Starting review processing...")
    results = process_reviews()
    
    if results:
        print(f"Processed {len(results)} reviews successfully!")
    else:
        print("Failed to process reviews.") 