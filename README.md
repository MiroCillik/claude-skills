# claude-skills

Personal Claude Code plugin marketplace.

## Install

```
/plugin marketplace add MiroCillik/claude-skills
/plugin install miro-engineering@miro-claude-skills
/plugin install miro-code-review@miro-claude-skills
```

## Skills

### miro-engineering

- `architecting-multi-session-delivery`: run a multi-repo initiative with one architect session and several developer Claude Code sessions (S1–Sn). It covers contracts, the Linear issue tree, the delivery playbook, kickoff prompts, SendMessage formats, peer review and owner-only merges. `playbook-template.md` holds the playbook and the kickoff prompt template.
  - Works best with the `kbl-engineering` plugin (`kbl-file-linear`) and the Linear MCP server.
  - Invoke it with `/miro-engineering:architecting-multi-session-delivery`, or ask Claude to act as architect over developer sessions.

### miro-code-review

The skills behind Revi, the PR review bot. See [plugins/miro-code-review/README.md](plugins/miro-code-review/README.md) for details and setup.

- `pr-review-style`: how to review a PR and write review comments (one line plus bullets, Linear first, `nit:` rules, verdict rules, re-reviews), how to answer review comments on your own PR, and code rules for PR code. Works in any agent.
- `pr-review-agent`: runs a scheduled reviewer that posts reviews without asking: a queue gate script, a retry guard, pre-post checks, extra security and CI checks, and the run summary format. Built for Hermes Agent cron jobs.

## License

MIT, see [LICENSE](LICENSE).
