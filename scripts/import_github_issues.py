#!/usr/bin/env python3
"""Import tickets.csv as GitHub issues. Requires: gh auth login"""
import csv
import subprocess
import sys

PRIORITY_TO_LABEL = {
    "Critical": "priority:critical",
    "High": "priority:high",
    "Normal": "priority:normal",
}


def main(csv_path: str) -> None:
    with open(csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            labels = [l.strip() for l in row["labels"].split(",") if l.strip()]
            labels.append(PRIORITY_TO_LABEL.get(row["priority"], ""))
            labels = [l for l in labels if l]

            body = f"""## Description
{row['description']}

## Acceptance Criteria
{row['acceptance_criteria']}

## Meta
- **Epic:** {row['epic']}
- **Estimate:** {row['estimate']}
- **Dependencies:** {row['dependencies']}
- **Milestone:** {row['milestone']}
"""
            cmd = [
                "gh",
                "issue",
                "create",
                "--title",
                f"[{row['id']}] {row['title']}",
                "--body",
                body,
            ]
            for label in labels:
                cmd.extend(["--label", label])
            if row.get("milestone"):
                cmd.extend(["--milestone", row["milestone"]])

            print(f"Creating {row['id']}...")
            subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "tickets.csv")
