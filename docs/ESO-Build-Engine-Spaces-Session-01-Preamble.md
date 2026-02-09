# ESO Build Engine – Spaces Session 01 Preamble (Initial Alignment Thread)

> PURPOSE  
> Define the rules and context for **Spaces Session 01**, the initial alignment thread for the ESO Build Engine – Permafrost Marshal project.[file:25]

## Session 01 scope

- Establish shared understanding of:
  - The overall ESO Build Engine architecture (data/logic/UI).
  - The v1 Data Model and Global Rules.
  - The Data Center scope and toolchain.[file:1][file:2][file:3][file:4]
- Produce:
  - A prioritized view of control documents.
  - A work plan that puts the Data Center scope first.
  - Naming and storage conventions for Spaces transcripts and prompts.[file:23][file:25]

## Session-specific documents and roles

For this session, treat these as especially central:[file:23][file:25]

- `docs/ESO-Build-Engine-Data-Center-Scope.md`  
  Active focus; defines the data center infrastructure, repo layout, tools, backend, frontend, and workflows.[file:4]

- `docs/ESO-Build-Engine-Overview.md`  
  Non-negotiable architecture and process rules; must be respected by all design decisions.[file:1]

- `docs/ESO-Build-Engine-Data-Model-v1.md`  
  JSON schema contract for `data/*.json` and `builds/permafrost-marshal.json`.[file:2]

- `docs/ESO-Build-Engine-Global-Rules.md`  
  Structural rules (bars, gear, CP) and Python function contracts for validators and effect math.[file:3]

- `docs/ESO Build Engine – Data Center Tool Checklist.md`  
  Status view for which tools and data pieces from the Data Center scope are [DONE] vs [PLANNED] vs [LATER].[file:7]

- `docs/ESO Build Engine – Copilot Bootstrap.md`  
  How AI must behave when editing this repo (full-file outputs, no hidden state, no external DBs).[file:6][file:24]

## Session 01 constraints for AI

During Session 01, AI assistants must:[file:23][file:25]

1. Treat the Data Center scope as the current active focus and frame other docs relative to it (dependencies and consumers).[file:4]
2. Avoid introducing new rules that contradict:
   - Overview
   - Data Model v1
   - Global Rules
   - Data Center Scope
   - Copilot Bootstrap.[file:1][file:2][file:3][file:4][file:6]
3. When suggesting changes:
   - Always provide full file contents and exact paths.
   - Keep logic in `tools/*.py` and JSON in `data/` and `builds/`.[file:3][file:4][file:24]
4. When planning future work:
   - Put completion and clarification of the Data Center scope before expansion into the larger ESO Build Database project.[file:4][file:5][file:23]

## How this preamble is used

- Place this preamble at the very top of the markdown file that captures the **Session 01** transcript.
- Future sessions (Session 02, 03, etc.) should have their own `...-Session-0X-Preamble.md` files referring back to this initial alignment where relevant.[file:23][file:25]
