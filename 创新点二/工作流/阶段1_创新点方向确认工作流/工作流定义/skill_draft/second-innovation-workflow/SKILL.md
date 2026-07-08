---
name: second-innovation-workflow
description: Dissertation second-innovation workflow for the current thesis workspace. Use when the user asks to start, continue, or resume the second innovation point process, including requests such as "开始第二创新点构思", "启动第二创新点工作流", "继续第二创新点筛选", "继续第二创新点构思", or equivalent requests to run the staged workflow for constraint alignment, gap analysis, candidate generation, comparison, literature search, and plan landing under `创新点二/`.
---

# Second Innovation Workflow

Execute the second-innovation workflow for this dissertation workspace. Treat this as a workspace-specific process, not a general brainstorming task.

## Load Order

Read these files in order before taking substantive action:

1. `创新点二/工作流/阶段1_创新点方向确认工作流/工作流定义/阶段1_创新点方向确认硬规则卡片.md`
2. `创新点二/工作流/阶段1_创新点方向确认工作流/工作流定义/阶段1_创新点方向确认执行摘要.md`
3. `创新点二/工作流/阶段1_创新点方向确认工作流/工作流定义/阶段1_创新点方向确认阶段执行模板.md`
4. `创新点二/工作流/阶段1_创新点方向确认工作流/工作流定义/阶段1_创新点方向确认工作流规范.md` only when boundary checks, detailed rules, or naming conventions need to be confirmed

## Hard Boundaries

Enforce these rules throughout the run:

- Do not read or rely on `创新点二/工作流/阶段1_创新点方向确认工作流/运行记录/待定方向/待定方向汇总.md` unless the user explicitly lifts the restriction.
- Do not read or rely on any file under `创新点二/工作流/阶段1_创新点方向确认工作流/运行记录/工作流轮次1` unless the user explicitly lifts the restriction.
- Keep the unfinished second innovation point neutral. Do not write it as a fixed direction or completed result.
- Prefer general, high-importance problems that can still be justified by recent literature.
- Prefer directions that connect naturally to the completed small paper and can be validated by simulation.
- Do not default to the nonstationary-jitter direction.
- When making claims about research status, importance, maturity, or comparisons, search online for real papers and keep a search log.
- Handle one local problem at a time even when the user gives a broad workflow request.

## Trigger Handling

If the user explicitly names a phase, execute only that phase.

If the user says "开始第二创新点构思" or gives an equivalent broad start request without naming a phase:

1. Determine whether there is an accessible ongoing workflow round under `创新点二/工作流/阶段1_创新点方向确认工作流/运行记录/` other than the forbidden `工作流轮次1`.
2. If the user named a target round, use that round.
3. If no usable round is specified or available, start a new round and begin from phase 1.
4. If the current phase is unclear, resolve it conservatively:
   - start with phase 1 when the boundaries are not yet consolidated;
   - start with phase 2 when boundaries are already clear but the coverage map is not;
   - otherwise ask only if the ambiguity blocks safe progress.

Default to single-phase advancement. Do not run the entire workflow end-to-end in one pass unless the user explicitly asks for continuous multi-phase execution. Even for broad start requests, complete only the current best-next phase, then stop and report whether moving to the next phase is advisable.

## Phase Execution

Use the stage template file to structure outputs and documents.

### Phase 1: Constraint Alignment

- Consolidate thesis objective, proposal boundaries, completed-paper coverage, and current restrictions.
- Output or update the phase-1 document for the active workflow round.

### Phase 2: Structural Decomposition

- Decompose the thesis mainline into subproblems.
- Mark covered and uncovered parts.
- Identify uncovered regions that are worth developing into the second innovation point.
- Output or update the phase-2 document for the active workflow round.

### Phase 3: Candidate Generation

- Generate 3 to 5 candidates in a uniform format.
- For each candidate, include the problem, link to the first paper, method sketch, feasibility, risk, and supporting literature.
- Output or update the phase-3 document for the active workflow round.

### Phase 4: Comparison and Selection

- Compare candidates on innovation, feasibility, difference from the first innovation, and structural support for the dissertation.
- Produce a main choice, a backup choice, and rejected options with reasons and paper support.
- Output or update the phase-4 document for the active workflow round.

### Phase 5: Plan Landing

- Expand the selected direction into problem definition, method idea, technical route, experiment design, expected contribution, and chapter placement.
- Keep all unfinished claims neutral.
- Output or update the phase-5 document for the active workflow round.

## Literature Search Protocol

Do not rely on a single natural-language query. For any research-status or importance judgment:

1. Define the exact judgment the search must support.
2. Build multiple query families:
   - task terms
   - method terms
   - scenario terms
   - metric terms
   - synonym, abbreviation, and variant terms
   - exclusion terms when needed
3. Search across multiple source baskets instead of a single entry point.
4. Perform forward and backward citation tracing for high-relevance papers.
5. Record a search log with:
   - query families
   - source baskets
   - new papers
   - duplicates
   - high-relevance core papers
   - current gaps
   - stop reason

Treat the collection as stable only when recent rounds add mostly duplicates or minor variants. Do not claim absolute completeness.

## Output Discipline

For each run:

- state the current phase
- state the single local objective
- use the corresponding stage template structure
- cite real papers when required
- preserve unresolved issues and next actions
- end with a short recommendation on whether to enter the next phase
- do not automatically continue into the next phase without explicit user direction

If a rule conflict or evidence gap blocks safe progress, stop and ask the user only about that blocking point.




