import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

# Загружаем переменные окружения
load_dotenv()

class DiscussionSummarizer:
    def __init__(self):
        """Инициализация клиента OpenAI"""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def get_latest_discussion_file(self):
        """Находит самый свежий файл с результатами дискуссии"""
        files = [f for f in os.listdir() if f.startswith("mascara_discussion_")]
        if not files:
            raise FileNotFoundError("Файл с результатами дискуссии не найден.")
        return max(files, key=os.path.getctime)
    
    def load_discussion_data(self, file_path=None):
        """Загружает данные дискуссии из файла"""
        if not file_path:
            file_path = self.get_latest_discussion_file()
        
        print(f"Загрузка данных дискуссии из файла: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    
    def generate_abstractive_summary(self, discussion_data):
        """Генерирует абстрактное резюме дискуссии с ключевыми предложениями по улучшению товара"""
        # Собираем все высказывания из групповой дискуссии
        all_messages = []
        for message in discussion_data.get("group_discussion", []):
            # Добавляем имя агента к сообщению для лучшего понимания контекста
            agent_name = message.get("agent", "Unknown")
            content = message.get("content", "")
            all_messages.append(f"[{agent_name}]: {content}")
        
        # Объединяем все сообщения в одну строку для анализа
        full_discussion = "\n\n".join(all_messages)
        
        # Определяем тип продукта
        product_type = discussion_data.get("product_type", "mascara")
        topic = discussion_data.get("topic", "Критерии выбора продукта")
        
        # Формируем промпт в зависимости от типа продукта
        if product_type == "mascara":
            system_prompt = "Ты - эксперт по анализу групповых дискуссий о косметических продуктах и выделению ключевых инсайтов для улучшения туши для ресниц."
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
            system_prompt = "Ты - эксперт по анализу групповых дискуссий о мобильных приложениях и выделению ключевых инсайтов для улучшения пользовательского опыта."
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
            system_prompt = "Ты - эксперт по анализу групповых дискуссий и выделению ключевых инсайтов для улучшения продуктов."
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
            print(f"Ошибка при генерации резюме: {str(e)}")
            return None
    
    def summarize_discussion(self, file_path=None):
        """Основной метод для резюмирования дискуссии"""
        # Загрузка данных
        data = self.load_discussion_data(file_path)
        
        # Получаем тип продукта
        product_type = data.get("product_type", "mascara")
        
        # Генерация резюме
        print(f"Генерация абстрактного резюме дискуссии о продукте типа: {product_type}")
        summary = self.generate_abstractive_summary(data)
        
        if summary:
            # Сохранение результатов
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"discussion_summary_{timestamp}.txt"
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(summary)
            
            print(f"Резюме сохранено в файл: {output_file}")
            
            # Также выводим результат в консоль
            print("\nРЕЗЮМЕ ДИСКУССИИ:")
            print(summary)
            
            return output_file
        
        return None

if __name__ == "__main__":
    # Пример использования
    summarizer = DiscussionSummarizer()
    summarizer.summarize_discussion() 