import pandas as pd

def completion_stats(df):
    total = len(df)
    done = df["completed"].sum()
    return round((done / total) * 100, 2) if total else 0
