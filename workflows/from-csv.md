# Workflow: Figure from CSV

1. Read the CSV header, row count, missing-value count, and numeric ranges. Do not modify the source.
2. Map the requested message to one supported figure type and confirm ambiguous columns or units.
3. Run the matching `paper-figures generate` command with explicit column options.
4. Run `paper-figures check <output-dir> --strict` with the same style config.
5. Inspect the PNG visually and report the exact source path and output files.

Never invent missing measurements or commit the user's dataset to this repository.
