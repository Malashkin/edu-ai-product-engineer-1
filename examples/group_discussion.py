import json
import glob
import os
import asyncio
from agents.agent import Agent
from agents.runner import Runner
from dotenv import load_dotenv
from openai import OpenAI

# Загружаем переменные окружения
load_dotenv()

class ProductType:
    """Определение типа продукта и генерация соответствующих вопросов"""
    MASCARA = "mascara"
    APP = "app"
    OTHER = "other"
    
    @staticmethod
    def determine_product_type(personas):
        """Определяет тип продукта на основе персон"""
        # Инициализация клиента OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Формируем текст для анализа
        persona_samples = []
        for i, persona in enumerate(personas[:2]):  # Берем первые две персоны для анализа
            persona_samples.append(persona.get('persona', ''))
        
        combined_text = "\n\n".join(persona_samples)
        
        # Формируем промпт для определения типа продукта
        prompt = f"""Определи, о каком типе продукта идет речь в следующих описаниях персон:

{combined_text}

Выбери один из вариантов:
1. Тушь для ресниц или другая косметика
2. Мобильное приложение или программное обеспечение
3. Другой тип продукта

Ответь только номером варианта."""
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты - аналитик, который определяет тип продукта по описаниям персон потребителей."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=10
            )
            
            answer = response.choices[0].message.content.strip()
            
            if "1" in answer:
                print("Определен тип продукта: тушь для ресниц/косметика")
                return ProductType.MASCARA
            elif "2" in answer:
                print("Определен тип продукта: мобильное приложение/ПО")
                return ProductType.APP
            else:
                print("Определен тип продукта: другой тип")
                return ProductType.OTHER
                
        except Exception as e:
            print(f"Ошибка при определении типа продукта: {str(e)}")
            # По умолчанию возвращаем тип Other
            return ProductType.OTHER
    
    @staticmethod
    def get_questions(product_type):
        """Возвращает вопросы для индивидуального опроса и для групповой дискуссии"""
        if product_type == ProductType.MASCARA:
            individual_question = "Что для вас важно при выборе туши для ресниц? Расскажите о ваших предпочтениях и критериях выбора."
            group_prompt = """Вы участвуете в групповой дискуссии о выборе туши для ресниц. 
            Вопрос для обсуждения: "Какие критерии выбора туши для ресниц наиболее важны и почему?"
            
            Поделитесь своим мнением и опытом, а затем задайте вопрос или прокомментируйте ответ другого участника.
            Оставайтесь в характере вашей персоны, опирайтесь на свои потребности и болевые точки.
            
            При обращении к другим участникам, используйте их имена в квадратных скобках, например [Имя_участника].
            
            Если вы считаете, что другой участник лучше ответит на конкретный вопрос - передайте ему слово."""
            
        elif product_type == ProductType.APP:
            individual_question = "Что для вас важно при выборе и использовании мобильных приложений? Расскажите о ваших предпочтениях и критериях оценки."
            group_prompt = """Вы участвуете в групповой дискуссии о мобильных приложениях. 
            Вопрос для обсуждения: "Какие функции и характеристики мобильных приложений наиболее важны для пользователей и почему?"
            
            Поделитесь своим мнением и опытом, а затем задайте вопрос или прокомментируйте ответ другого участника.
            Оставайтесь в характере вашей персоны, опирайтесь на свои потребности и болевые точки.
            
            При обращении к другим участникам, используйте их имена в квадратных скобках, например [Имя_участника].
            
            Если вы считаете, что другой участник лучше ответит на конкретный вопрос - передайте ему слово."""
            
        else:
            individual_question = "Что для вас важно при выборе этого продукта? Расскажите о ваших предпочтениях и критериях выбора."
            group_prompt = """Вы участвуете в групповой дискуссии о выборе продукта. 
            Вопрос для обсуждения: "Какие критерии выбора этого продукта наиболее важны и почему?"
            
            Поделитесь своим мнением и опытом, а затем задайте вопрос или прокомментируйте ответ другого участника.
            Оставайтесь в характере вашей персоны, опирайтесь на свои потребности и болевые точки.
            
            При обращении к другим участникам, используйте их имена в квадратных скобках, например [Имя_участника].
            
            Если вы считаете, что другой участник лучше ответит на конкретный вопрос - передайте ему слово."""
        
        return individual_question, group_prompt

def get_latest_personas_file():
    """Находит самый свежий файл с персонами"""
    print("\nПоиск файла с персонами...")
    files = glob.glob("personas_*.json")
    if not files:
        raise FileNotFoundError("Файл с персонами не найден. Сначала запустите main.py")
    latest = max(files, key=os.path.getctime)
    print(f"Найден файл: {latest}")
    return latest

def load_personas():
    """Загружаем персоны из последнего сгенерированного файла"""
    latest_file = get_latest_personas_file()
    print(f"\nЗагрузка персон из файла: {latest_file}")
    
    with open(latest_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Загружено {len(data['personas'])} персон")
    return data["personas"]

def create_agent_from_persona(persona, product_type):
    """Создает агента на основе данных персоны"""
    # Формируем имя агента из сайта и части
    agent_name = f"Persona_{persona['site']}_{persona['part']}"
    print(f"\nСоздание агента: {agent_name}")
    
    # Формируем роль агента и описание для хэндофа
    if product_type == ProductType.MASCARA:
        role_template = """You are a customer persona with the following characteristics:
{persona}

When discussing mascara preferences and criteria, always stay in character and base your responses
on your persona's characteristics, lifestyle, needs, and pain points.

In the group discussion, you can refer to other participants by using their full names in brackets like [Persona_site_part].
Always respond to the entire conversation context, not just the latest message.

Respond in Russian language."""
    elif product_type == ProductType.APP:
        role_template = """You are a customer persona with the following characteristics:
{persona}

When discussing mobile app preferences and criteria, always stay in character and base your responses
on your persona's characteristics, lifestyle, needs, and pain points.

In the group discussion, you can refer to other participants by using their full names in brackets like [Persona_site_part].
Always respond to the entire conversation context, not just the latest message.

Respond in Russian language."""
    else:
        role_template = """You are a customer persona with the following characteristics:
{persona}

When discussing product preferences and criteria, always stay in character and base your responses
on your persona's characteristics, lifestyle, needs, and pain points.

In the group discussion, you can refer to other participants by using their full names in brackets like [Persona_site_part].
Always respond to the entire conversation context, not just the latest message.

Respond in Russian language."""
    
    role = role_template.format(persona=persona['persona'])
    
    handoff_description = f"Покупатель со следующими характеристиками: {persona['persona'][:100]}..."
    
    print(f"Роль агента сформирована, длина: {len(role)} символов")
    
    return Agent(
        name=agent_name,
        role=role,
        handoff_description=handoff_description,
        temperature=0.7
    )

def run_group_discussion():
    """Запускает групповую дискуссию и возвращает результаты"""
    print("\nЗапуск групповой дискуссии...")
    
    # Создаем runner
    print("Инициализация Runner...")
    runner = Runner()
    
    # Загружаем персоны и создаем агентов
    print("\nЗагрузка персон и создание агентов...")
    personas = load_personas()
    
    # Определяем тип продукта
    product_type = ProductType.determine_product_type(personas)
    
    # Получаем вопросы для данного типа продукта
    individual_question, group_prompt = ProductType.get_questions(product_type)
    
    agents = {}
    agent_list = []
    
    for persona in personas:
        agent = create_agent_from_persona(persona, product_type)
        agents[agent.name] = agent
        agent_list.append(agent)
        runner.add_agent(agent)
    print(f"Создано {len(agents)} агентов")
    
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
    
    print(f"\nГрупповой промпт для типа продукта {product_type}:")
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
                "content": f"Пожалуйста, начните дискуссию о критериях выбора {product_type}. Поделитесь своим мнением и опытом."
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
    
    # Определяем тему на основе типа продукта
    if product_type == ProductType.MASCARA:
        topic = "Критерии выбора туши для ресниц"
    elif product_type == ProductType.APP:
        topic = "Критерии выбора и оценки мобильных приложений"
    else:
        topic = "Критерии выбора продукта"
    
    # Создаем структуру для результатов
    discussion_results = {
        "topic": topic,
        "product_type": product_type,
        "individual_question": individual_question,
        "group_prompt": group_prompt,
        "participants": [name for name in agents.keys()],
        "individual_responses": responses,
        "group_discussion": discussion_history
    }
    
    # Сохраняем результаты в файл с тем же timestamp, что и у файла персон
    timestamp = get_latest_personas_file().split("_")[1].split(".")[0]
    output_file = f"mascara_discussion_{timestamp}.json"
    
    print(f"\nСохранение результатов в файл: {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(discussion_results, f, ensure_ascii=False, indent=2)
    
    print("Групповая дискуссия завершена успешно")
    return output_file

async def run_group_discussion_async():
    """Асинхронная версия для совместимости с OpenAI Agents Python SDK"""
    return run_group_discussion()

if __name__ == "__main__":
    # При запуске файла напрямую, выводим результаты в консоль
    results = run_group_discussion()
    print("\nРезультаты беседы:")
    print(f"Сохранены в файл: {results}") 