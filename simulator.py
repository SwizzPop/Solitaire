import random
import sqlite3
from collections import Counter
from pathlib import Path

MAXRUNS = 5
SIMS_PER_RUN = 50000

origArray = [[1, 1], [1, 2], [1, 3], [1, 4], [2, 1], [2, 2], [2, 3], [2, 4], [3, 1], [3, 2], [3, 3], [3, 4],
             [4, 1], [4, 2], [4, 3], [4, 4], [5, 1], [5, 2], [5, 3], [5, 4], [6, 1], [6, 2], [6, 3], [6, 4], [7, 1],
             [7, 2], [7, 3], [7, 4],
             [8, 1], [8, 2], [8, 3], [8, 4], [9, 1], [9, 2], [9, 3], [9, 4], [10, 1], [10, 2], [10, 3], [10, 4],
             [11, 1], [11, 2], [11, 3], [11, 4], [12, 1], [12, 2], [12, 3], [12, 4], [13, 1], [13, 2], [13, 3],
             [13, 4], ]

dealt = ['']


def deal():
    random.shuffle(dealt)


def check():
    i = 3
    while i <= len(dealt) - 1:
        if origArray[dealt[i]][0] == origArray[dealt[i - 3]][0]:
            del dealt[i - 3]
            del dealt[i - 3]
            del dealt[i - 3]
            del dealt[i - 3]
            if i - 4 < 3:
                i = 3
            else:
                i -= 4
        elif origArray[dealt[i]][1] == origArray[dealt[i-3]][1]:
            del dealt[i - 2]
            del dealt[i - 2]
            if i - 2 < 3:
                i = 3
            else:
                i -= 2
        else:
            i += 1
    return len(dealt)

def init_database():
    """Initialize the SQLite database and create necessary table if it doesn't exist"""
    conn = sqlite3.connect('simulator.db')
    cursor = conn.cursor()
    
    # Create the results table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solitare (
            Results INTEGER PRIMARY KEY,
            Count INTEGER DEFAULT 0
        )
    ''')
    
    # Initialize all possible results (0-52) if table is empty
    cursor.execute('SELECT COUNT(*) FROM solitare')
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            'INSERT INTO solitare (Results, Count) VALUES (?, 0)',
            [(i,) for i in range(53)]
        )
    
    conn.commit()
    conn.close()

def updateDB(results):
    try:
        resultsRemaining = list(Counter(results).keys())
        resultsCount = list(Counter(results).values())

        conn = sqlite3.connect('simulator.db')
        cursor = conn.cursor()

        # Update counts for each result
        for remaining, count in zip(resultsRemaining, resultsCount):
            cursor.execute(
                "UPDATE solitare SET Count = Count + ? WHERE Results = ?", 
                (count, remaining)
            )

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")
        return


init_database()

total = 0
while total < MAXRUNS:
    results = []
    for x in range(SIMS_PER_RUN):
        dealt = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
                 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, ]
        deal()
        results.append(check())

    # Read existing results
    existing_stats = Counter()
    try:
        with open("solitaire.txt", "r") as file:
            for line in file:
                remaining_cards, count = map(int, line.strip().split())
                existing_stats[remaining_cards] = count
    except FileNotFoundError:
        pass  # File doesn't exist yet, start with empty counter

    # Update statistics with new results
    new_stats = Counter(results)
    combined_stats = existing_stats + new_stats

    # Write updated results back to file
    with open("solitaire.txt", "w") as file:
        for remaining_cards in range(53):  # 0 to 52 inclusive
            if remaining_cards in combined_stats:
                file.write(f"{remaining_cards} {combined_stats[remaining_cards]}\n")
            else:
                file.write(f"{remaining_cards} 0\n")

    updateDB(results)
    total += 1
    print(f"Simulation round number {total} completed.")
print(f"Completed {total * SIMS_PER_RUN} simulations.")