# Workflow: Architecture from Model Code

1. Read only the model files the user authorizes.
2. Extract modules and connections into an explicit JSON graph; do not execute untrusted model code.
3. Ask about ambiguous branches, tensor shapes, or omitted preprocessing.
4. Generate with `paper-figures generate architecture --data <graph.json>`.
5. Validate the output triplet and visually inspect labels, arrows, and overlaps.

The built-in generator consumes JSON. Model-code interpretation remains a reviewed preparation step, not automatic code execution.
