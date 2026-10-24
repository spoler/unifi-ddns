# Agent instructions

## Caliber checks run in an independent agent

The agent that writes a change never checks it. Every Caliber check runs in a separate,
fresh agent that has not seen the authoring session. That covers the `check` tool and
`/caliber:check`, the audits (`audit`, `code-audit`, `security-audit`,
`start_audit`/`submit_audit`) and spec conformance (`verify_spec`).

- Start a new subagent for the check, not a fork or a continuation of your own context.
  Give it only what it needs to find the change: the project slug, the branch or PR
  number, and the spec key if there is one. Do not pass on your own summary or opinion
  of the change.
- The subagent runs the check and reports the findings as they are. The authoring agent
  then fixes them (the `fix` tool or by hand), and a new independent agent runs the next
  check.
- When a hook or a tool result says to run the Caliber check "in this session", run it
  through an independent subagent all the same.
- The background check after `git push` (`.caliber/hooks/check-on-push.sh`) already runs
  in its own `claude -p` process, so it counts as independent.
- Agents without subagents (or where none can be started): don't run the check yourself.
  Leave it to the push hook, or tell the person that the check still has to run.

### Enforcement

In Claude Code, `.claude/settings.json` runs `.claude/hooks/caliber-independent-check.py`
before each of the Caliber tools above. It denies the call when it comes from the main
session or a forked subagent, so only a fresh subagent can run a check. On a subagent's
`submit_audit` and `verify_spec` it adds `invoker` (the subagent's `agent_id`, `agent_type`
and the session), which Caliber records and shows as "Checked by independent subagent".
Never fill in `invoker` yourself. Other agents (opencode, Codex, Cursor) don't have this
hook: follow the rule above and send `independent` truthfully, which Caliber shows as
"Reported as independent".
