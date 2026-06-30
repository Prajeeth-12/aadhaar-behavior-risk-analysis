# The Proactive-Reactive Divide

## Implementation Plan

## Executive Summary
This project measures Aadhaar update behavior to identify proactive and reactive patterns across districts and states. The core output is a Proactive-Reactive Score (PRS) that supports prioritization of outreach, service continuity planning, and risk-focused interventions.

## Project Objectives
- Build a reliable PRS framework using enrollment, demographic update, and biometric update data.
- Classify districts into clear behavioral tiers for decision support.
- Produce visual and tabular outputs suitable for policy and operational review.
- Provide an interactive dashboard for state and district-level exploration.

## Data Scope
- Enrollment data for baseline population and cohort context.
- Demographic update data for low-friction update behavior.
- Biometric update data for high-friction update behavior.
- District and state rollups for comparative analysis.

## Methodology
### PRS Components
1. Time Lag Score
Measures delay between expected and observed update activity by cohort.

2. Behavioral Gap Score
Measures imbalance between demographic and biometric updates to capture friction.

3. Trend Score
Measures change in update behavior over the analysis window.

### Weighted Formula
```
PRS = (0.375 * TimeScore) + (0.4375 * BehaviorScore) + (0.1875 * TrendScore)
```

## Classification Framework
| Category | PRS Range | Interpretation |
| --- | --- | --- |
| Proactive Leaders | 0.00 - 0.30 | Early and consistent update behavior |
| Transition Districts | 0.30 - 0.50 | Mixed behavior with moderate delays |
| Reactive Majority | 0.50 - 0.70 | Delayed, response-driven behavior |
| Crisis-Dependent | 0.70 - 0.90 | Updates mostly under pressure |
| System Failure Zones | > 0.90 | Severe update lag and high risk |

## Execution Plan
### Phase 1: Data Preparation
- Validate schema, null handling, and type consistency.
- Standardize state, district, and pincode identifiers.
- Build clean merged datasets for scoring.

### Phase 2: PRS Computation
- Compute component scores at district and pincode level.
- Apply weighted PRS formula and normalize outputs.
- Generate state-level aggregated summaries.

### Phase 3: Segmentation and Insights
- Apply tier classification for all districts.
- Identify top risk districts and high-priority states.
- Build comparative summaries for leadership review.

### Phase 4: Visualization and Dashboard
- Prepare distribution plots, heatmaps, and ranking views.
- Publish interactive dashboard with filters and drill-down.
- Export presentation-ready charts and summary tables.

### Phase 5: Validation and Documentation
- Run sanity checks and consistency tests.
- Cross-check ranked outputs against source metrics.
- Finalize documentation and submission artifacts.

## Deliverables
- District-level PRS scores and category labels.
- State-level PRS summary and risk ranking.
- Visual outputs for distribution and regional comparison.
- Interactive dashboard for exploration and reporting.
- Final documentation with methodology and findings.

## Quality Checklist
- Data quality checks completed before scoring.
- Formula and weight calculations verified.
- Classification thresholds consistently applied.
- Output files reproducible from the pipeline.
- Dashboard values aligned with exported summaries.

## Implementation Status
- Core analysis pipeline: complete.
- Classification and ranking: complete.
- Dashboard and visual outputs: complete.
- Documentation: updated for clean submission format.

## Next-Step Enhancements
- Add external validation signals where available.
- Add intervention impact tracking by district category.
- Extend monitoring for periodic PRS refresh.
