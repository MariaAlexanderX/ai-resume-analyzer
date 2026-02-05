import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

st.title("Resume Matcher - AI Job Fit Analyzer")

job_desc = st.text_area("Paste Job Description", height=200)
resume_text = st.text_area("Paste Resume Text", height=300)

if st.button("Analyze Fit"):
    if not job_desc or not resume_text:
        st.error("Both fields required.")
    else:
        with st.spinner("Analyzing..."):
            prompt = f"""
You are a precise HR automation assistant.
Analyze the job description and the resume below.
Follow this exact reasoning process:
1. List hard technical skills required by the job (only explicit ones).
2. List skills and relevant experience explicitly mentioned in the resume.
3. Compare them. Give credit for closely related transferable skills.
4. Calculate match_score: 100 = perfect match, deduct heavily for missing core hard skills.
Do not invent skills.

Example 1:
Job Description: Requires Java, Spring Boot, 4+ years backend experience, AWS.
Resume: Knows Java, Python. 3 years full-stack developer.
Output:
{{
  "match_score": 65,
  "matching_skills": ["Java"],
  "missing_skills": ["Spring Boot", "AWS", "4+ years backend experience"],
  "decision": "possible",
  "one_sentence_reason": "Solid on Java but lacks key backend framework and cloud experience.",
  "suggested_tailoring_advice": "Add any Spring or AWS exposure to resume."
}}
Example 2:
Job Description: Needs Python, pandas, data visualization, 2+ years data analysis.
Resume: Python, SQL, Tableau. 1.5 years as data analyst.
Output:
{{
  "match_score": 80,
  "matching_skills": ["Python", "data visualization"],
  "missing_skills": ["pandas"],
  "decision": "strong",
  "one_sentence_reason": "Strong overlap in Python and visualization tools, minor gap in pandas.",
  "suggested_tailoring_advice": null
}}
Example 3:
Job Description: Requires Python, REST APIs, Docker, 3+ years backend development.
Resume: Python, JavaScript, 2 years frontend developer with API integrations.
Output:
{{
  "match_score": 60,
  "matching_skills": ["Python"],
  "missing_skills": ["REST APIs", "Docker", "3+ years backend development"],
  "decision": "possible",
  "one_sentence_reason": "Python match + API experience is transferable, but lacks backend depth and Docker.",
  "suggested_tailoring_advice": "Emphasize API work and consider adding Docker projects."
}}
Example 4:
Job Description: Member of Technical Staff - AI Engineer. Requires Python, PyTorch/JAX, understanding of transformers/LLMs, ML projects/portfolio.
Resume: Python cert, Machine Learning Specialization, Neural Networks skill, no projects listed.
Output:
{{
  "match_score": 45,
  "matching_skills": ["Python", "Neural Networks", "ML concepts from specialization"],
  "missing_skills": ["PyTorch/JAX", "transformers/LLMs hands-on", "demonstrated ML projects/portfolio"],
  "decision": "possible",
  "one_sentence_reason": "Strong theoretical base from certs, but no practical ML implementation or projects shown.",
  "suggested_tailoring_advice": "Build and document 1–2 small ML projects (e.g. fine-tune a model with Hugging Face/PyTorch) and add GitHub link."
}}

Now analyze this case:
Job Description:
{job_desc}
Resume:
{resume_text}

Return **only** valid JSON. No extra text, no explanations, no markdown, no code blocks, no trailing characters. The JSON must be complete and parsable. Exact structure only.
"""

            try:
                response = client.chat.completions.create(
                    model=os.getenv("GROK_MODEL", "grok-3"),
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    temperature=0.0,
                    max_tokens=800
                )

                content = response.choices[0].message.content.strip()

                # Robust stripping
                if content.startswith("```json"):
                    content = content.split("```json", 1)[1].split("```", 1)[0].strip()
                elif content.startswith("```"):
                    content = content.split("```", 2)[1].strip()

                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end != 0:
                    content = content[start:end]

                output = json.loads(content)

                st.success("Analysis complete")

                # Colored score via markdown
                score = output['match_score']
                if score > 70:
                    color = "green"
                elif score >= 40:
                    color = "orange"
                else:
                    color = "red"

                st.markdown(f"<h3 style='color:{color};'>Match Score: {score}/100</h3>", unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Matching Skills**")
                    st.write(output["matching_skills"])
                with col2:
                    st.markdown("**Missing Skills**")
                    st.write(output["missing_skills"])

                st.markdown("**Decision**")
                st.write(output["decision"].upper())

                st.markdown("**Reason**")
                st.write(output["one_sentence_reason"])

                st.markdown("**Advice**")
                st.write(output.get("suggested_tailoring_advice", "N/A"))

            except json.JSONDecodeError as e:
                st.error(f"JSON parse failed: {e}")
                st.code(response.choices[0].message.content, language="json")
            except Exception as e:
                st.error(f"Error: {e}")