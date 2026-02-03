# from openai import OpenAI
# import streamlit as st
# from planner.prompt import build_prompt

# client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# def generate_plan(exam, days, hours, retries=2):
#     prompt = build_prompt(exam, days, hours)

#     for attempt in range(retries + 1):
#         response = client.chat.completions.create(
#             model="gpt-4.1",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.3
#         )

#         content = response.choices[0].message.content

#         # Quick sanity check
#         if "days" in content and "date" in content:
#             return content

#     raise RuntimeError("Failed to generate a valid study plan after retries")

from openai import OpenAI
import streamlit as st
from planner.prompt import build_prompt
import os

#client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_plan(exam, days, hours):
    """
    Calls OpenAI once and returns raw model output.
    Validation is handled separately.
    """
    prompt = build_prompt(exam, days, hours)

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content
