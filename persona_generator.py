import json
import os
import openai
from datetime import datetime

class PersonaGenerator:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
    def generate_persona(self, reviews):
        """Generate persona based on reviews using OpenAI API"""
        # Формируем промпт для OpenAI
        prompt = f"""На основе следующих отзывов создай персону покупателя по следующей структуре:
        Имя:
        Возраст:
        Пол:
        Профессия:
        Образ жизни и ценности:
        Основные потребности:
        - потребность 1
        - потребность 2
        - потребность 3
        Боли/тревоги:

        Отзывы для анализа:
        {json.dumps(reviews, ensure_ascii=False, indent=2)}

        Ответ должен быть строго в указанном формате, без дополнительных комментариев.
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты - эксперт по анализу потребительского поведения и созданию персон."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message['content']
            
        except Exception as e:
            print(f"Error generating persona: {str(e)}")
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