import os
import shutil
import json
from datetime import datetime

# Process the approved file
filename = 'LINKEDIN_POST_post_20260115_112109.md'
approved_path = os.path.join('Approved', filename)

if os.path.exists(approved_path):
    print(f'✅ Processing: {filename}')
    
    # Read content
    with open(approved_path, 'r') as f:
        content = f.read()
    
    # Create log
    log_data = {
        'action': 'linkedin_post_published',
        'post_id': 'post_20260115_112109',
        'filename': filename,
        'processed_at': datetime.now().isoformat(),
        'status': 'simulated_published',
        'content_preview': content[:200]
    }
    
    # Save log
    os.makedirs('Logs', exist_ok=True)
    log_file = f'Logs/post_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2)
    
    print(f'📝 Log created: {log_file}')
    
    # Move to Done
    os.makedirs('Done', exist_ok=True)
    shutil.move(approved_path, os.path.join('Done', filename))
    print(f'📁 Moved to Done folder')
    
    # Update Dashboard
    if os.path.exists('Dashboard.md'):
        with open('Dashboard.md', 'a') as f:
            f.write(f'\n- [{datetime.now().strftime("%Y-%m-%d %H:%M")}] LinkedIn post processed: post_20260115_112109')
        print('📊 Dashboard updated')
    
    print('🎉 Post processed successfully!')
else:
    print('❌ File not found in Approved folder')