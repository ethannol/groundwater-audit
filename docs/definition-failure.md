# Same cohort, different weighting, opposite-looking answers

Task T3 requested pooled arsenic summaries, not an additional cohort study.
Both workflow runs volunteered extra analyses of the same shared wells.
The checked reference definition for cohort change uses **the last result per
well per period**; neither volunteered summary answers exactly that question.

| Artifact | Quantity summarized | Weighting | Reported direction |
|---|---|---|---|
| [T3_B_r1 answer](../eval/runs/T3_B_r1/output/answer.md) and [calculation](../eval/runs/T3_B_r1/output/t3b.py) | Within-well period medians, then well directions | Each well contributes once | More wells had lower medians |
| [T3_B_r2 answer](../eval/runs/T3_B_r2/output/answer.md) and [calculation](../eval/runs/T3_B_r2/output/t3c.py) | Pooled observations restricted to shared wells | Frequently sampled wells contribute more observations | The pooled median increased |
| [Frozen T5 definition](../eval/tasks/T5_uncertainty.md) | Last result per well in each period | Each well contributes once, with censored intervals | Small measured shift, conditional on the defined comparison |

These summaries can all compute correctly while suggesting different stories.
“The same cohort” fixes who is included; it does not fix which observation is
used or how the wells are weighted. Before comparing results, name the
observation rule, weighting and non-detect treatment. Numerical agreement with
a reference row count cannot check those definitions.

See the [findings memo](findings_memo.md#what-happened) for the recorded numbers,
interpretive judgement and limitations. This example introduces no new model
runs or revised scientific conclusion.
