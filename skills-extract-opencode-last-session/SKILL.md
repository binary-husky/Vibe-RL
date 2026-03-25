---
name: extract-opencode-last-session
description: Extract and export the previous OpenCode session conversation to a markdown file
license: MIT
---

# Extract OpenCode Last Session

This skill helps you extract the previous OpenCode session conversation history and export it to a markdown file.

## When to Use

- When you want to review what happened in your previous OpenCode session
- When you need to document or share your previous conversation
- When you want to analyze past interactions

## How It Works

This skill queries the OpenCode SQLite database located at `~/.local/share/opencode/opencode.db` to:
1. Find recent sessions (excluding archived ones)
2. Identify the previous session (second most recent)
3. Extract all messages, parts, and tool calls
4. Format them into a readable markdown file

## Usage

When the user asks to extract or export the last/previous session, follow these steps:

### Step 1: Query Recent Sessions

```python
import sqlite3
from datetime import datetime

db_path = "/home/fuqingxu/.local/share/opencode/opencode.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get the 5 most recent non-archived sessions
cursor.execute("""
    SELECT id, title, time_created, time_updated, directory
    FROM session 
    WHERE time_archived IS NULL
    ORDER BY time_updated DESC 
    LIMIT 5
""")
sessions = cursor.fetchall()

# Display sessions for user reference
for i, session in enumerate(sessions):
    created = datetime.fromtimestamp(session[2]/1000) if session[2] else "N/A"
    updated = datetime.fromtimestamp(session[3]/1000) if session[3] else "N/A"
    print(f"{i+1}. {session[1]}")
    print(f"   Session ID: {session[0]}")
    print(f"   Updated: {updated}")
    print()

conn.close()
```

### Step 2: Extract Session Data

```python
import sqlite3
import json
from datetime import datetime

db_path = "/home/fuqingxu/.local/share/opencode/opencode.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Use the second session (index 1) as the previous session
session_id = "ses_xxx"  # Get from Step 1

# Get session info
cursor.execute("""
    SELECT title, time_created, time_updated, directory
    FROM session 
    WHERE id = ?
""", (session_id,))
session_info = cursor.fetchone()

# Get messages
cursor.execute("""
    SELECT id, time_created, data
    FROM message 
    WHERE session_id = ?
    ORDER BY time_created ASC
""", (session_id,))
messages = cursor.fetchall()
```

### Step 3: Format and Export

```python
# Create Markdown output
output = []
output.append(f"# Session: {session_info[0]}\n")
output.append(f"**Created:** {datetime.fromtimestamp(session_info[1]/1000)}\n")
output.append(f"**Updated:** {datetime.fromtimestamp(session_info[2]/1000)}\n")
output.append(f"**Directory:** {session_info[3]}\n")
output.append(f"**Session ID:** {session_id}\n")
output.append("\n---\n\n")

for msg in messages:
    msg_id = msg[0]
    msg_time = datetime.fromtimestamp(msg[1]/1000)
    msg_data = json.loads(msg[2]) if msg[2] else {}
    
    role = msg_data.get('role', 'unknown')
    output.append(f"## Message ({role}) - {msg_time}\n\n")
    
    # Get all parts for this message
    cursor.execute("""
        SELECT data
        FROM part 
        WHERE message_id = ?
        ORDER BY time_created ASC
    """, (msg_id,))
    parts = cursor.fetchall()
    
    for part in parts:
        part_data = json.loads(part[0]) if part[0] else {}
        
        if part_data.get('type') == 'text':
            text = part_data.get('text', '')
            output.append(f"{text}\n\n")
        elif part_data.get('type') == 'tool_use':
            tool_name = part_data.get('name', 'unknown')
            tool_input = part_data.get('input', {})
            output.append(f"**Tool Use:** `{tool_name}`\n\n")
            output.append(f"```json\n{json.dumps(tool_input, indent=2, ensure_ascii=False)}\n```\n\n")
        elif part_data.get('type') == 'tool_result':
            tool_name = part_data.get('tool_name', 'unknown')
            output.append(f"**Tool Result:** `{tool_name}`\n\n")
            content = part_data.get('content', '')
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        output.append(f"```\n{item.get('text', '')}\n```\n\n")
            else:
                output.append(f"```\n{content}\n```\n\n")
    
    output.append("\n---\n\n")

# Write to file
output_file = './last-session.md'  # or user-specified path
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(''.join(output))

print(f"Successfully exported session to {output_file}")
print(f"Total messages: {len(messages)}")

conn.close()
```

## Complete Script

For convenience, you can use this complete script saved as `extract_session.py`:

```python
#!/usr/bin/env python3
import sqlite3
import json
import sys
from datetime import datetime
from pathlib import Path

def extract_session(session_index=1, output_file='./last-session.md'):
    """
    Extract OpenCode session to markdown file.
    
    Args:
        session_index: 0 for current, 1 for previous, 2 for two sessions ago, etc.
        output_file: Path to output markdown file
    """
    db_path = str(Path.home() / ".local/share/opencode/opencode.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get recent sessions
        cursor.execute("""
            SELECT id, title, time_created, time_updated, directory
            FROM session 
            WHERE time_archived IS NULL
            ORDER BY time_updated DESC 
            LIMIT 10
        """)
        sessions = cursor.fetchall()
        
        if session_index >= len(sessions):
            print(f"Error: Only {len(sessions)} sessions found, cannot access index {session_index}")
            return False
        
        session = sessions[session_index]
        session_id = session[0]
        
        print(f"Extracting session: {session[1]}")
        print(f"Session ID: {session_id}")
        print(f"Updated: {datetime.fromtimestamp(session[3]/1000)}")
        print()
        
        # Get session info
        cursor.execute("""
            SELECT title, time_created, time_updated, directory
            FROM session 
            WHERE id = ?
        """, (session_id,))
        session_info = cursor.fetchone()
        
        # Get messages
        cursor.execute("""
            SELECT id, time_created, data
            FROM message 
            WHERE session_id = ?
            ORDER BY time_created ASC
        """, (session_id,))
        messages = cursor.fetchall()
        
        # Build output
        output = []
        output.append(f"# Session: {session_info[0]}\n")
        output.append(f"**Created:** {datetime.fromtimestamp(session_info[1]/1000)}\n")
        output.append(f"**Updated:** {datetime.fromtimestamp(session_info[2]/1000)}\n")
        output.append(f"**Directory:** {session_info[3]}\n")
        output.append(f"**Session ID:** {session_id}\n")
        output.append("\n---\n\n")
        
        for msg in messages:
            msg_id = msg[0]
            msg_time = datetime.fromtimestamp(msg[1]/1000)
            msg_data = json.loads(msg[2]) if msg[2] else {}
            
            role = msg_data.get('role', 'unknown')
            output.append(f"## Message ({role}) - {msg_time}\n\n")
            
            # Get parts
            cursor.execute("""
                SELECT data
                FROM part 
                WHERE message_id = ?
                ORDER BY time_created ASC
            """, (msg_id,))
            parts = cursor.fetchall()
            
            for part in parts:
                part_data = json.loads(part[0]) if part[0] else {}
                
                if part_data.get('type') == 'text':
                    text = part_data.get('text', '')
                    output.append(f"{text}\n\n")
                elif part_data.get('type') == 'tool_use':
                    tool_name = part_data.get('name', 'unknown')
                    tool_input = part_data.get('input', {})
                    output.append(f"**Tool Use:** `{tool_name}`\n\n")
                    output.append(f"```json\n{json.dumps(tool_input, indent=2, ensure_ascii=False)}\n```\n\n")
                elif part_data.get('type') == 'tool_result':
                    tool_name = part_data.get('tool_name', 'unknown')
                    output.append(f"**Tool Result:** `{tool_name}`\n\n")
                    content = part_data.get('content', '')
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get('type') == 'text':
                                output.append(f"```\n{item.get('text', '')}\n```\n\n")
                    else:
                        output.append(f"```\n{content}\n```\n\n")
            
            output.append("\n---\n\n")
        
        # Write file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(''.join(output))
        
        print(f"✓ Successfully exported to {output_file}")
        print(f"✓ Total messages: {len(messages)}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    session_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    output = sys.argv[2] if len(sys.argv) > 2 else './last-session.md'
    extract_session(session_idx, output)
```

## Examples

**Extract previous session:**
```bash
python extract_session.py 1 ./previous-session.md
```

**Extract current session:**
```bash
python extract_session.py 0 ./current-session.md
```

**Extract session from 2 sessions ago:**
```bash
python extract_session.py 2 ./older-session.md
```

## Database Schema Reference

### Session Table
- `id`: Session identifier
- `title`: Session title
- `time_created`: Creation timestamp (milliseconds)
- `time_updated`: Last update timestamp (milliseconds)
- `time_archived`: Archive timestamp (NULL if not archived)
- `directory`: Working directory

### Message Table
- `id`: Message identifier
- `session_id`: Parent session ID
- `time_created`: Creation timestamp (milliseconds)
- `data`: JSON data containing role and other metadata

### Part Table
- `id`: Part identifier
- `message_id`: Parent message ID
- `session_id`: Parent session ID
- `time_created`: Creation timestamp (milliseconds)
- `data`: JSON data containing type, text, tool calls, etc.

## Notes

- Sessions are identified by IDs like `ses_xxx`
- Timestamps are stored in milliseconds since epoch
- The script skips archived sessions (`time_archived IS NULL`)
- Tool calls and results are preserved in the export
- Output format is GitHub-flavored Markdown
