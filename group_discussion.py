import json
import glob
import os
import asyncio
from agents.agent import Agent
from agents.runner import Runner
from dotenv import load_dotenv
import openai
from datetime import datetime

# Загружаем переменные окружения
load_dotenv()

class ItemType:
    """Определение типа объекта отзывов и генерация соответствующих вопросов"""
    COSMETICS = "cosmetics"
    APP = "app"
    ELECTRONICS = "electronics"
    OTHER = "other"
    
    @staticmethod
    def determine_item_type(personas):
        """Определяет тип объекта отзывов на основе персон и информации из предыдущего этапа.
        
        Если в файле с персонами указан тип объекта, берем его.
        Иначе пытаемся определить из текста персон.
        """
        try:
            # Проверяем, есть ли в файле с персонами информация о типе объекта
            latest_file = get_latest_personas_file()
            with open(os.path.join('output', latest_file), 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Если в файле указан тип объекта, используем его
            if 'item_type' in data:
                item_type = data['item_type'].lower()
                
                # Преобразуем в константу класса
                if item_type in ["cosmetics", "makeup"]:
                    print(f"Определен тип объекта: косметика ({item_type})")
                    return ItemType.COSMETICS
                elif item_type in ["app", "mobile_app", "application", "software"]:
                    print(f"Определен тип объекта: приложение ({item_type})")
                    return ItemType.APP
                elif item_type in ["electronics", "gadget", "device"]:
                    print(f"Определен тип объекта: электроника ({item_type})")
                    return ItemType.ELECTRONICS
                else:
                    print(f"Определен тип объекта: другой тип ({item_type})")
                    return ItemType.OTHER
        except Exception as e:
            print(f"Ошибка при получении типа объекта из файла: {str(e)}")
        
        # Инициализация клиента OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Формируем текст для анализа
        persona_samples = []
        for i, persona in enumerate(personas[:2]):  # Берем первые две персоны для анализа
            persona_samples.append(persona.get('persona', ''))
        
        combined_text = "\n\n".join(persona_samples)
        
        # Формируем промпт для определения типа объекта
        prompt = f"""Определи, о каком типе объекта идет речь в следующих описаниях персон:

{combined_text}

Выбери один из вариантов:
1. Косметика или средства ухода
2. Мобильное приложение или программное обеспечение
3. Электроника или гаджеты
4. Другой тип объекта

Ответь только номером варианта."""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты - аналитик, который определяет тип объекта по описаниям персон потребителей."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=10
            )
            
            answer = response.choices[0].message.content.strip()
            
            if "1" in answer:
                print("Определен тип объекта: косметика/средства ухода")
                return ItemType.COSMETICS
            elif "2" in answer:
                print("Определен тип объекта: мобильное приложение/ПО")
                return ItemType.APP
            elif "3" in answer:
                print("Определен тип объекта: электроника/гаджеты")
                return ItemType.ELECTRONICS
            else:
                print("Определен тип объекта: другой тип")
                return ItemType.OTHER
                
        except Exception as e:
            print(f"Ошибка при определении типа объекта: {str(e)}")
            # По умолчанию возвращаем тип Other
            return ItemType.OTHER
    
    @staticmethod
    def get_questions(item_type, item_name=None):
        """Возвращает вопросы для индивидуального опроса и для групповой дискуссии"""
        # Используем обобщенное название, если конкретное не указано
        item_display_name = item_name or "этого объекта"
        
        # Конвертируем возможные None в строки
        if item_type is None:
            item_type = ItemType.OTHER
            
        if not item_display_name or item_display_name.lower() == "none":
            item_display_name = "этого объекта"
        
        # Генерируем вопросы на основе типа объекта
        if item_type == ItemType.COSMETICS:
            individual_question = f"Что для вас важно при выборе {item_display_name}? Расскажите о ваших предпочтениях и критериях выбора косметики."
            group_prompt = f"""Вы участвуете в групповой дискуссии о выборе {item_display_name}. 
            Вопрос для обсуждения: "Какие критерии выбора {item_display_name} наиболее важны и почему?"
            
            Поделитесь своим мнением и опытом, а затем задайте вопрос или прокомментируйте ответ другого участника.
            Оставайтесь в характере вашей персоны, опирайтесь на свои потребности и болевые точки.
            
            При обращении к другим участникам, используйте их имена в квадратных скобках, например [Имя_участника].
            
            Если вы считаете, что другой участник лучше ответит на конкретный вопрос - передайте ему слово."""
            
        elif item_type == ItemType.APP:
            individual_question = f"Что для вас важно при выборе и использовании {item_display_name}? Расскажите о ваших предпочтениях и критериях оценки."
            group_prompt = f"""Вы участвуете в групповой дискуссии о приложениях. 
            Вопрос для обсуждения: "Какие функции и характеристики {item_display_name} наиболее важны для пользователей и почему?"
            
            Поделитесь своим мнением и опытом, а затем задайте вопрос или прокомментируйте ответ другого участника.
            Оставайтесь в характере вашей персоны, опирайтесь на свои потребности и болевые точки.
            
            При обращении к другим участникам, используйте их имена в квадратных скобках, например [Имя_участника].
            
            Если вы считаете, что другой участник лучше ответит на конкретный вопрос - передайте ему слово."""
            
        elif item_type == ItemType.ELECTRONICS:
            individual_question = f"Что для вас важно при выборе {item_display_name}? Расскажите о ваших предпочтениях и критериях выбора электроники."
            group_prompt = f"""Вы участвуете в групповой дискуссии о выборе {item_display_name}. 
            Вопрос для обсуждения: "Какие характеристики и функции {item_display_name} наиболее важны и почему?"
            
            Поделитесь своим мнением и опытом, а затем задайте вопрос или прокомментируйте ответ другого участника.
            Оставайтесь в характере вашей персоны, опирайтесь на свои потребности и болевые точки.
            
            При обращении к другим участникам, используйте их имена в квадратных скобках, например [Имя_участника].
            
            Если вы считаете, что другой участник лучше ответит на конкретный вопрос - передайте ему слово."""
        else:
            individual_question = f"Что для вас важно при выборе {item_display_name}? Расскажите о ваших предпочтениях и критериях выбора."
            group_prompt = f"""Вы участвуете в групповой дискуссии о выборе {item_display_name}. 
            Вопрос для обсуждения: "Какие критерии выбора {item_display_name} наиболее важны и почему?"
            
            Поделитесь своим мнением и опытом, а затем задайте вопрос или прокомментируйте ответ другого участника.
            Оставайтесь в характере вашей персоны, опирайтесь на свои потребности и болевые точки.
            
            При обращении к другим участникам, используйте их имена в квадратных скобках, например [Имя_участника].
            
            Если вы считаете, что другой участник лучше ответит на конкретный вопрос - передайте ему слово."""
        
        return individual_question, group_prompt

def get_latest_personas_file():
    """Находит самый свежий файл с персонами"""
    files = [f for f in os.listdir('output') if f.startswith("personas_")]
    if not files:
        raise FileNotFoundError("Файл с персонами не найден. Сначала запустите main.py")
    return max(files, key=lambda x: os.path.getctime(os.path.join('output', x)))

def load_personas():
    """Загружает персоны из последнего сгенерированного файла"""
    print("\nПоиск файла с персонами...")
    latest_file = get_latest_personas_file()
    print(f"Загрузка персон из файла: {latest_file}")
    
    with open(os.path.join('output', latest_file), 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('personas', [])

def create_agent_from_persona(persona, item_type):
    """Создает агента на основе данных персоны"""
    # Проверяем наличие персоны и ее данных
    if not persona or 'persona' not in persona or not persona['persona']:
        print(f"Пропускаю создание агента для персоны {persona.get('site', 'unknown')}_{persona.get('part', 'unknown')}, так как данные персоны отсутствуют")
        return None
        
    # Формируем имя агента из сайта и части
    agent_name = f"Persona_{persona['site']}_{persona['part']}"
    print(f"\nСоздание агента: {agent_name}")
    
    # Формируем универсальную роль агента
    role_template = """You are a customer persona with the following characteristics:
{persona}

When discussing preferences and criteria, always stay in character and base your responses
on your persona's characteristics, lifestyle, needs, and pain points.

In the group discussion, you can refer to other participants by using their full names in brackets like [Persona_site_part].
Always respond to the entire conversation context, not just the latest message.

Respond in Russian language."""
    
    role = role_template.format(persona=persona['persona'])
    
    handoff_description = f"Пользователь со следующими характеристиками: {persona['persona'][:100]}..."
    
    print(f"Роль агента сформирована, длина: {len(role)} символов")
    
    return Agent(
        name=agent_name,
        role=role,
        handoff_description=handoff_description,
        temperature=0.7
    )

def run_group_discussion(item_type=None, item_name=None):
    """Запускает групповую дискуссию и возвращает результаты
    
    Args:
        item_type (str, optional): Тип объекта отзывов. Если None, будет определен автоматически.
        item_name (str, optional): Название объекта. Если None, будет использовано обобщенное название.
    """
    print("\nЗапуск групповой дискуссии...")
    
    # Создаем runner
    print("Инициализация Runner...")
    runner = Runner()
    
    # Загружаем персоны и создаем агентов
    print("\nЗагрузка персон и создание агентов...")
    personas = load_personas()
    
    # Определяем тип объекта если не задан
    if item_type is None:
        item_type = ItemType.determine_item_type(personas)
    else:
        # Преобразуем тип объекта в константу класса
        if item_type.lower() in ["cosmetics", "makeup"]:
            item_type = ItemType.COSMETICS
            print(f"Используем тип объекта: косметика ({item_type})")
        elif item_type.lower() in ["app", "application", "software"]:
            item_type = ItemType.APP
            print(f"Используем тип объекта: приложение ({item_type})")
        elif item_type.lower() in ["electronics", "gadget", "device"]:
            item_type = ItemType.ELECTRONICS
            print(f"Используем тип объекта: электроника ({item_type})")
        else:
            item_type = ItemType.OTHER
            print(f"Используем тип объекта: другой тип ({item_type})")
    
    # Получаем вопросы для данного типа объекта
    individual_question, group_prompt = ItemType.get_questions(item_type, item_name)
    
    agents = {}
    agent_list = []
    
    for persona in personas:
        agent = create_agent_from_persona(persona, item_type)
        if agent:
            agents[agent.name] = agent
            agent_list.append(agent)
            runner.add_agent(agent)
    print(f"Создано {len(agents)} агентов")
    
    # Проверяем, что есть хотя бы один агент
    if not agents:
        print("Не удалось создать ни одного агента. Завершаем групповую дискуссию.")
        # Создаем пустой файл результатов
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"discussion_{timestamp}.json"
        empty_result = {
            "topic": "Нет данных",
            "error": "Не удалось создать агентов для дискуссии"
        }
        with open(os.path.join('output', output_file), "w", encoding="utf-8") as f:
            json.dump(empty_result, f, ensure_ascii=False, indent=2)
        return output_file
    
    # Настраиваем хэндофы для каждого агента
    print("\nНастройка связей между агентами...")
    for name, agent in agents.items():
        # Добавляем всех других агентов как возможные хэндофы
        handoffs = [a for a in agent_list if a.name != name]
        agent.handoffs = handoffs
        print(f"Для агента {name} настроено {len(handoffs)} хэндофов")
    
    # Запускаем индивидуальный опрос каждой персоны
    responses = {}
    
    print("\nНачинаем опрос агентов...")
    print(f"Вопрос для индивидуального опроса: \"{individual_question}\"")
    
    for i, (name, agent) in enumerate(agents.items(), 1):
        print(f"\nОпрос агента {i}/{len(agents)}: {name}")
        try:
            response = runner.run_conversation(name, individual_question)
            responses[name] = response
            print(f"Получен ответ длиной {len(response)} символов")
        except Exception as e:
            print(f"Ошибка при опросе агента {name}: {str(e)}")
            responses[name] = f"ERROR: {str(e)}"
    
    # Запускаем групповую дискуссию
    print("\nЗапуск групповой дискуссии между персонами...")
    
    # Выбираем первого агента для начала дискуссии
    first_agent_name = list(agents.keys())[0]
    
    print(f"\nГрупповой промпт для типа объекта {item_type}:")
    print(group_prompt)
    
    print(f"Начинаем групповую дискуссию с агента: {first_agent_name}")
    
    # Создаем хранилище для групповой дискуссии
    discussion_history = []
    
    # Максимальное количество передач слова в дискуссии
    max_turns = 6
    
    # Сформируем список участников
    participants = "\n".join([f"- {name}" for name in agents.keys()])
    
    # Инициируем дискуссию
    current_agent_name = first_agent_name
    for turn in range(max_turns):
        print(f"Ход {turn+1}/{max_turns}: агент {current_agent_name}")
        
        # Формируем полный контекст дискуссии 
        messages = []
        
        # Добавляем первый промпт и список участников как системное сообщение
        system_message = f"""{group_prompt}

Список участников дискуссии:
{participants}

Вы - {current_agent_name}. Всегда оставайтесь в своей роли и обращайтесь к другим участникам по их именам.
"""
        messages.append({
            "role": "system",
            "content": system_message
        })
        
        # Добавляем всю историю дискуссии
        if discussion_history:
            for msg in discussion_history:
                agent_label = f"[{msg['agent']}]: "
                
                # Определяем роль сообщения (текущий агент - assistant, остальные - user)
                role = "assistant" if msg['agent'] == current_agent_name else "user"
                
                messages.append({
                    "role": role,
                    "content": agent_label + msg["content"]
                })
        else:
            # Если это первое сообщение, добавляем специальное приглашение к обсуждению
            messages.append({
                "role": "user",
                "content": f"Пожалуйста, начните дискуссию о критериях выбора {item_type}. Поделитесь своим мнением и опытом."
            })
            
        try:
            # Запускаем агента с полным контекстом дискуссии
            result = runner.run_conversation(current_agent_name, messages)
            
            # Сохраняем ответ в истории дискуссии
            discussion_history.append({
                "agent": current_agent_name,
                "is_user": False,
                "content": result
            })
            
            print(f"Получен ответ от {current_agent_name}, длина: {len(result)} символов")
            
            # Определяем, нужно ли передать слово другому агенту
            # Для простоты, просто выбираем следующего агента по списку
            agent_names = list(agents.keys())
            current_index = agent_names.index(current_agent_name)
            next_index = (current_index + 1) % len(agent_names)
            current_agent_name = agent_names[next_index]
            
            print(f"Передаем слово агенту: {current_agent_name}")
            
        except Exception as e:
            print(f"Ошибка в дискуссии при ходе агента {current_agent_name}: {str(e)}")
            break
    
    # Формируем результаты
    print("\nФормирование результатов дискуссии...")
    
    # Определяем тему на основе типа объекта
    topic_text = f"Критерии выбора {item_name or item_type}"
    
    # Создаем структуру для результатов
    discussion_results = {
        "topic": topic_text,
        "item_type": item_type,
        "item_name": item_name,
        "individual_question": individual_question,
        "group_prompt": group_prompt,
        "participants": [name for name in agents.keys()],
        "individual_responses": responses,
        "group_discussion": discussion_history
    }
    
    # Сохраняем результаты в файл с тем же timestamp, что и у файла персон
    timestamp = get_latest_personas_file().split("_")[1].split(".")[0]
    output_file = f"discussion_{timestamp}.json"
    
    print(f"\nСохранение результатов в файл: {output_file}")
    with open(os.path.join('output', output_file), "w", encoding="utf-8") as f:
        json.dump(discussion_results, f, ensure_ascii=False, indent=2)
    
    print("Групповая дискуссия завершена успешно")
    return output_file

async def run_group_discussion_async():
    """Асинхронная версия для совместимости с OpenAI Agents Python SDK"""
    return run_group_discussion()

def save_discussion_results(discussion_data):
    """Сохраняет результаты дискуссии в файл"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"discussion_{timestamp}.json"
    
    with open(os.path.join('output', filename), 'w', encoding='utf-8') as f:
        json.dump(discussion_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nРезультаты дискуссии сохранены в файл: {filename}")
    return filename

if __name__ == "__main__":
    # При запуске файла напрямую, выводим результаты в консоль
    results = run_group_discussion()
    print("\nРезультаты беседы:")
    print(f"Сохранены в файл: {results}") 