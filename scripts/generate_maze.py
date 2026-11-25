#!/usr/bin/env python3
"""Generate a static SVG contribution labyrinth from GitHub GraphQL data."""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

API = "https://api.github.com/graphql"
USERNAME = os.environ.get("GITHUB_USERNAME", "realityuncompiled")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
OUTPUT = Path(os.environ.get("OUTPUT_SVG", "assets/contribution-maze.svg"))

QUERY = '''
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
'''

PALETTE = ["#eadfd2", "#d8b8ae", "#bd8587", "#925568", "#54283f"]
INK, GOLD, PAPER = "#351a27", "#c5a46d", "#f3e8d9"
BROWN, CREAM = "#795038", "#f1d8b7"


def fetch_calendar() -> dict:
    if not TOKEN:
        raise RuntimeError("Missing GH_TOKEN/GITHUB_TOKEN environment variable.")
    payload = json.dumps({"query": QUERY, "variables": {"login": USERNAME}}).encode()
    request = urllib.request.Request(
        API, data=payload,
        headers={"Authorization": f"Bearer {TOKEN}",
                 "Content-Type": "application/json",
                 "User-Agent": "realityuncompiled-contribution-maze"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)
    if data.get("errors"):
        raise RuntimeError(f"GitHub GraphQL error: {data['errors']}")
    user = data.get("data", {}).get("user")
    if not user:
        raise RuntimeError(f"GitHub user not found: {USERNAME}")
    return user["contributionsCollection"]["contributionCalendar"]


def intensity(count: int) -> int:
    if count <= 0:
        return 0
    if count == 1:
        return 1
    if count <= 3:
        return 2
    if count <= 6:
        return 3
    return 4


def cat_svg(x: float, y: float) -> str:
    return f'''
    <g transform="translate({x:.1f},{y:.1f})" shape-rendering="crispEdges">
      <path d="M8 24 Q-1 20 2 12 Q4 7 8 11" fill="none" stroke="{BROWN}" stroke-width="4" stroke-linecap="round"/>
      <rect x="7" y="17" width="25" height="13" rx="5" fill="{BROWN}"/>
      <rect x="11" y="27" width="6" height="5" fill="{CREAM}"/>
      <rect x="25" y="27" width="6" height="5" fill="{CREAM}"/>
      <rect x="20" y="7" width="17" height="16" rx="5" fill="{BROWN}"/>
      <path d="M21 12 L21 3 L29 9 Z M30 9 L37 3 L37 13 Z" fill="{BROWN}"/>
      <path d="M23 8 L23 5 L27 9 Z M32 9 L36 5 L35 10 Z" fill="#c88e83"/>
      <rect x="25" y="14" width="2.5" height="2.5" fill="{CREAM}"/>
      <rect x="32" y="14" width="2.5" height="2.5" fill="{CREAM}"/>
      <rect x="29" y="18" width="3" height="2" fill="#d58e83"/>
      <rect x="19" y="23" width="10" height="3" fill="#9b4058"/>
      <rect x="28" y="24" width="3" height="3" fill="{GOLD}"/>
    </g>'''


def build_svg(calendar: dict) -> str:
    days = [d for week in calendar["weeks"] for d in week["contributionDays"]]
    cols = max(1, len(calendar["weeks"]))
    cell, gap = 13, 5
    left, top = 30, 91
    width, height = left * 2 + cols * (cell + gap), 255
    latest = max((i for i, d in enumerate(days) if d["contributionCount"] > 0),
                 default=max(0, len(days) - 1))
    latest_week, latest_day = min(cols - 1, latest // 7), latest % 7

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="100%" height="100%" rx="18" fill="{INK}"/>',
        f'<rect x="10" y="10" width="{width-20}" height="{height-20}" rx="13" fill="none" stroke="{GOLD}" stroke-opacity=".55"/>',
        f'<text x="30" y="39" fill="{PAPER}" font-family="Georgia,serif" font-size="20">the contribution labyrinth</text>',
        f'<text x="30" y="61" fill="#d2b8ad" font-family="monospace" font-size="10">{escape(USERNAME)} · {calendar.get("totalContributions", 0)} contributions</text>',
    ]

    for week in range(cols):
        for dow in range(7):
            idx = week * 7 + dow
            if idx >= len(days):
                continue
            day = days[idx]
            x, y = left + week * (cell + gap), top + dow * (cell + gap)
            level = intensity(day["contributionCount"])
            out.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" '
                f'fill="{PALETTE[level]}" stroke="{GOLD}" stroke-opacity=".18" stroke-width=".6">'
                f'<title>{escape(day["date"])}: {day["contributionCount"]} contributions</title></rect>'
            )
            if level >= 3:
                out.append(f'<path d="M{x+3} {y+cell/2} h{cell-6}" stroke="{INK}" stroke-opacity=".25"/>')

    cx = left + latest_week * (cell + gap) + cell / 2
    cy = top + latest_day * (cell + gap) + cell / 2
    out.append(f'<circle cx="{cx}" cy="{cy}" r="10" fill="none" stroke="{GOLD}" stroke-width="2"/>')
    cat_x = min(width - 60, max(15, cx - 20))
    cat_y = min(height - 48, max(72, cy - 31))
    out.append(cat_svg(cat_x, cat_y))
    out.extend([
        f'<text x="30" y="{height-20}" fill="#d2b8ad" font-family="monospace" font-size="9">quiet days are part of the map, too.</text>',
        '</svg>',
    ])
    return "\\n".join(out)


def main() -> None:
    calendar = fetch_calendar()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(build_svg(calendar), encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Could not generate contribution maze: {exc}", file=sys.stderr)
        raise
