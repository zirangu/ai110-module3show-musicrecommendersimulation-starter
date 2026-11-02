"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


def print_recommendations_table(recommendations) -> None:
    """Prints recommendations as a table, including each song's score and reasons."""
    rows = [
        [rank, song["title"], song["artist"], song["genre"], song["mood"], f"{score:.2f}", explanation]
        for rank, (song, score, explanation) in enumerate(recommendations, start=1)
    ]
    headers = ["#", "Title", "Artist", "Genre", "Mood", "Score", "Reasons"]

    if HAS_TABULATE:
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    else:
        widths = [max(len(str(r[i])) for r in [headers] + rows) for i in range(len(headers))]
        def fmt_row(row):
            return " | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))
        print(fmt_row(headers))
        print("-+-".join("-" * w for w in widths))
        for row in rows:
            print(fmt_row(row))


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print(f"\nBased on your preferences ({user_prefs}), here are your top {len(recommendations)} recommendations:\n")
    print_recommendations_table(recommendations)


if __name__ == "__main__":
    main()
