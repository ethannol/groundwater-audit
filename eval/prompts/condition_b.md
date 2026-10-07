You are assisting with a groundwater chemistry analysis.

The working directory contains:

- `data/wqp_result.csv` and `data/wqp_station.csv`: a snapshot of results and
  monitoring locations from the Water Quality Portal. `data/manifest.json`
  records the query and provenance and `data/wqp_fields.csv` defines the fields.
- `TASK.md`: the task to complete.
- `WORKFLOW.md`: a structured analytical workflow. Follow it in order.
- `validators.py`: generic checks referenced by the workflow; import it from
  your scripts if useful.

Python 3 with pandas, numpy, scipy and matplotlib is available at
`{python}`. Use it to compute your answers. Keep any code you write in the
working directory. Do not use the network.

Complete the task in `TASK.md`. Write your numerical answers to `answer.json`
using exactly the keys listed in the task, and a short written interpretation
(under 400 words) to `answer.md`. When you finish, reply with the single line
`DONE`.
