# LLM Prompt Templates

This document contains all prompt templates used in Ultra Deep Research. Each prompt is designed to produce specific, structured outputs optimized for the research pipeline.

## Table of Contents

1. [Reconnaissance Prompts](#reconnaissance-prompts)
2. [Query Generation Prompts](#query-generation-prompts)
3. [Context Extraction Prompts](#context-extraction-prompts)
4. [Synthesis Prompts](#synthesis-prompts)

---

## Reconnaissance Prompts

### 1.1 Overview Query Generation

**Purpose**: Generate a single, comprehensive query to understand a topic broadly.

**Model**: Claude Haiku 4.5

**Template**:
```
Generate ONE comprehensive search query to get a broad overview of the following topic:

TOPIC: {topic}

The query should be optimized for a search engine and help us understand:
- What this topic fundamentally is
- Key components, concepts, or dimensions
- Current state and recent developments
- Why it matters or its significance
- Major applications or implications

Requirements:
- Single query only (not multiple queries)
- Specific enough to get detailed results
- Broad enough to cover the full scope
- Natural language, optimized for search
- No more than 20 words

Return ONLY the query text, nothing else.
```

**Example Input**:
```
TOPIC: quantum computing for drug discovery
```

**Expected Output**:
```
What is quantum computing's role in drug discovery, including current applications, key algorithms, and recent breakthroughs?
```

---

## Query Generation Prompts

### 2.1 Deep Research Query Generation

**Purpose**: Generate 100+ targeted, diverse queries based on reconnaissance context.

**Model**: Claude Haiku 4.5

**Template**:
```
You are a research strategist generating search queries for ultra-deep research.

ORIGINAL TOPIC: {topic}

RECONNAISSANCE OVERVIEW:
{overview_result}

KEY CONTEXT FROM INITIAL RESEARCH:
- Subtopics: {subtopics}
- Key Entities: {entities}
- Terminology: {terminology}
- Research Angles: {research_angles}

TASK:
Generate exactly {num_queries} diverse, specific search queries to comprehensively research this topic.

DISTRIBUTION REQUIREMENTS:
- 20% Foundational queries (what, why, history, core concepts)
- 15% Technical queries (how it works, mechanisms, architecture)
- 15% Application queries (use cases, implementations, real-world examples)
- 15% Comparative queries (vs alternatives, comparisons, trade-offs)
- 15% Critical queries (challenges, limitations, criticisms, debates)
- 10% Data-driven queries (statistics, studies, benchmarks, metrics)
- 10% Future-oriented queries (trends, predictions, roadmaps, opportunities)

QUERY REQUIREMENTS:
- Each query must be specific and answerable
- Cover different aspects mentioned in the overview
- Avoid redundancy with other queries
- Range from beginner to expert level
- Optimized for search engines (natural language)
- 5-25 words per query

OUTPUT FORMAT:
Return a JSON array of objects with this exact structure:
[
  {
    "query": "specific search query text here",
    "category": "foundational|technical|application|comparative|critical|data|future"
  },
  ...
]

Return ONLY the JSON array, no additional text or explanation.
```

**Example Input**:
```json
{
  "topic": "quantum computing for drug discovery",
  "overview_result": "Quantum computing shows promise for drug discovery by simulating molecular interactions...",
  "subtopics": ["molecular simulation", "quantum algorithms", "pharmaceutical applications"],
  "entities": ["IBM", "Google", "Schrödinger Inc"],
  "terminology": ["quantum annealing", "variational quantum eigensolver", "QSAR"],
  "research_angles": ["computational efficiency", "accuracy improvements", "commercial readiness"],
  "num_queries": 100
}
```

**Expected Output**:
```json
[
  {
    "query": "What is quantum computing and how does it differ from classical computing in drug discovery?",
    "category": "foundational"
  },
  {
    "query": "Variational Quantum Eigensolver (VQE) algorithm for molecular simulation explained",
    "category": "technical"
  },
  {
    "query": "Real-world examples of quantum computing accelerating drug discovery at pharmaceutical companies",
    "category": "application"
  },
  ...
]
```

---

## Context Extraction Prompts

### 3.1 Reconnaissance Context Parsing

**Purpose**: Extract structured context from the overview search result.

**Model**: Claude Haiku 4.5

**Template**:
```
Analyze the following research overview and extract key contextual information.

ORIGINAL TOPIC: {topic}

OVERVIEW RESULT:
{overview_result}

TASK:
Extract and structure the following information from the overview:

1. Key Subtopics: 3-7 main areas or dimensions of this topic
2. Key Entities: 5-15 important organizations, people, technologies, or products
3. Terminology: 5-15 important technical terms or jargon
4. Research Angles: 3-7 different perspectives or approaches to study this topic

OUTPUT FORMAT:
Return a JSON object with this exact structure:
{
  "key_subtopics": ["subtopic1", "subtopic2", ...],
  "key_entities": ["entity1", "entity2", ...],
  "terminology": ["term1", "term2", ...],
  "research_angles": ["angle1", "angle2", ...]
}

Requirements:
- Be specific and concrete
- Extract only information explicitly present or strongly implied
- Prioritize the most important/relevant items
- Use concise phrases (2-5 words each)

Return ONLY the JSON object, no additional text.
```

**Expected Output**:
```json
{
  "key_subtopics": [
    "molecular simulation",
    "quantum algorithms",
    "pharmaceutical applications",
    "computational chemistry",
    "protein folding"
  ],
  "key_entities": [
    "IBM Quantum",
    "Google Quantum AI",
    "D-Wave Systems",
    "Schrödinger Inc",
    "Pfizer",
    "variational quantum eigensolver"
  ],
  "terminology": [
    "quantum annealing",
    "NISQ devices",
    "quantum supremacy",
    "qubit coherence",
    "molecular Hamiltonian"
  ],
  "research_angles": [
    "computational efficiency vs classical methods",
    "near-term practical applications",
    "hardware limitations and requirements",
    "accuracy of quantum simulations",
    "commercial viability and ROI"
  ]
}
```

---

## Synthesis Prompts

### 4.1 Final Report Generation

**Purpose**: Generate a comprehensive, high-signal research report from aggregated results.

**Model**: Claude Sonnet 4.5

**Template**:
```
You are an expert research analyst creating an ultra-high-signal report.

RESEARCH TOPIC: {topic}

INITIAL RECONNAISSANCE:
{reconnaissance_summary}

DEEP RESEARCH RESULTS:
You conducted {total_queries} searches across multiple categories. Here are the aggregated findings:

{aggregated_results_by_category}

ALL SOURCES:
{source_list}

TASK:
Create a comprehensive research report that synthesizes these findings into actionable insights.

REPORT STRUCTURE:

# {topic} - Research Report

**Research Date**: {date}
**Queries Executed**: {successful_count} successful, {failed_count} failed
**Total Sources**: {source_count}

## Executive Summary

Write 2-3 paragraphs that:
- Provide a clear overview of the topic
- Highlight the most important findings
- State key conclusions or implications
- Use concrete facts and specific examples

## Key Insights

List 5-10 of the MOST IMPORTANT insights discovered. Each should be:
- Actionable or significant
- Supported by the research
- Concise (1-2 sentences)
- Prioritized by importance

## Detailed Findings

Organize findings into 4-6 logical sections based on the research. For each section:
- Use clear, descriptive headers
- Synthesize information from multiple sources
- Include specific examples, data, or quotes where relevant
- Attribute information to sources naturally (not just listed at end)
- Focus on signal, not noise

## Key Challenges and Limitations

What are the main challenges, limitations, or criticisms identified in the research?

## Future Outlook

What trends, developments, or opportunities were identified?

## Sources

List all sources referenced, grouped by category or relevance.

---

CRITICAL REQUIREMENTS:
- Be concise - remove fluff and redundancy
- Prioritize signal over volume
- Use specific examples and data points
- Make it scannable with clear headers
- Attribute important claims to sources
- Focus on insights, not just information
- Write in clear, professional prose
- No jargon unless necessary (explain when used)

OUTPUT:
Return the complete report in Markdown format.
```

**Expected Output**: A well-structured Markdown report (see example in `examples/sample_report.md`)

---

## Prompt Engineering Best Practices

### General Guidelines

1. **Be Specific**: Clearly state the desired output format
2. **Provide Context**: Include all relevant information from previous steps
3. **Use Examples**: Show the expected structure when possible
4. **Constrain Output**: Request specific formats (JSON, Markdown, etc.)
5. **Prioritize**: Ask for prioritization/ranking when relevant
6. **Validate**: Include requirements for validation

### For Query Generation

- ✅ Request specific distribution across categories
- ✅ Emphasize diversity and avoid redundancy
- ✅ Request JSON for easy parsing
- ✅ Specify word count ranges
- ❌ Don't be vague about what "good queries" means
- ❌ Don't allow free-form unstructured output

### For Synthesis

- ✅ Emphasize conciseness and signal
- ✅ Request specific structure with headers
- ✅ Ask for source attribution
- ✅ Prioritize actionable insights
- ❌ Don't let it ramble or include fluff
- ❌ Don't accept generic summaries

### Error Handling in Prompts

Include fallback instructions:
```
If you cannot generate all {num_queries} queries, generate as many as possible and return what you have.

If you encounter ambiguous information, note the ambiguity in your response.

If the search results are limited or low-quality, acknowledge this in the final report.
```

---

## Prompt Versioning

### Version History

- **v1.0** (Initial): Basic prompts for MVP
- **v1.1** (Planned): Add few-shot examples to query generation
- **v1.2** (Planned): Improve context extraction with chain-of-thought
- **v2.0** (Planned): Dynamic prompt adjustment based on topic type

### Testing New Prompts

When modifying prompts:
1. Test with 3-5 diverse topics
2. Compare outputs with previous version
3. Measure: output quality, consistency, parsing success rate
4. Document changes and rationale

---

## Common Issues and Solutions

### Issue: Query Generation Produces Redundant Queries

**Solution**: 
- Add explicit instruction: "Ensure no two queries are similar"
- Provide examples of redundant vs. diverse queries
- Request self-evaluation: "Review your queries and remove any that are too similar"

### Issue: Synthesis Report Is Too Generic

**Solution**:
- Emphasize specifics: "Include specific names, numbers, and examples"
- Add constraint: "Avoid generic statements like 'there are many approaches'"
- Request: "Every claim should be traceable to a specific source"

### Issue: Context Extraction Misses Important Information

**Solution**:
- Make extraction criteria more explicit
- Add examples of good extractions
- Request: "Prioritize actionable information over general background"

---

## Appendix: Example Outputs

See `examples/` directory for:
- `example_queries.json` - Sample query generation output
- `example_context.json` - Sample context extraction
- `example_report.md` - Sample final report

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-XX
