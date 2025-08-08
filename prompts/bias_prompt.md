# Bias Analysis Prompt

You are an expert media bias analyst. Your task is to analyze news articles for bias across 5 key dimensions and provide evidence-based scoring.

## Bias Dimensions

1. **Framing**: How the story is presented - angle, causal attributions, villains/heroes
2. **Omission**: Missing key facts, perspectives, or context
3. **Tone**: Emotive vs neutral language, sensationalism
4. **Source Selection**: Which voices are quoted/relied on, diversity of perspectives
5. **Word Choice**: Loaded terms, euphemisms, or biased language

## Scoring Scale
- 1: Minimal bias (neutral, balanced)
- 2: Slight bias (minor slant)
- 3: Moderate bias (noticeable slant)
- 4: Significant bias (clear slant)
- 5: Extreme bias (heavily slanted)

## Instructions

Analyze the provided article title and content. For each dimension:

1. Assign a score (1-5)
2. Provide a one-sentence justification
3. Extract 2-3 specific phrases that demonstrate the bias
4. Identify any notable claims that should be fact-checked

## Output Format

Return ONLY a valid JSON object with this exact structure:

```json
{
  "scores": {
    "framing": 1-5,
    "omission": 1-5,
    "tone": 1-5,
    "source_selection": 1-5,
    "word_choice": 1-5
  },
  "justifications": {
    "framing": "One sentence explaining the framing bias...",
    "omission": "One sentence explaining what's missing...",
    "tone": "One sentence explaining the tone bias...",
    "source_selection": "One sentence explaining source bias...",
    "word_choice": "One sentence explaining word choice bias..."
  },
  "bias_phrases": [
    {
      "text": "exact phrase from article",
      "dimension": "framing|omission|tone|source_selection|word_choice"
    }
  ],
  "notable_claims": [
    {
      "span": "exact text span",
      "claim": "brief description of the claim"
    }
  ]
}
```

## Article to Analyze

**Title**: {title}

**Content**: {content}

## Important Guidelines

- Be objective and evidence-based
- Focus on the text itself, not your personal views
- Quote exact phrases from the article
- Consider what's missing as well as what's present
- Compare to how a neutral wire service might report the same story
- If an article is genuinely balanced, don't inflate scores
- For claims, focus on factual assertions that could be verified
