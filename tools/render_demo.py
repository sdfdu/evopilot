"""Render the README demo GIF from a deterministic terminal storyboard."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"docs"/"demo.gif"
W,H=1200,675
BG="#0b1020"; PANEL="#121a2d"; TEXT="#d8e1f0"; MUTED="#8491a8"; PURPLE="#9b87f5"; GREEN="#5ee3a1"; AMBER="#ffca80"

def font(size,bold=False):
 candidates=[Path("C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf"),Path("C:/Windows/Fonts/arial.ttf")]
 for candidate in candidates:
  if candidate.exists():return ImageFont.truetype(str(candidate),size)
 return ImageFont.load_default()

TITLE=font(34,True); BODY=font(22); BOLD=font(22,True); SMALL=font(17)
story=[
 ("Start with a vague idea",[("you","> Help me turn this idea into a useful agent."),("evopilot","Idea Lab activated — I will discuss choices before building.")]),
 ("Learn an explicit preference",[("you","> Remember: show the conclusion before details."),("evopilot","Saved locally · confidence 0.60 · evidence 1")]),
 ("Observe outcomes, not private content",[("system","tool: run_tests · outcome: success"),("system","tool: apply_patch · outcome: success"),("evopilot","Raw commands and outputs were not stored.")]),
 ("Detect repeated habits",[("you","> Analyze my workflow habits."),("evopilot","Candidate: run tests after edits · evidence 3 · confidence 0.78")]),
 ("Promote what works",[("evopilot","Workflow reached promotion threshold."),("evopilot","Drafted Skill: test-after-edit · validation passed")]),
 ("Keep dangerous actions human-approved",[("agent","> Proposed action: enable_mcp"),("policy","HUMAN REQUIRED · new permission boundary")]),
 ("Grow safely over time",[("evopilot","Observe → Measure → Promote → Test → Roll back"),("evopilot","Your instructions always override learned memory.")]),
]

def frame(index,subtitle,lines):
 im=Image.new("RGB",(W,H),BG);d=ImageDraw.Draw(im)
 d.rounded_rectangle((45,38,W-45,H-38),radius=22,fill=PANEL,outline="#28344e",width=2)
 d.ellipse((73,65,89,81),fill="#ff6b6b");d.ellipse((99,65,115,81),fill="#ffd166");d.ellipse((125,65,141,81),fill="#5ee3a1")
 d.text((170,57),"EVOPILOT  /  ADAPTIVE CODEX COPILOT",font=SMALL,fill=MUTED)
 d.text((78,122),subtitle,font=TITLE,fill="#f4f7ff")
 d.text((1040,125),f"{index+1}/{len(story)}",font=SMALL,fill=MUTED)
 y=212
 colors={"you":PURPLE,"evopilot":GREEN,"system":MUTED,"agent":AMBER,"policy":"#ff7f8e"}
 labels={"you":"YOU","evopilot":"EVOPILOT","system":"SIGNAL","agent":"AGENT","policy":"POLICY"}
 for role,text in lines:
  color=colors[role];d.text((82,y),labels[role],font=BOLD,fill=color)
  d.rounded_rectangle((220,y-7,W-82,y+51),radius=10,fill="#0d1425",outline="#26334c")
  d.text((244,y+7),text,font=BODY,fill=TEXT);y+=88
 d.line((82,H-110,W-82,H-110),fill="#26334c",width=1)
 d.text((82,H-87),"Local-first  •  inspectable memory  •  versioned extensions  •  human-in-the-loop",font=SMALL,fill=MUTED)
 d.text((W-245,H-87),"github.com/sdfdu/evopilot",font=SMALL,fill=PURPLE)
 return im

OUT.parent.mkdir(parents=True,exist_ok=True)
frames=[frame(i,*item) for i,item in enumerate(story)]
frames[0].save(OUT,save_all=True,append_images=frames[1:],duration=[1800]*len(frames),loop=0,optimize=True)
print(OUT)
