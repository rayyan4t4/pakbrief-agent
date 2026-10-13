# PakBrief Agent

A tool-using research agent that answers current Pakistan questions with cited live web sources.

## How it works
1. User asks a current-affairs question
2. Agent calls DuckDuckGo search (no API key needed)
3. Reads top results, synthesizes answer with inline citations via OpenRouter LLM
4. Shows the tool trace so the agentic loop is visible

## Run locally
```
pip install -r requirements.txt
export OPENROUTER_API_KEY=your_key
streamlit run app.py
```

## Eval
~25 hand-written gold questions scored on accuracy + citation rate vs a no-tool baseline.
