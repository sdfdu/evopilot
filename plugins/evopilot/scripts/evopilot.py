#!/usr/bin/env python3
"""Command-line interface for EvoPilot."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from core import analyze_habits, context, export_data, forget, observe, remember, review_action

def main() -> int:
    p=argparse.ArgumentParser(prog="evopilot",description="Local-first adaptive memory for Codex")
    sub=p.add_subparsers(dest="command",required=True)
    o=sub.add_parser("observe");o.add_argument("app");o.add_argument("action");o.add_argument("--outcome",default="unknown",choices=["unknown","success","failure","abandoned"])
    r=sub.add_parser("remember");r.add_argument("key");r.add_argument("value");r.add_argument("--scope",default="global");r.add_argument("--confidence",type=float,default=.6)
    f=sub.add_parser("forget");f.add_argument("key")
    c=sub.add_parser("context");c.add_argument("--scope",default="global")
    h=sub.add_parser("habits");h.add_argument("--min-count",type=int,default=3)
    a=sub.add_parser("review");a.add_argument("action");a.add_argument("--details",default="")
    e=sub.add_parser("export");e.add_argument("destination",type=Path)
    args=p.parse_args()
    if args.command=="observe": result={"id":observe(args.app,args.action,args.outcome)}
    elif args.command=="remember": result=remember(args.key,args.value,scope=args.scope,confidence=args.confidence)
    elif args.command=="forget": result={"forgotten":forget(args.key)}
    elif args.command=="context": print(context(args.scope));return 0
    elif args.command=="habits": result=analyze_habits(args.min_count)
    elif args.command=="review": result=review_action(args.action,args.details)
    else: result={"path":str(export_data(args.destination))}
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0
if __name__=="__main__": raise SystemExit(main())
