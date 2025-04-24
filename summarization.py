import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def summarize_reviews(reviews):
    """Generate an abstractive summary for multiple reviews using OpenAI API."""
    openai.api_key = os.getenv('OPENAI_API_KEY')
    
    # Объединяем тексты отзывов
    combined_reviews = "\n".join([review['text'] for review in reviews])
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты - эксперт по анализу отзывов. Твоя задача - создать один общий отзыв на основе нескольких отзывов, сохраняя ключевые моменты и общее впечатление."},
                {"role": "user", "content": f"Создай один общий отзыв на основе следующих отзывов, объединив ключевые моменты и впечатления:\n\n{combined_reviews}"}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return {
            'original_reviews': reviews,
            'summary': response.choices[0].message['content'].strip()
        }
        
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        return None 