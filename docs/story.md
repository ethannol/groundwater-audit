I wanted to know whether two groundwater contaminants had gone down at the same wells over two decades, in a way I could defend to someone who runs a monitoring programme. The data were public United States Geological Survey records for wells in San Bernardino County, California, pulled from the Water Quality Portal for 2000 to 2023. The constituents were dissolved arsenic and dissolved nitrate, one sparsely resampled and one densely.

A second question sat on top of the first, and it was the reason for the project. I wanted to find out where a language model helps produce a defensible answer to a question like this and where it introduces plausible errors that survive casual review. So I built a reference analysis I had checked by hand, then gave the same data and a set of fixed tasks to a model under two prompting conditions and scored its answers against that reference.

## Finding out what one row means

Before any statistics, I needed to know what one row of the snapshot was. The portal returned a little over thirteen thousand rows. A row is one laboratory result for one sampling activity at one site, with fields for the medium sampled, the chemical definition and unit, and whether the value is a detection or a non-detect, a result reported only as being below the laboratory's reporting limit.

Those fields hid four traps, each logged in an exclusion log. First, a sizeable block of rows were leachate, soil moisture and elutriate samples collected at well sites; they are not groundwater. Second, every nitrate sample appeared twice, once as nitrate as N (the mass of nitrogen in the nitrate) and once as the mass of the whole nitrate ion. The second set is a re-expression of the first, so I dropped it rather than converting it and counting each sample twice.

Third, nitrate-plus-nitrite is a different chemical definition stored under its own name; it equals plain nitrate in most paired samples here, but that is a finding, not an assumption, so I kept it out of the trend question. Fourth, the arsenic reporting limits changed over the record; more on that below. After the filters, the analysis table held {{arsenic.coverage.rows}} routine arsenic results from {{arsenic.coverage.wells}} wells and {{nitrate_as_n.coverage.rows}} nitrate results from {{nitrate_as_n.coverage.wells}} wells.

![Routine groundwater samples per year for arsenic and nitrate, detected and non-detect, with the early period shaded.](reports/figures/fig1_coverage.png)

The coverage figure shows why the question could not be answered by comparing years. Most wells were sampled only once, {{arsenic.coverage.samples_per_well.1}} of the arsenic wells and {{nitrate_as_n.coverage.samples_per_well.1}} of the nitrate wells. Whatever comparison I made would have to say which wells it was about.

## Deciding what would count as a decline before computing it

After profiling the record but before computing any period summary, I wrote down in the decisions log what would count as a decline, because I knew the choice of comparison would otherwise drift toward whatever looked interesting. The periods were fixed as 2000 to 2011 and 2012 to 2023, split where the arsenic reporting limit dropped to its final value and the USGS laboratory became the only analyst.

The target quantity was the change at the same well between the last routine sample of each period, over wells sampled in both periods. That makes the well the unit of analysis, the thing that counts as one independent observation. Non-detects would be carried as censored values, intervals from zero to the limit, and a change would be called only when the two intervals do not overlap. Medians would be Kaplan-Meier estimates, which use the limits without replacing them with a number, and uncertainty would come from a sign test, a well-level bootstrap and a Wilcoxon signed-rank test.

## The pooled comparison and why I did not trust it

The obvious first comparison is the pooled one, the median of all early samples against the median of all late samples. I expected this to mislead, because my hypothesis going in was that a pooled comparison reflects changes in which wells were sampled rather than change at wells. I computed it anyway, beside the cohort version.

![Kaplan-Meier period medians for all samples, for one sample per well, and for the consistent cohort, arsenic and nitrate.](reports/figures/fig4_pooled_vs_cohort.png)

The pooled medians moved in opposite directions for the two constituents. Nitrate falls from {{nitrate_as_n.pooled_vs_cohort.pooled_early.km_median:.2f}} to {{nitrate_as_n.pooled_vs_cohort.pooled_late.km_median:.2f}} mg/L as N, and arsenic rises from {{arsenic.pooled_vs_cohort.pooled_early.km_median:.2f}} to {{arsenic.pooled_vs_cohort.pooled_late.km_median:.2f}} µg/L. That was the first sign that the pooled comparison was answering a different question from the one I had asked. Of the wells in the arsenic record, {{arsenic.pooled_vs_cohort.wells_only_early}} were sampled only in the early period and {{arsenic.pooled_vs_cohort.wells_only_late}} only in the late period; for nitrate the counts are {{nitrate_as_n.pooled_vs_cohort.wells_only_early}} and {{nitrate_as_n.pooled_vs_cohort.wells_only_late}}. The late period simply sampled more high-arsenic wells and more low-nitrate wells.

The cohort bars in the same figure barely move. Among the {{arsenic.pooled_vs_cohort.cohort_wells}} arsenic wells sampled in both periods the median goes from {{arsenic.pooled_vs_cohort.cohort_early.km_median:.2f}} to {{arsenic.pooled_vs_cohort.cohort_late.km_median:.2f}} µg/L, and among the {{nitrate_as_n.pooled_vs_cohort.cohort_wells}} nitrate cohort wells from {{nitrate_as_n.pooled_vs_cohort.cohort_early.km_median:.2f}} to {{nitrate_as_n.pooled_vs_cohort.cohort_late.km_median:.2f}} mg/L. That settled the composition question and left the real one, what happened at those cohort wells.

## How I treated non-detects

The fourth trap bites hardest in the arsenic cohort. {{arsenic.coverage.censored}} arsenic results, {{arsenic.coverage.censored_share:.1%}} of the record, are non-detects, and their reporting limits are not constant.

![Reporting limits of non-detects by year and laboratory, arsenic and nitrate, on a log scale.](reports/figures/fig2_limits.png)

The arsenic panel shows a laboratory change as a step in the limits. In the first year of the record the highest limit was {{arsenic.limits_by_year.0.max}} µg/L; in the last year with non-detects the median limit was {{arsenic.limits_by_year.-1.median}} µg/L, and the laboratory doing the analyses had changed twice in between. An early non-detect at the old limit and a late detection just under it are the same water measured two ways. Substituting half the limit, as is common, would have turned every such pair into a decline by construction.

So no value was substituted in the main analysis. A non-detect is an interval, a pair is determinate only when the intervals do not overlap, and the medians are Kaplan-Meier. Substitution at zero, half the limit and the full limit was run only as a labelled sensitivity check, and the shares of declining wells it gives sit close to the interval-based answer without matching it.

## The cohort comparison

With the rules fixed I paired each cohort well's last early sample with its last late sample.

![Each cohort well's last late-period result against its last early-period result, with declines, increases and indeterminate pairs marked.](reports/figures/fig3_cohort_pairs.png)

Nitrate scatters around the diagonal. Of the {{nitrate_as_n.paired_change.n_pairs}} cohort wells, {{nitrate_as_n.paired_change.decline}} declined, {{nitrate_as_n.paired_change.increase}} increased and {{nitrate_as_n.paired_change.indeterminate}} are indeterminate because of a non-detect. The sign test, which asks whether that split could be chance, gives a two-sided p of {{nitrate_as_n.paired_change.sign_test.p_two_sided:.2f}}, and the median late-over-early ratio among the {{nitrate_as_n.paired_change.both_detected}} pairs with both values detected is {{nitrate_as_n.paired_change.wilcoxon_both_detected.median_ratio_late_over_early:.2f}}. The data do not support a decline in nitrate at repeatedly sampled wells. That answered the nitrate half of the question.

Arsenic leans slightly below the diagonal. Of {{arsenic.paired_change.n_pairs}} cohort wells, {{arsenic.paired_change.decline}} declined, {{arsenic.paired_change.increase}} increased and {{arsenic.paired_change.indeterminate}} are indeterminate. Among the {{arsenic.paired_change.sign_test.determinate}} determinate wells the share declining is {{arsenic.paired_change.sign_test.share_declining:.2f}}, with an exact binomial interval of {{arsenic.paired_change.sign_test.ci95_share_declining.0:.2f}} to {{arsenic.paired_change.sign_test.ci95_share_declining.1:.2f}} and a sign test p of {{arsenic.paired_change.sign_test.p_two_sided:.3f}}. Among the {{arsenic.paired_change.both_detected}} wells with both values detected, the median ratio is {{arsenic.paired_change.wilcoxon_both_detected.median_ratio_late_over_early:.3f}} and the Wilcoxon signed-rank test, which also uses the sizes of the differences, gives p = {{arsenic.paired_change.wilcoxon_both_detected.p_two_sided:.3f}}. That raised the question I had been expecting since the limits figure, whether a statistically detectable shift this small is a decline at all.

## Why a significant sign test is still not a decline

A small p-value says the direction of change is not balanced. It does not say the change is bigger than the measurement can resolve, or that it comes from the water rather than the laboratory.

The first is replicate precision. The {{arsenic.replicate_precision.pairs}} arsenic field replicates I could match to a routine sample have a median relative percent difference of {{arsenic.replicate_precision.median_rpd_pct:.0f}} percent, and a median within-well ratio of {{arsenic.paired_change.wilcoxon_both_detected.median_ratio_late_over_early:.3f}} is a change of about three percent, well inside that. The second is the laboratory change at the period boundary; a method shift of a few percent would produce the same picture. The third is the {{arsenic.paired_change.indeterminate}} indeterminate wells, typically an early non-detect at the old limit overlapping the late result, which the sign test cannot use. The well-level bootstrap of {{arsenic.paired_change.bootstrap_wells.n_boot}} resamples puts the share declining at {{arsenic.paired_change.bootstrap_wells.share_declining_all_pairs:.2f}}, with an interval of {{arsenic.paired_change.bootstrap_wells.share_declining_ci95.0:.2f}} to {{arsenic.paired_change.bootstrap_wells.share_declining_ci95.1:.2f}} that includes one half.

Measured arsenic at the cohort wells was, on average, slightly lower in the late period, by an amount comparable to measurement variability, coincident with a change of laboratory and reporting limit, and with no evidence of a widespread decline. The cohort is also the set of wells the agencies chose to resample, not a random sample of the county.

## Why I then ran a language model on the same data

Every step of the reference answer had turned on a definition rather than a calculation. The question for the second half was whether a model, given the same snapshot and a bounded task, would reach the same numbers, and whether a structured analytical workflow would make it more reliable than a neutral prompt. My hypothesis was that the workflow would reduce errors.

I fixed what the model would see before any run. Six frozen tasks, each with its wording, data and reference answer settled in advance, covered the chain above, from a data profile through the comparable-unit, censoring, cohort and uncertainty steps to a decision memo on a synthetic basin with a known truth and planted issues. Condition A was a neutral prompt that named the files and asked for the task. Condition B added a structured workflow (inspect before computing, establish comparability, treat non-detects as censored, name the unit of analysis, compute in code, report uncertainty) and generic validators; both were written before the fixtures existed and contain no dataset-specific numbers. A pilot run exposed an ambiguity in the first task's wording, fixed before the matrix started; the pilot is recorded and excluded.

Each task ran under each condition twice, which makes {{evaluation.runs}} runs of one Sonnet-series Claude model, its exact identifier pinned and recorded per run. Each run worked alone in a temporary directory holding only the snapshot, its manifest, the field dictionary, the task and, under Condition B, the workflow, with no network tools and a fixed money and wall-clock budget.

## How I scored the answers

Each answer was a JSON file of named keys plus a short interpretation. Mechanical scoring compared the numeric keys against the reference with a script, no judgement involved, and each check carried a severity. A critical check is one where the trap would show, such as the nitrate row count that doubles if the re-expressed rows are kept; a major check is a reporting error that would mislead a reader of the JSON alone.

I also read every interpretation against a written rubric, a list of what a correct answer had to say about definitions, units and uncertainty, and gave each run a verdict of correct or correct with gaps. The scorer was not frozen. After seeing runs I corrected it four times, for two ambiguous task wordings, one miscalibrated severity and one keyword match that credited a run for the word "duplicate" when it had not found the duplicated row. Every correction is logged and was applied to both conditions.

## What the model got right

The model produced correct numbers under both conditions. Across the {{evaluation.runs}} runs, {{evaluation.passed}} of {{evaluation.checks}} mechanical checks passed and there were {{evaluation.critical_failures}} critical failures, for a total cost of {{evaluation.total_cost_usd:money}}. Every run excluded the non-groundwater media, dropped rather than converted the re-expressed nitrate rows, treated non-detects as intervals or bounded the median, named the well as the independent unit, and said that the pooled nitrate comparison reflected which wells were sampled. All four runs of the synthetic decision memo declined to support the decline the water agency wanted and found the planted limit change, composition change and missing units.

What did not happen was the thing I had expected. The structured workflow cost {{evaluation.workflow_cost_uplift_pct:.0f}} percent more and did not reduce errors; both major failures and all but one of the interpretive gaps were in Condition B. The neutral prompt already did the things the workflow prescribes, which is a statement about this model's defaults on a precisely specified task, not about workflows in general.

## The definitional failures and how they were caught

The failures were definitional, right numbers computed or reported for the wrong definition. One run dropped the re-expressed nitrate rows correctly, reported the right row count and drop count, and then listed the dropped code among the codes it had included. One run of the synthetic memo never found the duplicated station row, because its validators checked the result table's keys but not the station table it was about to join.

The clearest case came from the censored arsenic summary, which asked only for pooled period summaries. Both Condition B runs volunteered an extra cohort analysis on the same shared wells. One reported that per-well medians fell at most of those wells, with a very small p-value; the other reported that the pooled median within the same wells rose. Both numbers reproduce from the data. They point in opposite directions because one weights each well once and the other weights by how often each well was sampled, and neither run said so in a way a reader could compare. "The same cohort" fixes who is included; it does not fix which observation is used or how the wells are weighted.

The reference row counts caught none of this, because the counts were right. The failures were caught by reading the answers against the reference definitions and re-running the volunteered calculations. Mechanical scoring passed the inconsistent code list and, until the keyword correction, the missed duplicate. The scoring harness itself needed four logged corrections, so the harness made more mistakes than the model did.

## A corrected scorer, published separately

The keyword correction made me doubt the rest of the mechanical layer, so after the evaluation was published I wrote a stricter scorer version. It validates the shape of each answer, requires a named censored-median method and a sensitivity statement, and searches an explicit issue inventory rather than free notes. It re-scores the recorded answers without new model calls. Review of its output caught a false negative of its own, fixed in a further revision.

Under the corrected scorer, {{v2.passed}} of {{v2.checks}} mechanical checks pass, with {{v2.major}} major and {{v2.critical}} critical failures, against {{evaluation.passed}} of {{evaluation.checks}} under the original scoring. This re-score is exploratory. I decided to do it after seeing the primary result, and I report it as such; the original published scores remain the baseline.

## What the evaluation does not show

No human time was measured. The reference analysis is a correctness reference, not a productivity baseline, and no analyst session was timed; a protocol for doing so is in the repository and has not been run. Two repetitions per cell show consistency, not superiority. The cohort and uncertainty tasks spelled out the cohort rule, the period boundaries and the interval rule, so they measure execution of a stated method more than choice of method.

## What I concluded

Nitrate did not decline at repeatedly sampled wells, and the lower pooled median is a change in which wells were sampled. Arsenic is slightly lower on average at the cohort wells, by an amount within replicate precision and coincident with a laboratory and reporting-limit change, which is not evidence of a widespread decline. The model reproduced the checked numbers under both prompting conditions, the structured workflow raised cost without reducing errors, and the residual errors were definitional and were found by reading, not by counting.

## What I would not claim

I would not claim a remediation effect, an aquifer-wide improvement or a health conclusion. I would not claim that the model saves analyst time, because no time was measured. I would not claim that either prompting condition is better in general, or that the model would handle a less specified task as well as it handled these.

## What I would do with another week

I would run the human-time protocol with one or two analysts on the same six tasks, so that the cost comparison has a denominator. I would add measurement noise to the synthetic fixture, whose cohort wells have identical early and late values by construction. And I would write a less prescriptive version of the cohort and uncertainty tasks, where the model has to choose the comparison rule itself, because that is where I would expect the definitional failures to multiply.
