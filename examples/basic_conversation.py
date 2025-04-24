from agents.agent import Agent
from agents.runner import Runner

def main():
    # Создаем агента
    assistant = Agent(
        name="assistant",
        role="You are a helpful AI assistant that provides clear and concise answers",
        temperature=0.7
    )

    # Создаем runner и добавляем агента
    runner = Runner()
    runner.add_agent(assistant)

    # Пример беседы
    prompt = "What is the capital of France?"
    response = runner.run_conversation("assistant", prompt)
    print(f"Assistant's response: {response}")

    # Очищаем историю
    runner.clear_all_histories()

if __name__ == "__main__":
    main() 