# claude-skills

Personal Claude Code plugin marketplace.

## Install

```
/plugin marketplace add MiroCillik/claude-skills
/plugin install miro-engineering@miro-claude-skills
```

## Skills

### miro-engineering

- `architecting-multi-session-delivery`: run a multi-repo initiative with one architect session and several developer Claude Code sessions (S1–Sn). It covers contracts, the Linear issue tree, the delivery playbook, kickoff prompts, SendMessage formats, peer review and owner-only merges. `playbook-template.md` holds the playbook and the kickoff prompt template.
  - Works best with the `kbl-engineering` plugin (`kbl-file-linear`) and the Linear MCP server.
  - Invoke it with `/miro-engineering:architecting-multi-session-delivery`, or ask Claude to act as architect over developer sessions.

## License

MIT, see [LICENSE](LICENSE).
