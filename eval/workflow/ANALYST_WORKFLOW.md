# Structured analytical workflow (Condition B)

This document is the only thing added in Condition B beyond the neutral task
prompt. It was written before any evaluation fixture existed and contains no
dataset-specific answers. Follow it in order and write the evidence for each
step into your answer.

## 1. Inspect before computing

1. Read the data dictionary and the manifest. List the fields you will rely on
   for: site identity, sample identity, date, medium, activity type,
   constituent definition, sample fraction, units, detection condition,
   detection or reporting limits, method, and laboratory.
2. Tabulate the distinct values of every categorical field you rely on
   (`validators.tabulate_fields`). Do not assume a field is uniform because the
   query filtered on something related.
3. State which rows are field samples and which are quality-control, blank,
   replicate, or undetermined records. Say what you do with each class.

## 2. Establish comparability

4. For each constituent, group rows by (characteristic name, parameter code,
   sample fraction, unit, method speciation). Decide which groups measure the
   same quantity. Treat different chemical definitions, fractions, and
   speciations as different quantities unless you can show they are equivalent
   in this dataset.
5. Convert units with an explicit factor you write down. Check for rows that
   are the same measurement re-expressed in other units
   (`validators.check_reexpressed_pairs`), and do not count them twice.
6. Check key uniqueness for every table you join or aggregate
   (`validators.check_unique_key`). Report the row count before and after each
   join or filter.

## 3. Account for non-detects and limits

7. Count censored results and tabulate their limits by year and by laboratory
   (`validators.censoring_profile`). If limits changed over time, say how that
   can create or hide an apparent change.
8. Do not substitute zero, the limit, or half the limit as the main method.
   Use interval bounds, a censored estimator, or state that the quantity is not
   identifiable. If you use substitution as a sensitivity check, label it.

## 4. Define the quantity and the unit of analysis

9. Write the target quantity in one sentence (what, where, which period, which
   wells) before computing it.
10. Name the independent unit (usually the well). Repeated samples from one
    well and samples close in time are not independent.
11. Compare the pooled summary with a consistent-cohort summary
    (`validators.cohort_composition`). If the set of wells differs between
    periods, say what that does to the pooled comparison.

## 5. Compute in code, report with uncertainty

12. Every number in the answer must come from code you ran in this session.
    Keep the script in the working directory.
13. Report uncertainty in a form the sampling structure supports (for example,
    well-level resampling or an exact test on per-well directions). Do not
    report precision the data cannot support.
14. State material caveats next to the claim they affect, not in a separate
    section.

## 6. Decide whether to answer

15. If a required piece of metadata is missing or inconsistent so that the
    requested comparison is not defensible, say so explicitly and stop at the
    strongest claim the data support. A justified abstention is a valid answer.

## Answer format

Produce `answer.json` with the fields the task asks for, plus `checks` (a list
of the validator outputs or equivalent evidence you relied on) and `caveats`.
Produce `answer.md` with a short written interpretation.
