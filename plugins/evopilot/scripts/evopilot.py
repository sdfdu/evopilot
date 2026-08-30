#!/usr/bin/env python3
"""Command-line interface for EvoPilot."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from core import (
    analyze_habits, analyze_sequences, authorize_once, context, correct_memory,
    compile_skill, demo, doctor, draft_skill, export_data, forget, memory_history,
    observe, remember, review_action, weekly_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(prog="evopilot", description="Local-first workflow compiler for AI agents")
    sub = parser.add_subparsers(dest="command", required=True)
    item = sub.add_parser("observe")
    item.add_argument("app")
    item.add_argument("action")
    item.add_argument("--outcome", default="unknown", choices=["unknown", "success", "failure", "abandoned"])
    item.add_argument("--session-id", default="")
    item = sub.add_parser("remember")
    item.add_argument("key")
    item.add_argument("value")
    item.add_argument("--scope", default="global")
    item.add_argument("--confidence", type=float, default=0.6)
    item.add_argument("--source", choices=["explicit", "inferred"], default="explicit")
    item = sub.add_parser("correct")
    item.add_argument("key")
    item.add_argument("value")
    item.add_argument("--scope")
    item = sub.add_parser("history")
    item.add_argument("--key")
    item.add_argument("--limit", type=int, default=50)
    item = sub.add_parser("forget")
    item.add_argument("key")
    item = sub.add_parser("context")
    item.add_argument("--scope", default="global")
    item = sub.add_parser("habits")
    item.add_argument("--min-count", type=int, default=3)
    item = sub.add_parser("sequences")
    item.add_argument("--min-count", type=int, default=3)
    item.add_argument("--max-length", type=int, default=4)
    item = sub.add_parser("review")
    item.add_argument("action")
    item.add_argument("--details", default="")
    item = sub.add_parser("approve")
    item.add_argument("approval_id")
    item.add_argument("--label", default="human-confirmed action")
    item = sub.add_parser("draft-skill")
    item.add_argument("fingerprint")
    item.add_argument("destination", type=Path)
    item = sub.add_parser("compile-skill")
    item.add_argument("fingerprint")
    item.add_argument("destination", type=Path)
    item = sub.add_parser("demo")
    item.add_argument("--destination", type=Path)
    item = sub.add_parser("doctor")
    item.add_argument("--plugin-root", type=Path)
    item = sub.add_parser("report")
    item.add_argument("--days", type=int, default=7)
    item = sub.add_parser("export")
    item.add_argument("destination", type=Path)
    args = parser.parse_args()

    if args.command == "observe":
        result = {"id": observe(args.app, args.action, args.outcome, session_id=args.session_id)}
    elif args.command == "remember":
        result = remember(args.key, args.value, scope=args.scope, confidence=args.confidence, source=args.source)
    elif args.command == "correct":
        result = correct_memory(args.key, args.value, scope=args.scope)
    elif args.command == "history":
        result = memory_history(args.key, args.limit)
    elif args.command == "forget":
        result = {"forgotten": forget(args.key)}
    elif args.command == "context":
        print(context(args.scope))
        return 0
    elif args.command == "habits":
        result = analyze_habits(args.min_count)
    elif args.command == "sequences":
        result = analyze_sequences(args.min_count, args.max_length)
    elif args.command == "review":
        result = review_action(args.action, args.details)
    elif args.command == "approve":
        result = authorize_once(args.approval_id, args.label)
    elif args.command == "draft-skill":
        result = draft_skill(args.fingerprint, args.destination)
    elif args.command == "compile-skill":
        result = compile_skill(args.fingerprint, args.destination)
    elif args.command == "demo":
        result = demo(args.destination)
    elif args.command == "doctor":
        result = doctor(args.plugin_root)
    elif args.command == "report":
        print(weekly_report(args.days))
        return 0
    else:
        result = {"path": str(export_data(args.destination))}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
