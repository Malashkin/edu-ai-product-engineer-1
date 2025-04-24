import json
import glob
import os
from agents.agent import Agent
from agents.runner import Runner
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def get_latest_personas_file():
    """Находит самый свежий файл с персонами"""
    files = glob.glob("personas_*.json")
    if not files:
        raise FileNotFoundError("Файл с персонами не найден. Сначала запустите main.py")
    return max(files, key=os.path.getctime)

def load_personas():
    """Загружаем персоны из последнего сгенерированного файла"""
    latest_file = get_latest_personas_file()
    print(f"Используем файл с персонами: {latest_file}")
    
    with open(latest_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["personas"]

def create_agent_from_persona(persona):
    """Создает агента на основе данных персоны"""
    # Формируем имя агента из сайта и части
    agent_name = f"Persona_{persona['site']}_{persona['part']}"
    
    # Формируем роль агента
    role = f"""You are a customer persona with the following characteristics:
    {persona['persona']}
    
    When discussing mascara preferences and criteria, always stay in character and base your responses
    on your persona's characteristics, lifestyle, needs, and pain points.
    Respond in Russian language."""
    
    return Agent(
        name=agent_name,
        role=role,
        temperature=0.7
    )

def run_group_discussion():
    """Запускает групповую дискуссию и возвращает результаты"""
    # Создаем runner
    runner = Runner()
    
    # Загружаем персоны и создаем агентов
    personas = load_personas()
    agents = {}
    
    for persona in personas:
        agent = create_agent_from_persona(persona)
        agents[agent.name] = agent
        runner.add_agent(agent)
    
    # Задаем вопрос каждой персоне
    question = "Что для вас важно при выборе туши для ресниц? Расскажите о ваших предпочтениях и критериях выбора."
    responses = {}
    
    for name, agent in agents.items():
        response = runner.run_conversation(name, question)
        responses[name] = response
    
    # Формируем результаты
    discussion_results = {
        "topic": "Критерии выбора туши для ресниц",
        "question": question,
        "responses": responses
    }
    
    # Сохраняем результаты в файл с тем же timestamp, что и у файла персон
    timestamp = get_latest_personas_file().split("_")[1].split(".")[0]
    output_file = f"mascara_discussion_{timestamp}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(discussion_results, f, ensure_ascii=False, indent=2)
    
    print(f"Результаты сохранены в файл: {output_file}")
    return discussion_results

if __name__ == "__main__":
    # При запуске файла напрямую, выводим результаты в консоль
    results = run_group_discussion()
    print("\nРезультаты беседы:")
    print(json.dumps(results, ensure_ascii=False, indent=2)) 