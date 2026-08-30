"""Render the README demo GIF from a deterministic workflow-compiler storyboard."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "demo.gif"
W, H = 1200, 675
BG = "#080d1a"
PANEL = "#11192b"
TEXT = "#e4e9f2"
MUTED = "#8895aa"
PURPLE = "#a894ff"
GREEN = "#62e6a7"
AMBER = "#ffd080"


def font(size, bold=False):
    candidates = [
        Path("C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


TITLE = font(34, True)
BODY = font(21)
BOLD = font(20, True)
SMALL = font(17)

STORY = [
    (
        "1. Work normally",
        [
            ("signal", "workspace:inspect  ->  workspace:apply_patch  ->  terminal:test"),
            ("signal", "Outcome: success  |  raw arguments and responses are not stored"),
        ],
    ),
    (
        "2. Repetition becomes evidence",
        [
            ("evopilot", "Same 3-step sequence observed 5 times"),
            ("evopilot", "4 successful outcomes  |  success rate 80%  |  status: draft_ready"),
        ],
    ),
    (
        "3. Compile the workflow",
        [
            ("you", "> Compile my strongest proven workflow."),
            ("evopilot", "Created portable Open Agent Skills bundle"),
        ],
    ),
    (
        "4. Inspect the artifact",
        [
            ("file", "SKILL.md       workflow instructions + safety boundaries"),
            ("file", "evopilot.json  provenance + evidence + pending_human_review"),
        ],
    ),
    (
        "5. Validate before review",
        [
            ("evopilot", "Quality score: 100 / 100  |  all structural checks passed"),
            ("policy", "Does not execute the workflow or promise universal compatibility"),
        ],
    ),
    (
        "6. Human review stays in control",
        [
            ("policy", "Generated Skill is NOT installed automatically"),
            ("policy", "New permissions, publishing, and destructive actions require approval"),
        ],
    ),
    (
        "Your agent gets better from real work",
        [
            ("evopilot", "Repeat  ->  measure  ->  compile  ->  review  ->  reuse"),
            ("evopilot", "Local-first. Evidence-backed. Portable. Inspectable."),
        ],
    ),
]


def frame(index, subtitle, lines):
    image = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((45, 38, W - 45, H - 38), radius=22, fill=PANEL, outline="#2b3751", width=2)
    draw.ellipse((73, 65, 89, 81), fill="#ff6b6b")
    draw.ellipse((99, 65, 115, 81), fill="#ffd166")
    draw.ellipse((125, 65, 141, 81), fill=GREEN)
    draw.text((170, 57), "EVOPILOT  /  WORKFLOW COMPILER", font=SMALL, fill=MUTED)
    draw.text((78, 122), subtitle, font=TITLE, fill="#f7f9ff")
    draw.text((1040, 125), f"{index + 1}/{len(STORY)}", font=SMALL, fill=MUTED)

    colors = {"you": PURPLE, "evopilot": GREEN, "signal": MUTED, "file": AMBER, "policy": "#ff8392"}
    labels = {"you": "YOU", "evopilot": "EVOPILOT", "signal": "SIGNAL", "file": "BUNDLE", "policy": "POLICY"}
    y = 220
    for role, text in lines:
        color = colors[role]
        draw.text((82, y), labels[role], font=BOLD, fill=color)
        draw.rounded_rectangle((220, y - 8, W - 82, y + 52), radius=10, fill="#0b1222", outline="#293651")
        draw.text((244, y + 8), text, font=BODY, fill=TEXT)
        y += 92

    progress_y = H - 132
    width = (W - 164) / len(STORY)
    for step in range(len(STORY)):
        x1 = 82 + step * width
        x2 = x1 + width - 10
        draw.rounded_rectangle((x1, progress_y, x2, progress_y + 7), radius=3, fill=PURPLE if step <= index else "#293651")
    draw.text((82, H - 91), "Turn repeated successful work into a reusable Agent Skill.", font=SMALL, fill=MUTED)
    draw.text((W - 345, H - 91), "github.com/sdfdu/evopilot", font=SMALL, fill=PURPLE)
    return image


OUT.parent.mkdir(parents=True, exist_ok=True)
frames = [frame(index, *item) for index, item in enumerate(STORY)]
frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=[1900] * len(frames), loop=0, optimize=True)
print(OUT)
