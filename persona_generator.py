import json
import os
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class PersonaGenerator:
    def __init__(self):
        """Инициализация клиента OpenAI"""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def generate_persona(self, reviews):
        """Генерирует персону на основе отзывов"""
        # Объединяем все отзывы в один текст
        reviews_text = "\n\n".join([f"Отзыв {i+1}: {review}" for i, review in enumerate(reviews)])
        
        # Формируем промпт для генерации персоны
        prompt = f"""На основе следующих отзывов о туши для ресниц, создай детальный портрет типичного покупателя.
        
        Включи в описание:
        1. Демографические характеристики (возраст, пол, социальный статус)
        2. Потребности и болевые точки
        3. Критерии выбора продукта
        4. Предпочтения в использовании
        5. Ожидания от продукта
        
        Отзывы:
        {reviews_text}
        
        Создай подробное описание персоны, которое отражает общие характеристики и потребности, 
        выявленные из анализа отзывов."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Ты - эксперт по анализу потребительского поведения и созданию портретов целевой аудитории."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating persona: {str(e)}")
            return None

    def generate_reviews_summary(self, reviews):
        """Generate a summary of reviews using OpenAI API"""
        # Извлекаем только текст отзывов
        reviews_text = []
        for review in reviews:
            if isinstance(review, dict):
                text = review.get('text', '')
                if text and not text.startswith('Комментарий:') and not text.startswith('Отзывы') and not text.startswith('Срок использования:'):
                    reviews_text.append(text)
            elif isinstance(review, str):
                if not review.startswith('Комментарий:') and not review.startswith('Отзывы') and not review.startswith('Срок использования:'):
                    reviews_text.append(review)
        
        # Формируем промпт для OpenAI
        prompt = f"""Проанализируй следующие отзывы о туши для ресниц и создай краткое саммари, 
        которое описывает основные тенденции в отзывах, включая:
        - Общее впечатление пользователей
        - Основные положительные моменты
        - Основные отрицательные моменты
        - Часто упоминаемые характеристики продукта

        Отзывы для анализа:
        {' | '.join(reviews_text)}

        Ответ должен быть в виде связного текста на русском языке, без заголовков и списков.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты - эксперт по анализу потребительских отзывов. Твоя задача - создавать четкие и информативные обзоры на основе отзывов покупателей."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return None

    def process_reviews_batch(self, reviews_file, batch_size=15):
        """Process reviews in batches and generate personas"""
        # Загружаем отзывы
        with open(reviews_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        personas = []
        persona_number = 1
        
        # Обрабатываем отзывы по каждому сайту
        for site_name, site_data in data['sites'].items():
            reviews = site_data['reviews']
            
            # Разбиваем отзывы на группы по batch_size
            for i in range(0, len(reviews), batch_size):
                batch = reviews[i:i + batch_size]
                
                # Генерируем персону для текущей группы отзывов
                persona = self.generate_persona(batch)
                if persona:
                    personas.append({
                        'persona_number': persona_number,
                        'site': site_name,
                        'reviews_range': f"{i+1}-{min(i+batch_size, len(reviews))}",
                        'persona': persona
                    })
                    persona_number += 1
        
        # Сохраняем результаты
        if personas:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"personas_{timestamp}.json"
            
            result = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'total_personas': len(personas),
                'personas': personas
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            
            print(f"\nGenerated {len(personas)} personas")
            print(f"Results saved to: {output_file}")
            
        return personas

if __name__ == "__main__":
    # Пример использования
    generator = PersonaGenerator()
    generator.process_reviews_batch("reviews_20250424_155400.json") 