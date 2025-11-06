#!/usr/bin/env python3
"""
Update data/index.json with list of available news files
This runs after saving new synthesis to keep the index up to date
"""
import json
import os
from pathlib import Path
from datetime import datetime

def update_index():
    """Update the index.json file with available dates and story counts"""
    data_dir = Path('../data')
    index_file = data_dir / 'index.json'
    
    # Find all JSON files (excluding index.json itself)
    available_dates = []
    dates_with_counts = {}
    
    if data_dir.exists():
        for file in data_dir.glob('*.json'):
            if file.name == 'index.json':
                continue
            
            # Extract date from filename (YYYY-MM-DD.json)
            date_str = file.stem
            try:
                # Validate it's a date
                datetime.strptime(date_str, '%Y-%m-%d')
                available_dates.append(date_str)
                
                # Load file to get story count (for faster archive loading)
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        story_count = len(data.get('stories', []))
                        dates_with_counts[date_str] = story_count
                except Exception as e:
                    dates_with_counts[date_str] = 0
            except ValueError:
                continue
    
    # Sort dates (newest first)
    available_dates.sort(reverse=True)
    
    # Create index with story counts
    index = {
        'available_dates': available_dates,
        'story_counts': dates_with_counts,
        'last_updated': datetime.now().isoformat(),
        'total_files': len(available_dates)
    }
    
    # Save index
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"Updated index.json with {len(available_dates)} dates and story counts")
    return index_file

if __name__ == '__main__':
    update_index()

