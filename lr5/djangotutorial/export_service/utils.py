import csv
from io import StringIO


def poll_stats_to_csv(stats: dict) -> str:
    buffer = StringIO()
    writer = csv.writer(buffer)

    writer.writerow(["Question", stats["question"]])
    writer.writerow(["Published at", stats["published_at"]])
    writer.writerow(["Total votes", stats["total_votes"]])
    writer.writerow([])
    writer.writerow(["Choice", "Votes", "Percent"])

    for choice in stats["choices"]:
        writer.writerow([
            choice["text"],
            choice["votes"],
            choice["percent"],
        ])

    return buffer.getvalue()
