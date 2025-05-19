import glob
import json
import os
from analyze_sober_reviews import generate_bug_report_via_openai

def get_latest_file(pattern):
    files = glob.glob(os.path.join('output', pattern))
    if not files:
        print(f'Файл не найден по маске: {pattern}')
        return None
    files.sort(key=os.path.getctime, reverse=True)
    return os.path.basename(files[0])

final_recommendations_file = get_latest_file('final_recommendations_*.json')
if not final_recommendations_file:
    raise FileNotFoundError('Не найден файл с финальными рекомендациями!')

with open(os.path.join('output', final_recommendations_file), 'r', encoding='utf-8') as f:
    recommendations = json.load(f)

# Ищем баги только в high/medium/low_priority_recommendations по category == 'bug_fixes'
bug_candidates = []
for priority_key in ['high_priority_recommendations', 'medium_priority_recommendations', 'low_priority_recommendations']:
    for item in recommendations.get(priority_key, []):
        if item.get('category') == 'bug_fixes':
            bug_text = f"{item.get('title', '')}\n{item.get('description', '')}"
            bug_candidates.append(bug_text)

if not bug_candidates:
    print('Не найдено багов в финальных рекомендациях!')
    exit(0)

from datetime import datetime
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

for i, bug_text in enumerate(bug_candidates, 1):
    generate_bug_report_via_openai(bug_text, bug_index=i, timestamp=timestamp) 