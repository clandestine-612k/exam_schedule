# def build_prompt(exam, days, hours):
#     return f"""
# You are an expert academic planner for Indian competitive examinations.

# Exam: {exam}
# Total days remaining: {days}
# Maximum study hours per day: {hours}

# STRICT RULES:
# 1. Generate EXACTLY one entry per calendar day.
# 2. Dates must be continuous, starting from tomorrow.
# 3. Do not skip days.
# 4. Do not exceed the daily hour limit.
# 5. Use commonly accepted syllabus structure for the exam.
# 6. Do NOT add explanations or markdown.

# Return ONLY valid JSON in the following format:

# {{
#   "days": [
#     {{
#       "date": "YYYY-MM-DD",
#       "tasks": [
#         {{
#           "subject": "string",
#           "topic": "string",
#           "hours": number
#         }}
#       ]
#     }}
#   ]
# }}
# """
def build_prompt(exam, days, hours):
    return f"""
You are an expert academic planner for Indian competitive exams.

Exam: {exam}
Total study days: {days}
Study hours per day: {hours}

IMPORTANT:
- DO NOT use real calendar dates
- Use day numbers only (Day 1, Day 2, ...)
- Allocate subjects/topics per day
- Do not skip days.
- Respect daily hour limits
- Include revision and tests
- Use commonly accepted syllabus structure for the exam.
- Do NOT add explanations or markdown.

Return ONLY valid JSON in this format:

{{
  "days": [
    {{
      "day": 1,
      "tasks": [
        {{
          "subject": "string",
          "topic": "string",
          "hours": number
        }}
      ]
    }}
  ]
}}
"""
