#!/usr/bin/env python3
"""
Extract OpenCode session conversation history to markdown file.

Usage:
    python extract_session.py [session_index] [output_file]
    
    session_index: 0 for current, 1 for previous (default), 2 for two sessions ago, etc.
    output_file: Path to output markdown file (default: ./last-session.md)

Examples:
    python extract_session.py                    # Extract previous session
    python extract_session.py 1 ./prev.md        # Extract previous session to prev.md
    python extract_session.py 0 ./current.md     # Extract current session
"""

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
    
    Returns:
        bool: True if successful, False otherwise
    """
    db_path = str(Path.home() / ".local/share/opencode/opencode.db")
    
    if not Path(db_path).exists():
        print(f"Error: OpenCode database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get recent non-archived sessions
        cursor.execute("""
            SELECT id, title, time_created, time_updated, directory
            FROM session 
            WHERE time_archived IS NULL
            ORDER BY time_updated DESC 
            LIMIT 10
        """)
        sessions = cursor.fetchall()
        
        if not sessions:
            print("Error: No sessions found")
            return False
        
        if session_index >= len(sessions):
            print(f"Error: Only {len(sessions)} sessions found, cannot access index {session_index}")
            print("\nAvailable sessions:")
            for i, s in enumerate(sessions):
                updated = datetime.fromtimestamp(s[3]/1000)
                print(f"  {i}: {s[1]} (updated: {updated})")
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
        
        if not messages:
            print("Warning: No messages found in this session")
        
        # Build markdown output
        output = []
        output.append(f"# Session: {session_info[0]}\n\n")
        output.append(f"**Created:** {datetime.fromtimestamp(session_info[1]/1000)}\n\n")
        output.append(f"**Updated:** {datetime.fromtimestamp(session_info[2]/1000)}\n\n")
        output.append(f"**Directory:** {session_info[3]}\n\n")
        output.append(f"**Session ID:** {session_id}\n\n")
        output.append("---\n\n")
        
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
                part_type = part_data.get('type', 'unknown')
                
                if part_type == 'text':
                    text = part_data.get('text', '')
                    output.append(f"{text}\n\n")
                    
                elif part_type == 'tool_use':
                    tool_name = part_data.get('name', 'unknown')
                    tool_input = part_data.get('input', {})
                    output.append(f"**Tool Use:** `{tool_name}`\n\n")
                    output.append(f"```json\n{json.dumps(tool_input, indent=2, ensure_ascii=False)}\n```\n\n")
                    
                elif part_type == 'tool_result':
                    tool_name = part_data.get('tool_name', 'unknown')
                    output.append(f"**Tool Result:** `{tool_name}`\n\n")
                    content = part_data.get('content', '')
                    
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict):
                                if item.get('type') == 'text':
                                    text = item.get('text', '')
                                    if text:
                                        output.append(f"```\n{text}\n```\n\n")
                    elif content:
                        output.append(f"```\n{content}\n```\n\n")
            
            output.append("---\n\n")
        
        # Write to file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(''.join(output))
        
        print(f"✓ Successfully exported to {output_file}")
        print(f"✓ Total messages: {len(messages)}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Command-line interface."""
    session_idx = 1  # Default to previous session
    output = './last-session.md'
    
    if len(sys.argv) > 1:
        try:
            session_idx = int(sys.argv[1])
        except ValueError:
            print(f"Error: Invalid session index '{sys.argv[1]}', must be an integer")
            print(__doc__)
            sys.exit(1)
    
    if len(sys.argv) > 2:
        output = sys.argv[2]
    
    success = extract_session(session_idx, output)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
