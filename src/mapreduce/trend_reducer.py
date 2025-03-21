#!/usr/bin/env python3
import sys
import json
from collections import defaultdict

def process_values(values):
    """Process and aggregate values for a key"""
    total_count = 0
    total_score = 0
    total_comments = 0
    
    for value in values:
        total_count += value['count']
        total_score += value['score']
        total_comments += value['num_comments']
    
    return {
        'count': total_count,
        'avg_score': total_score / len(values),
        'avg_comments': total_comments / len(values),
        'engagement_score': (total_score + total_comments) / len(values)
    }

def main():
    """Main function to process mapper output"""
    current_key = None
    values = []
    
    for line in sys.stdin:
        try:
            # Parse input line
            key, value = line.strip().rsplit('\t', 1)
            value = json.loads(value)
            
            # If we have a new key, process the previous group
            if current_key and current_key != key:
                result = process_values(values)
                # Output: date, bigram, metrics
                print(f"{current_key}\t{json.dumps(result)}")
                values = []
            
            current_key = key
            values.append(value)
            
        except Exception as e:
            sys.stderr.write(f"Error processing line: {str(e)}\n")
    
    # Process the last group
    if current_key:
        result = process_values(values)
        print(f"{current_key}\t{json.dumps(result)}")

if __name__ == '__main__':
    main() 