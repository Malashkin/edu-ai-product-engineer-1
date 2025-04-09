from summarization import read_text, extractive_summarize, abstractive_summarize
from analysis import analyze_summarization_methods
import json
from datetime import datetime

def save_results_to_json(results, filename=None):
    """Save results to a JSON file with timestamp."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"summarization_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    
    print(f"\nResults saved to {filename}")

def main():
    # Read the input text
    text = read_text('oreilly_endofprogramming.txt')
    
    # Generate extractive summary
    print("Generating extractive summary...\n")
    extractive_summary = extractive_summarize(text)
    print("Extractive Summary:")
    print(extractive_summary)
    print("\n")
    
    # Generate abstractive summary
    print("Generating abstractive summary...\n")
    abstractive_summary = abstractive_summarize(text)
    print("Abstractive Summary:")
    print(abstractive_summary)
    print("\n")
    
    # Analyze summarization methods
    print("Analyzing summarization methods...\n")
    analysis = analyze_summarization_methods()
    
    # Prepare results dictionary
    results = {
        "extractive_summary": extractive_summary,
        "abstractive_summary": abstractive_summary,
        "analysis": analysis,
        "timestamp": datetime.now().isoformat(),
        "input_file": "oreilly_endofprogramming.txt"
    }
    
    # Save results to JSON
    save_results_to_json(results)

if __name__ == "__main__":
    main() 