import glob
import json
import os
from datetime import datetime
from analyze_sober_reviews import find_duplicate_improvements, generate_improvement_proposal

def get_latest_file(pattern):
    files = glob.glob(os.path.join('output', pattern))
    if not files:
        print(f'Файл не найден по маске: {pattern}')
        return None
    files.sort(key=os.path.getctime, reverse=True)
    return os.path.basename(files[0])

def main():
    # Ищем последний файл с рекомендациями
    final_recommendations_file = get_latest_file('final_recommendations_*.json')
    if not final_recommendations_file:
        raise FileNotFoundError('Не найден файл с финальными рекомендациями!')

    print(f'Найден файл с рекомендациями: {final_recommendations_file}')
    with open(os.path.join('output', final_recommendations_file), 'r', encoding='utf-8') as f:
        recommendations = json.load(f)

    # Собираем все предложения по улучшениям (не баги)
    improvements = []
    
    for priority_level in ['high_priority_recommendations', 'medium_priority_recommendations', 'low_priority_recommendations']:
        if priority_level in recommendations:
            for rec in recommendations[priority_level]:
                # Фильтруем только улучшения, исключаем баги
                if rec.get('category') != 'bug_fixes' and 'bug' not in rec.get('category', ''):
                    # Добавляем приоритет из названия массива, если его нет в самом улучшении
                    if 'priority' not in rec:
                        if 'high' in priority_level:
                            rec['priority'] = 'high'
                        elif 'medium' in priority_level:
                            rec['priority'] = 'medium'
                        else:
                            rec['priority'] = 'low'
                    improvements.append(rec)

    print(f'Найдено {len(improvements)} предложений по улучшениям')
    
    if not improvements:
        print('Предложения по улучшениям не найдены!')
        return
    
    # Анализируем улучшения на дубликаты
    print('Анализ улучшений на дубликаты...')
    unique_improvements = find_duplicate_improvements(improvements)
    print(f'После анализа осталось {len(unique_improvements)} уникальных предложений')
    
    # Создаем детальные планы реализации для каждого улучшения
    print('Создание планов реализации...')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Сохраняем уникальные улучшения в JSON-файл
    unique_improvements_file = os.path.join('output', f'unique_improvements_{timestamp}.json')
    with open(unique_improvements_file, 'w', encoding='utf-8') as f:
        json.dump(unique_improvements, f, ensure_ascii=False, indent=2)
    print(f'Уникальные улучшения сохранены в {unique_improvements_file}')
    
    # Создаем и сохраняем планы реализации для каждого улучшения
    improvement_proposals = []
    for i, imp in enumerate(unique_improvements, 1):
        print(f'Создание плана реализации для улучшения {i} из {len(unique_improvements)}...')
        proposal = generate_improvement_proposal(imp)
        
        # Сохраняем предложение в отдельный файл
        imp_title = imp.get('title', f'improvement_{i}').replace(' ', '_').lower()
        proposal_file = os.path.join('output', f'improvement_proposal_{imp_title}_{timestamp}.md')
        with open(proposal_file, 'w', encoding='utf-8') as f:
            f.write(proposal)
        print(f'Предложение сохранено в {proposal_file}')
        
        # Добавляем в общий список
        improvement_proposals.append({
            'improvement': imp,
            'proposal': proposal,
            'file': proposal_file
        })
    
    # Сохраняем все предложения в один файл для удобства
    all_proposals_file = os.path.join('output', f'all_improvement_proposals_{timestamp}.md')
    with open(all_proposals_file, 'w', encoding='utf-8') as f:
        for i, item in enumerate(improvement_proposals, 1):
            f.write(f'# Предложение по улучшению #{i}\n\n')
            f.write(item['proposal'])
            f.write('\n\n---\n\n')
    
    print(f'Все предложения сохранены в {all_proposals_file}')
    print('Готово!')

if __name__ == "__main__":
    main() 