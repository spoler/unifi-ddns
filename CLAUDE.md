@AGENTS.md

## Claude Code

- Run Caliber checks through the Agent tool with a fresh `general-purpose` subagent,
  never `subagent_type: "fork"`. The project hook
  (`.claude/hooks/caliber-independent-check.py`) denies Caliber check, audit and
  `verify_spec` calls from the main session and from forks.
- If the hook denies a call, delegate it. Don't work around the hook.
