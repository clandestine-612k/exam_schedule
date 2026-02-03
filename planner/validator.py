# import json
# import re
# from datetime import datetime

# def validate_plan(raw_json, days_left, hours_per_day):
#     try:
#         # Remove markdown if present
#         raw_json = re.sub(r"```json|```", "", raw_json).strip()

#         data = json.loads(raw_json)

#         if "days" not in data or not data["days"]:
#             raise ValueError("Missing or empty 'days' field")

#         dates = []

#         for day in data["days"]:
#             if "date" not in day or "tasks" not in day:
#                 raise ValueError("Each day must have date and tasks")

#             total_hours = 0

#             for task in day["tasks"]:
#                 if not all(k in task for k in ("subject", "topic", "hours")):
#                     raise ValueError("Task missing required fields")

#                 total_hours += float(task["hours"])

#             # Allow small floating tolerance
#             if total_hours > hours_per_day + 0.5:
#                 raise ValueError(f"Daily hours exceeded on {day['date']}")

#             dates.append(datetime.fromisoformat(day["date"]))

#         # Ensure plan does not exceed allowed span
#         span = (max(dates) - min(dates)).days + 1
#         if span > days_left + 2:
#             raise ValueError("Plan duration exceeds allowed days")

#         return data

#     except Exception as e:
#         raise ValueError(f"Invalid plan structure: {e}")
import json
import re

def validate_plan(raw_json, days_left, hours_per_day):
    try:
        # Remove markdown if present
        raw_json = re.sub(r"```json|```", "", raw_json).strip()
        data = json.loads(raw_json)

        if "days" not in data or not isinstance(data["days"], list):
            raise ValueError("Missing or invalid 'days' list")

        if len(data["days"]) == 0:
            raise ValueError("Plan contains no days")

        for day in data["days"]:
            if "day" not in day or "tasks" not in day:
                raise ValueError("Each day must have 'day' and 'tasks'")

            if not isinstance(day["day"], int) or day["day"] <= 0:
                raise ValueError("Day index must be a positive integer")

            if not isinstance(day["tasks"], list) or len(day["tasks"]) == 0:
                raise ValueError("Each day must contain tasks")

            total_hours = 0
            for task in day["tasks"]:
                if not all(k in task for k in ("subject", "topic", "hours")):
                    raise ValueError("Task missing required fields")

                total_hours += float(task["hours"])

            if total_hours > hours_per_day + 0.5:
                raise ValueError(
                    f"Daily hour limit exceeded on Day {day['day']}"
                )

        # Optional sanity check
        if len(data["days"]) > days_left + 2:
            raise ValueError("Plan exceeds allowed number of days")

        return data

    except Exception as e:
        raise ValueError(f"Invalid plan structure: {e}")
