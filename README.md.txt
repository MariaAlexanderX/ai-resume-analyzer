# Resume Matcher

Interactive tool that analyzes resume fit against job descriptions using Grok API.

## Features
- Prompt engineering with few-shot examples
- Structured JSON output
- Streamlit web interface

## Screenshots

### Interface
![Interface](screenshots/interface.png)

### Example result (xAI role)
![xAI result](screenshots/xai_result.png)

### Example result (other role)
![Other result](screenshots/other_result.png)

## How to run locally
1. `pip install -r requirements.txt` (create file with `streamlit`, `openai`, `python-dotenv`)
2. Add `.env` with `XAI_API_KEY=...`
3. `streamlit run app.py`

## Evaluation
Tested on 4 cases → average score difference 8.8 points vs manual judgment.

## Deployed version
[Live demo link] (add after step 3)