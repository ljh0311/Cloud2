#!/usr/bin/env python3
import sys
import json
from datetime import datetime
import re
from collections import Counter

def extract_ngrams(text, n=2):
    """Extract n-grams from text"""
    words = re.findall(r'\b\w+\b', text.lower())
    return [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]

def process_post(post):
    """Process a Reddit post and emit trends"""
    try:
        # Extract timestamp and convert to date
        timestamp = datetime.fromtimestamp(post['created_utc']).strftime('%Y-%m-%d')
        
        # Combine title and text
        content = f"{post['title']} {post['text']}"
        
        # Extract bigrams
        bigrams = extract_ngrams(content)
        bigram_counter = Counter(bigrams)
        
        # Emit trends
        for bigram, count in bigram_counter.items():
            # Key: date, bigram
            # Value: count, score, num_comments
            key = f"{timestamp}\t{bigram}"
            value = {
                'count': count,
                'score': post['score'],
                'num_comments': post['num_comments']
            }
            print(f"{key}\t{json.dumps(value)}")
            
    except Exception as e:
        sys.stderr.write(f"Error processing post: {str(e)}\n")

def main():
    """Main function to process input lines"""
    for line in sys.stdin:
        try:
            post = json.loads(line.strip())
            process_post(post)
        except Exception as e:
            sys.stderr.write(f"Error parsing line: {str(e)}\n")

if __name__ == '__main__':
    main() 