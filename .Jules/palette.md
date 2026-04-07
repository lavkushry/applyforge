## 2024-04-07 - Missing htmlFor attributes on labels
**Learning:** Found widespread issue where form labels in components/forms/ lack the htmlFor attribute and associated input ids, reducing accessibility for screen reader users and preventing users from clicking labels to focus inputs.
**Action:** Always map form labels to inputs using htmlFor and id.
