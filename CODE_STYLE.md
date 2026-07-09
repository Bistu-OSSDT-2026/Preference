# TasteWise Code Style Guide

This guide keeps project contributions consistent and easy to review. It is intentionally lightweight so every team member can follow it during course development.

## Python Style

- Use clear English names for modules, functions, variables, and CSV field names.
- Keep user-facing text in Chinese when it appears in the Streamlit UI.
- Prefer small functions with one responsibility over long blocks inside `app.py`.
- Put reusable recommendation logic in `recommender.py` or `utils/`, not directly in page rendering code.
- Validate input data at the boundary where it enters the system.
- Avoid silently swallowing exceptions. Show a helpful UI message or raise a clear error.

## Streamlit Page Structure

- Keep page configuration, styles, data loading, sidebar controls, recommendation calls, and result rendering in separate sections.
- Put expensive or repeated data loading behind `st.cache_data` when the data is read-only during a page run.
- Do not write recommendation scoring logic inside button handlers. Call `recommend_dishes()` or a helper instead.
- Keep cards, metrics, and feedback buttons consistent across all recommendation result sections.

## Data Rules

- Treat `TasteWise/data/dishes.csv` as the source dataset for dishes.
- Keep CSV column names stable. If a field must be renamed, update the importer, tests, and README in the same PR.
- Do not commit personal runtime data generated during local testing unless the PR is specifically about sample data.
- Keep taste scores in the range `1` to `5`.
- Use UTF-8 for CSV and Markdown files.

## Testing Expectations

- Add or update tests when changing recommendation scoring, data import, or user feedback behavior.
- For UI-only changes, run the app locally and include the checked page or workflow in the PR description.
- Before opening a PR, run the most relevant command:

```powershell
cd TasteWise
python -m pytest tests/test_recommender.py
```

Use the full suite when touching shared data or import code:

```powershell
cd TasteWise
python -m pytest
```

## Pull Request Checklist

Before requesting review, confirm:

- The PR has one clear purpose.
- The branch is based on the latest `master`.
- Generated files, caches, and personal test data are not included.
- The README or docs are updated when behavior changes.
- The PR description lists how the change was tested.
