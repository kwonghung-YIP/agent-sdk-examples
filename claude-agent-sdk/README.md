# How to run the examples
1. Generate and fetch the API Key from [Claude Console](https://platform.claude.com/dashboard).
2. Create the .env file, add the **ANTHROPIC_API_KEY=<<your-claude-apikey>>**. (the file is included in .gitignore and will not be committed to git).
3. Run as the command below:
```bash
uv sync
source .venv/bin/activate
uv run --env-file .env src/image-input.py
```


# Reference
- [Claude Code Docs - Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview)
- [Claude Console](https://platform.claude.com/dashboard)