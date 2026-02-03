# def flatten_plan(plan):
#     rows = []
#     for day in plan["days"]:
#         for task in day["tasks"]:
#             rows.append({
#                 "date": day["date"],
#                 "subject": task["subject"],
#                 "topic": task["topic"],
#                 "hours": task["hours"],
#                 "completed": False
#             })
#     return rows
from datetime import date, timedelta

def flatten_plan(plan):
    rows = []
    start_date = date.today()

    for day in plan["days"]:
        real_date = start_date + timedelta(days=day["day"] - 1)

        for task in day["tasks"]:
            rows.append({
                "date": real_date.isoformat(),
                "subject": task["subject"],
                "topic": task["topic"],
                "hours": task["hours"],
                "completed": False
            })

    return rows
