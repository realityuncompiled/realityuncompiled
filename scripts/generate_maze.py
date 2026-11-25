#!/usr/bin/env python3

import json
import os
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

USERNAME = os.getenv("GITHUB_USERNAME", "realityuncompiled")
TOKEN = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")

OUTPUT = Path("assets/contribution-maze.svg")

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
            contributionLevel
          }
        }
      }
    }
  }
}
"""

COLORS = {
    "NONE": "#382431",
    "FIRST_QUARTILE": "#805064",
    "SECOND_QUARTILE": "#a96d7b",
    "THIRD_QUARTILE": "#d09b9b",
    "FOURTH_QUARTILE": "#f0d9c8",
}

BG = "#291923"
BORDER = "#b99570"
TEXT = "#f4e8d9"
MUTED = "#cbb5b0"
CAT = "#795038"
CAT_LIGHT = "#f1d8b7"
GOLD = "#d5ad78"


def fetch_calendar():
    if not TOKEN:
        raise RuntimeError("Missing GH_TOKEN or GITHUB_TOKEN.")

    payload = json.dumps({
        "query": QUERY,
        "variables": {"login": USERNAME}
    }).encode()

    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "realityuncompiled-contribution-garden"
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.load(response)

    if result.get("errors"):
        raise RuntimeError(result["errors"])

    user = result.get("data", {}).get("user")

    if not user:
        raise RuntimeError(f"GitHub user not found: {USERNAME}")

    return user["contributionsCollection"]["contributionCalendar"]


def draw_cat(x, y):
    return f"""
    <g transform="translate({x},{y})"
       shape-rendering="crispEdges">

      <path d="M13 47 Q-2 39 5 25 Q8 18 15 24"
            fill="none" stroke="{CAT}"
            stroke-width="6" stroke-linecap="round"/>

      <rect x="12" y="34" width="45" height="23"
            rx="9" fill="{CAT}"/>

      <rect x="20" y="53" width="10" height="7"
            fill="{CAT_LIGHT}"/>

      <rect x="43" y="53" width="10" height="7"
            fill="{CAT_LIGHT}"/>

      <rect x="34" y="14" width="31" height="29"
            rx="9" fill="{CAT}"/>

      <path d="M35 24 L35 6 L49 18 Z
               M52 18 L66 6 L66 26 Z"
            fill="{CAT}"/>

      <path d="M40 17 L40 11 L46 18 Z
               M56 18 L62 11 L61 20 Z"
            fill="#c88e83"/>

      <rect x="42" y="27" width="4" height="4"
            fill="{CAT_LIGHT}"/>

      <rect x="55" y="27" width="4" height="4"
            fill="{CAT_LIGHT}"/>

      <path d="M48 35 Q51 38 54 35"
            fill="none" stroke="{CAT_LIGHT}"
            stroke-width="1.5"/>

      <rect x="32" y="43" width="19" height="4"
            fill="#9b4058"/>

      <path d="M51 44 l5 5 -5 5 -5 -5z"
            fill="{GOLD}"/>

    </g>
    """


def render_calendar(calendar):
    weeks = calendar["weeks"]

    cell = 13
    gap = 4

    left = 54
    top = 92

    columns = len(weeks)
    grid_width = columns * (cell + gap) - gap

    panel_x = left + grid_width + 38
    width = panel_x + 112
    height = 235

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',

        f'<rect width="100%" height="100%" '
        f'rx="16" fill="{BG}"/>',

        f'<rect x="9" y="9" width="{width-18}" '
        f'height="{height-18}" rx="12" '
        f'fill="none" stroke="{BORDER}" '
        f'stroke-opacity=".7"/>',

        f'<text x="27" y="36" fill="{TEXT}" '
        f'font-family="Georgia,serif" font-size="19">'
        f'the contribution garden</text>',

        f'<text x="27" y="57" fill="{MUTED}" '
        f'font-family="monospace" font-size="10">'
        f'{escape(USERNAME)} · '
        f'{calendar["totalContributions"]} contributions '
        f'in the last year</text>'
    ]

    # Weekday labels
    weekdays = ("Sun", "Mon", "Tue", "Wed",
                "Thu", "Fri", "Sat")

    for row, label in enumerate(weekdays):
        if row in (1, 3, 5):
            y = top + row * (cell + gap) + 10

            svg.append(
                f'<text x="22" y="{y}" fill="{MUTED}" '
                f'font-family="monospace" font-size="9">'
                f'{label}</text>'
            )

    # Real contribution data, in chronological order
    for col, week in enumerate(weeks):
        for row, day in enumerate(week["contributionDays"]):

            x = left + col * (cell + gap)
            y = top + row * (cell + gap)

            level = day["contributionLevel"]
            color = COLORS.get(level, COLORS["NONE"])

            svg.append(
                f'<rect x="{x}" y="{y}" '
                f'width="{cell}" height="{cell}" '
                f'rx="3" fill="{color}" '
                f'stroke="{BORDER}" stroke-opacity=".35">'
                f'<title>{escape(day["date"])}: '
                f'{day["contributionCount"]} contributions'
                f'</title></rect>'
            )

    # Contribution intensity legend
    legend_y = top + 7 * (cell + gap) + 7

    svg.append(
        f'<text x="{left}" y="{legend_y+9}" '
        f'fill="{MUTED}" font-family="monospace" '
        f'font-size="9">less</text>'
    )

    levels = (
        "NONE",
        "FIRST_QUARTILE",
        "SECOND_QUARTILE",
        "THIRD_QUARTILE",
        "FOURTH_QUARTILE"
    )

    for i, level in enumerate(levels):
        x = left + 34 + i * 17

        svg.append(
            f'<rect x="{x}" y="{legend_y}" '
            f'width="12" height="12" rx="3" '
            f'fill="{COLORS[level]}"/>'
        )

    svg.append(
        f'<text x="{left+34+5*17+4}" '
        f'y="{legend_y+9}" fill="{MUTED}" '
        f'font-family="monospace" font-size="9">'
        f'more</text>'
    )

    # Cat gets its own territory.
    svg.append(
        f'<path d="M{panel_x-18} 78 V{height-24}" '
        f'stroke="{BORDER}" stroke-opacity=".35" '
        f'stroke-dasharray="3 5"/>'
    )

    svg.append(draw_cat(panel_x, 112))

    svg.append(
        f'<text x="{panel_x-2}" y="194" '
        f'fill="{TEXT}" font-family="Georgia,serif" '
        f'font-size="12">still wandering.</text>'
    )

    svg.append(
        f'<text x="{panel_x-2}" y="209" '
        f'fill="{MUTED}" font-family="monospace" '
        f'font-size="8">one square at a time</text>'
    )

    svg.append("</svg>")

    return "\n".join(svg)


def main():
    calendar = fetch_calendar()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT.write_text(
        render_calendar(calendar),
        encoding="utf-8"
    )

    print(f"Updated {OUTPUT}")


if __name__ == "__main__":
    main()
