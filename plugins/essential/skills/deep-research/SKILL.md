---
name: deep-research
description: Conduct comprehensive multi-source research with AI-powered analysis. Use when investigating complex topics, gathering information from multiple sources, or synthesizing research findings.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Task, Read, Write, Edit, MultiEdit, WebSearch, WebFetch, Grep, Glob, TodoWrite
argument-hint: <research-topic> [optional-focus-area]
---

# Deep Research Command

Conduct systematic, multi-source research on specified topics using AI-powered analysis and cross-referenced insights.

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Generate research without source attribution
- Create content without verification

**When to REJECT**:

- Topic is better suited for simple web search

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Planning

1. **Analyze Requirements**
   - Parse research topic from $ARGUMENTS
   - Identify optional focus areas
   - Determine research scope and boundaries
   - **Select Research Strategy** based on topic type:
     - **Technical/Scientific**: Prioritize academic papers, documentation, code repos
     - **Historical**: Focus on primary sources, archives, temporal progression
     - **Current Events**: Emphasize recent sources, news, real-time updates
     - **Theoretical/Conceptual**: Balance foundational texts with recent developments
     - **Product/Market**: Industry reports, user feedback, competitive analysis
   - Plan source discovery strategy aligned with selected approach

2. **Initialize Research Infrastructure**
   - Create research workspace: `research_$ARGUMENTS_$(date +%Y%m%d)`
   - Initialize source tracker: `source_tracker.md`
   - Set up finding templates for cross-source insights
   - **Check for existing research sessions**: Look for `source_tracker.md` in workspace
     - If exists: Resume from last state (check status fields)
     - Auto-save progress to tracker after each source analysis
     - Tracker serves as both documentation and checkpoint
     - Resume capability: Continue from any 'pending' or 'analyzing' sources

3. **Identify Applicable Workflows & Standards**
   - Identify any relevant workflows for research processes
   - Identify any related documentation standards
   - Note: MUST follow any matching workflows and standards

4. **Delegation Decision**
   - Plan parallel source analysis tasks
   - Identify specialized research agents needed
   - Define synthesis coordination points

5. **Risk Assessment**
   - Identify potential source reliability issues
   - Plan verification strategies
   - Note information gaps

### Step 2: Execution

1. **Workflow Compliance**
   - MUST follow workflows identified in Phase 1
   - Apply research methodology standards
   - Reference specific workflow files when applicable

2. **Primary Implementation**
   - Dispatch subagents for iterative source analysis
   - Each agent analyzes assigned sources for:
     - Key information relevant to topic
     - Cross-source patterns and themes
     - Contradictions and debates
     - **NEW INSIGHTS requiring further research**
   - Update source tracker with analysis status
   - **CRITICAL: When finding new insights, discover additional sources**

3. **Cross-Source Finding Format**
   - Pattern/Theme identification
   - Evidence compilation from multiple sources
   - Implication analysis for research topic
   - Source attribution with locations

4. **Iterative Deep Research Strategy**
   - **Discovery Triggers**: When subagents identify:
     - Unfamiliar concepts or terminology
     - References to related work
     - Gaps in understanding
     - Contradictory information requiring more context
   - **Action Protocol**:
     1. Add discovered sources to tracker immediately
     2. Spawn new research tasks for high-relevance discoveries
     3. Update finding files with connection chains
     4. Document research depth (initial → level 2 → level 3)
   - **Depth Limits**: Maximum 3 levels of iterative discovery
   - **Priority Management**: High-relevance discoveries analyzed first

5. **Edge Case Handling**
   - No sources found: Expand search parameters
   - **Duplicate sources**: Check content similarity before analysis
   - Conflicting information: Document all perspectives
   - Subagent timeout: Mark as failed, continue with available data
   - Discovery overflow: Prioritize by relevance + credibility
   - Circular references: Document but don't re-analyze
   - **Early termination**: If high-confidence convergent evidence achieved

### Step 3: Verification

1. **Quality Assurance**
   - Verify all sources marked as analyzed have summaries
   - **Confirm discovered sources are tracked and processed**
   - Cross-reference findings across multiple sources
   - Identify contradictions between sources
   - Flag gaps in research coverage
   - **Validate discovery chains (source → insight → new source)**

2. **Consolidation Tasks**
   - Merge similar findings from different subagents
   - Resolve conflicting information with source priority
   - **Apply Synthesis Framework**:
     - **Convergent Evidence**: Multiple sources supporting same conclusion
     - **Divergent Perspectives**: Document contrasting viewpoints with context
     - **Confidence Scoring**: Weight findings by source credibility + convergence
     - **Knowledge Gaps**: Explicitly mark where evidence is insufficient
   - Create synthesis notes for complex topics with confidence levels

3. **Source Validation**
   - Confirm source reliability and credibility
   - Check for citation accuracy
   - Verify quotes and references

4. **Side Effect Validation**
   - Clean temporary sketchpad files
   - Ensure all findings traceable to sources
   - Verify workspace organization

### Step 4: Reporting

**Output Format**:

```text
[✅/❌] Research: $ARGUMENTS

## Summary
- Initial sources: [count]
- **Discovered sources: [count] (across [N] levels)**
- Total sources analyzed: [count]
- **Duplicates detected: [count]**
- Key findings: [count]
- Research gaps: [count]
- **Overall confidence**: [High/Medium/Low]
- **Discovery depth reached: [1-3 levels]**
- **Credibility distribution**: Academic:[N] | Official:[N] | Industry:[N] | Community:[N]

## Executive Summary
[3-5 sentence overview of key discoveries]

## Key Findings
### Finding 1: [Title] (Confidence: High/Medium/Low)
- **Evidence**: [Sources and quotes with credibility indicators]
- **Convergence**: [N sources agree] | [M sources disagree]
- **Significance**: [Why this matters]

### Finding 2: [Title] (Confidence: High/Medium/Low)
[Continue pattern...]

## Thematic Analysis
### Theme A: [Emergent Pattern]
[Synthesis across multiple findings]

## Debates and Contradictions
[Areas where sources disagree]

## Discovery Chains
### Chain 1: [Initial Topic → Discovery]
- Started with: [initial source]
- Led to discovery of: [concept/source]
- Further revealed: [deeper insight]

### Chain 2: [Another Discovery Path]
[Continue pattern...]

## Research Gaps
[What wasn't found or needs further investigation]

## References
[Complete source list with access information, grouped by discovery level]
### Level 1 (Initial Sources)
- [Source 1]
- [Source 2]

### Level 2 (Discovered from initial research)
- [Source A] ← discovered from [Source 1]
- [Source B] ← discovered from [Source 2]

### Level 3 (Deep discoveries)
- [Source X] ← discovered from [Source A]
```

## 📝 Examples

### Basic Research

```bash
/deep-research "quantum computing applications"
# Conducts comprehensive research on quantum computing uses
```

### Focused Research

```bash
/deep-research "machine learning" "healthcare applications"
# Researches ML specifically in healthcare context
```

### Complex Multi-Domain Research

```bash
/deep-research "climate change impact on global supply chains"
# Analyzes intersection of climate and supply chain topics
```

### Iterative Discovery Research

```bash
/deep-research "emerging AI safety frameworks"
# Initial search finds 3 sources
# Agent A discovers reference to "constitutional AI" → adds 2 new sources
# Agent B finds mention of "RLHF techniques" → triggers deep dive with 4 sources
# Agent C identifies "red teaming methodologies" → spawns specialized search
# Result: 15 total sources analyzed across 3 discovery levels
```

### Parallel Source Analysis

```bash
/deep-research "blockchain scalability solutions"
# Automatically delegates to:
#   - Agent A: Academic papers analysis
#   - Agent B: Industry reports (parallel)
#   - Agent C: Technical documentation (parallel)
#   - Agent D: Synthesis and consolidation
```

### Error Case Handling

```bash
/deep-research "classified-information"
# Error: Topic requires restricted access
# Suggestion: Refine to publicly available information
# Alternative: Focus on general concepts instead
```
