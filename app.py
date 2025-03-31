import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from string import punctuation
import openai
from dotenv import load_dotenv
import os

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def read_text(file_path):
    """Read text from file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extractive_summarize(text, num_sentences=5):
    """Extractive summarization using NLTK."""
    # Tokenize the text into sentences
    sentences = sent_tokenize(text)
    
    # Tokenize the text into words
    words = word_tokenize(text.lower())
    
    # Remove stopwords and punctuation
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words and word not in punctuation]
    
    # Calculate word frequencies
    freq_dist = FreqDist(words)
    
    # Calculate sentence scores based on word frequencies
    sentence_scores = {}
    for sentence in sentences:
        for word in word_tokenize(sentence.lower()):
            if word in freq_dist:
                if sentence not in sentence_scores:
                    sentence_scores[sentence] = freq_dist[word]
                else:
                    sentence_scores[sentence] += freq_dist[word]
    
    # Get the top sentences
    summary_sentences = sorted(sentence_scores.items(), 
                             key=lambda x: x[1], 
                             reverse=True)[:num_sentences]
    
    # Sort sentences by their original order
    summary_sentences = sorted(summary_sentences, 
                             key=lambda x: sentences.index(x[0]))
    
    # Join sentences into summary
    summary = ' '.join([sentence for sentence, score in summary_sentences])
    return summary

def abstractive_summarize(text):
    """Abstractive summarization using OpenAI API."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini-search-preview-2025-03-11",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates concise summaries of articles."},
                {"role": "user", "content": f"Please provide a concise summary of the following article:\n\n{text}"}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Error in abstractive summarization: {str(e)}"

def main():
    # Read the article
    text = read_text('oreilly_endofprogramming.txt')
    
    # Generate summaries
    print("\n=== Extractive Summary (NLTK) ===")
    extractive_summary = extractive_summarize(text)
    print(extractive_summary)
    
    print("\n=== Abstractive Summary (OpenAI) ===")
    abstractive_summary = abstractive_summarize(text)
    print(abstractive_summary)

if __name__ == "__main__":
    main() 