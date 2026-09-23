# How to run the examples
1. Generate and get the API Key from [OpenAI Platform](https://platform.openai.com/home).
2. Create the .env file, add the **OPENAI_API_KEY=<<your-openai-apikey>>**. (the file is included in .gitignore and will not be committed to git).
3. Run as the command below:
```bash
uv sync
source .venv/bin/activate
uv run --env-file .env src/image-input.py
```


# Reference
- [OpenAI Agents SDK - GitHub](https://openai.github.io/openai-agents-python/)
- [Agents SDK - OpenAI Developers Doc](https://developers.openai.com/api/docs/guides/agents)
- [OpenAI Platform](https://platform.openai.com/home)