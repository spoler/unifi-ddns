#!/usr/bin/env python3
"""PreToolUse hook: Caliber checks run only in an independent subagent, and say so.

Claude Code adds `agent_id` to a hook's input only when the tool call comes from a
subagent. A Caliber check, audit or spec verification called from the main session
(the one that wrote the code) is denied, with a reason that tells it to delegate.
A forked subagent inherits the author's context, so it is denied as well.

A subagent's `submit_audit` and `verify_spec` get `invoker`: the stamp Caliber records
as "Checked by independent subagent" (brief assure-independent-checks). The hook
writes it last, so whatever the model put there is replaced.

The push runner (.caliber/hooks/check-on-push.sh) starts its own `claude -p` without
this repository's settings, so this hook never sees its calls.
"""
import json
import sys

STAMPED = ("submit_audit", "verify_spec")

try:
    data = json.load(sys.stdin)
except ValueError:
    sys.exit(0)

agent_id = data.get("agent_id")
agent_type = str(data.get("agent_type") or "")
tool = data.get("tool_name", "a Caliber check")

if not agent_id or agent_type.lower() == "fork":
    reason = (
        f"{tool} must run in an independent agent, not in the session that wrote the code "
        "(see AGENTS.md, \"Caliber checks run in an independent agent\"). Start a fresh "
        "subagent with the Agent tool (general-purpose, not a fork), give it the branch or "
        "PR and the project slug, and have it run the check and report the findings. Don't "
        "pass it your own assessment of the change."
    )
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))
    sys.exit(0)

if not tool.endswith(STAMPED):
    sys.exit(0)

tool_input = dict(data.get("tool_input") or {})
tool_input["invoker"] = {
    "harness": "claude-code",
    "agent_id": str(agent_id),
    "agent_type": agent_type,
    "session_id": str(data.get("session_id") or ""),
}
# No permissionDecision: the call still goes through the usual permission rules.
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "updatedInput": tool_input,
}}))
