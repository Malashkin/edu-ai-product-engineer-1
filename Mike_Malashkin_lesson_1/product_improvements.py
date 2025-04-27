import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

# Загружаем переменные окружения
load_dotenv()

class ProductImprovements:
    def __init__(self):
        """Инициализация клиента OpenAI"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY не найден в переменных окружения")
        self.client = OpenAI(api_key=api_key)
    
    def get_latest_discussion_file(self):
        """Находит самый свежий файл с результатами дискуссии"""
        files = [f for f in os.listdir() if f.startswith("mascara_discussion_")]
        if not files:
            raise FileNotFoundError("Файл с результатами дискуссии не найден")
        return max(files, key=os.path.getctime)
    
    def load_discussion_data(self, file_path=None):
        """Загружает данные дискуссии из файла"""
        if not file_path:
            file_path = self.get_latest_discussion_file()
        
        print(f"Загрузка данных дискуссии из файла: {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Ошибка при загрузке файла: {str(e)}")
            return None
    
    def generate_improvements(self, discussion_data):
        """Генерирует рекомендации по улучшению продукта на основе дискуссии"""
        if not discussion_data:
            print("Нет данных для анализа")
            return None
            
        # Собираем все высказывания из групповой дискуссии
        all_messages = []
        for message in discussion_data.get("group_discussion", []):
            # Добавляем имя агента к сообщению для лучшего понимания контекста
            agent_name = message.get("agent", "Unknown")
            content = message.get("content", "")
            all_messages.append(f"[{agent_name}]: {content}")
        
        if not all_messages:
            print("В дискуссии нет сообщений для анализа")
            return None
        
        # Объединяем все сообщения в одну строку для анализа
        full_discussion = "\n\n".join(all_messages)
        
        # Определяем тип продукта
        product_type = discussion_data.get("product_type", "mascara")
        topic = discussion_data.get("topic", "Критерии выбора продукта")
        
        # Формируем промпт в зависимости от типа продукта
        if product_type == "mascara":
            system_prompt = "Ты - эксперт по анализу групповых дискуссий о косметических продуктах и выделению ключевых инсайтов для улучшения туши для ресниц"
            prompt = f"""Проанализируй следующую групповую дискуссию о выборе туши для ресниц и 
            выдели 2-3 ключевых предложения по улучшению продукта.
            
            Особое внимание удели конкретным требованиям к кисточке, формуле туши и другим аспектам продукта.
            Выдели только самые значимые и повторяющиеся мнения участников дискуссии.
            
            Твой ответ должен быть в формате:
            
            КЛЮЧЕВЫЕ ПРЕДЛОЖЕНИЯ ПО УЛУЧШЕНИЮ ТУШИ ДЛЯ РЕСНИЦ:
            1. [Первое предложение]
            2. [Второе предложение]
            3. [Третье предложение, если есть]
            
            Дискуссия:
            {full_discussion}
            """
        elif product_type == "app":
            system_prompt = "Ты - эксперт по анализу групповых дискуссий о мобильных приложениях и выделению ключевых инсайтов для улучшения пользовательского опыта"
            prompt = f"""Проанализируй следующую групповую дискуссию о мобильных приложениях и 
            выдели 2-3 ключевых предложения по улучшению продукта.
            
            Особое внимание удели конкретным требованиям к интерфейсу, функциональности и другим аспектам мобильного приложения.
            Выдели только самые значимые и повторяющиеся мнения участников дискуссии.
            
            Твой ответ должен быть в формате:
            
            КЛЮЧЕВЫЕ ПРЕДЛОЖЕНИЯ ПО УЛУЧШЕНИЮ МОБИЛЬНОГО ПРИЛОЖЕНИЯ:
            1. [Первое предложение]
            2. [Второе предложение]
            3. [Третье предложение, если есть]
            
            Дискуссия:
            {full_discussion}
            """
        else:
            system_prompt = "Ты - эксперт по анализу групповых дискуссий и выделению ключевых инсайтов для улучшения продуктов"
            prompt = f"""Проанализируй следующую групповую дискуссию на тему "{topic}" и 
            выдели 2-3 ключевых предложения по улучшению продукта.
            
            Особое внимание удели конкретным требованиям и аспектам продукта, упомянутым в дискуссии.
            Выдели только самые значимые и повторяющиеся мнения участников дискуссии.
            
            Твой ответ должен быть в формате:
            
            КЛЮЧЕВЫЕ ПРЕДЛОЖЕНИЯ ПО УЛУЧШЕНИЮ ПРОДУКТА:
            1. [Первое предложение]
            2. [Второе предложение]
            3. [Третье предложение, если есть]
            
            Дискуссия:
            {full_discussion}
            """
        
        # Отправляем запрос к OpenAI
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Ошибка при генерации рекомендаций: {str(e)}")
            return None
    
    def analyze_discussion(self, file_path=None):
        """Основной метод для анализа дискуссии и генерации рекомендаций"""
        try:
            # Загрузка данных
            data = self.load_discussion_data(file_path)
            if not data:
                return None
            
            # Получаем тип продукта
            product_type = data.get("product_type", "mascara")
            
            # Генерация рекомендаций
            print(f"Генерация рекомендаций по улучшению продукта типа: {product_type}")
            improvements = self.generate_improvements(data)
            
            if improvements:
                # Сохранение результатов
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"product_improvements_{timestamp}.txt"
                
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(improvements)
                
                print(f"Рекомендации сохранены в файл: {output_file}")
                
                # Также выводим результат в консоль
                print("\nРЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ ПРОДУКТА:")
                print(improvements)
                
                return output_file
            
            return None
            
        except Exception as e:
            print(f"Ошибка при анализе дискуссии: {str(e)}")
            return None

if __name__ == "__main__":
    # Пример использования
    analyzer = ProductImprovements()
    analyzer.analyze_discussion() 