# Extract OpenCode Last Session

A skill for extracting and exporting OpenCode session conversation history to markdown files.

## Overview

This skill provides tools to extract conversation history from OpenCode's SQLite database and export it to a well-formatted markdown file. Useful for:

- Reviewing previous conversations
- Documenting workflows
- Sharing session transcripts
- Analyzing past interactions

## Installation

This skill is already installed if you're in this directory. To use it:

```bash
# Make the script executable
chmod +x extract_session.py

# Run the script
./extract_session.py
```

## Usage

### Basic Usage

Extract the previous session (most common use case):

```bash
python extract_session.py
```

This will create `./last-session.md` with the previous session's conversation.

### Advanced Usage

Extract specific sessions:

```bash
# Extract current session
python extract_session.py 0 ./current-session.md

# Extract previous session (default)
python extract_session.py 1 ./previous-session.md

# Extract session from 2 sessions ago
python extract_session.py 2 ./older-session.md

# Extract to a specific file
python extract_session.py 1 ~/Documents/my-session.md
```

### In OpenCode

Simply ask OpenCode:

- "Extract the last session"
- "Export my previous conversation"
- "Save the last session to a file"

OpenCode will use this skill to extract the session for you.

## Output Format

The exported markdown file includes:

- **Session metadata**: Title, creation/update timestamps, directory, session ID
- **Complete message history**: All user and assistant messages
- **Tool calls**: All tool invocations with their parameters
- **Tool results**: Output from each tool
- **Timestamps**: When each message was created

Example output structure:

```markdown
# Session: My Session Title

**Created:** 2026-03-25 08:13:26
**Updated:** 2026-03-25 08:47:06
**Directory:** /home/user/project
**Session ID:** ses_xxx

---

## Message (user) - 2026-03-25 08:13:26

User's message content...

---

## Message (assistant) - 2026-03-25 08:13:30

Assistant's response...

**Tool Use:** `bash`

```json
{
  "command": "ls -la",
  "description": "List files"
}
```

**Tool Result:** `bash`

```
total 48
drwxrwxr-x 5 user user 4096 Mar 25 08:13 .
...
```

---
```

## How It Works

1. **Database Location**: Reads from `~/.local/share/opencode/opencode.db`
2. **Session Selection**: Queries non-archived sessions ordered by update time
3. **Data Extraction**: Retrieves messages and their parts (text, tool calls, results)
4. **Formatting**: Converts to GitHub-flavored Markdown
5. **Export**: Writes to specified file path

## Database Schema

The skill understands OpenCode's database structure:

- **session**: Session metadata (title, timestamps, directory)
- **message**: Individual messages (user/assistant)
- **part**: Message components (text, tool_use, tool_result)

## Requirements

- Python 3.6+
- OpenCode installed with sessions in `~/.local/share/opencode/`
- No external dependencies (uses built-in `sqlite3` module)

## Troubleshooting

**"Database not found" error:**
- Ensure OpenCode is installed and has been used at least once
- Check that `~/.local/share/opencode/opencode.db` exists

**"No sessions found" error:**
- Verify you have active sessions (not all archived)
- Try accessing a different session index

**"Only N sessions found" error:**
- The requested session index is too high
- Use a lower index (0 for current, 1 for previous, etc.)

## Files

- `SKILL.md`: Detailed skill documentation and instructions
- `extract_session.py`: Main extraction script
- `README.md`: This file

## License

MIT License - Feel free to use and modify as needed.
