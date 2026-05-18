## 2024-05-15 - Consolidate independent counts and checks into a single query via scalar_subquery()
**Learning:** Dashboard-style endpoints often run 5-10 separate aggregate/existence queries, leading to unnecessary database round trips.
**Action:** When multiple independent counts and checks are needed for a dashboard, wrap them in `scalar_subquery()` and combine them into a single `select()` execution. This reduces N independent database round trips to 1, significantly improving endpoint response time while keeping application code readable.
