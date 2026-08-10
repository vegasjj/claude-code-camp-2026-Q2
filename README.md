# Claude Code Camp

This is my project for the Claude Code Camp operated by [ExamPro](https://www.exampro.co)

## Summary

- **[`.boukensha/`](./.boukensha)**: Harness runtime workspace, settings, and session telemetry logs.
  - **[`.boukensha/prompts/`](./.boukensha/prompts)**: System prompt templates tailored for agent tasks.
  - **[`.boukensha/sessions/`](./.boukensha/sessions)**: Recorded JSONL execution logs for agent sessions.
  - **[`.boukensha/settings.yaml`](./.boukensha/settings.yaml)**: Configuration file defining provider defaults and task settings.
- **[`docs/`](./docs)**: Technical documentation, architectural plans, and session journals.
  - **[`docs/journal/`](./docs/journal)**: Journal entries detailing technical goals, hypotheses, and observations (`0_preweek.md`, `1_baseline.md`).
  - **[`docs/plans/`](./docs/plans)**: Feature implementation plans and technical proposal documents.
  - **[`docs/src/`](./docs/src)**: Documentation assets, screenshots, and visual diagrams.
- **[`week0_explore/`](./week0_explore)**: Early exploration phase for MUD connectivity, parsers, and architecture spikes.
  - **[`week0_explore/bin/`](./week0_explore/bin)**: Executable scripts for early MUD interaction testing.
  - **[`week0_explore/circlemud-world-parser/`](./week0_explore/circlemud-world-parser)**: Utilities for parsing CircleMUD/tbaMUD world data files.
  - **[`week0_explore/explore_architecture/`](./week0_explore/explore_architecture)**: Experimental spikes testing various agent harness patterns.
  - **[`week0_explore/infrastructure/`](./week0_explore/infrastructure)**: Infrastructure and server container configurations for running the MUD.
  - **[`week0_explore/mud_manager/`](./week0_explore/mud_manager)**: Ruby gem providing low-level socket connections and game commands.
  - **[`week0_explore/preview/`](./week0_explore/preview)**: Visual previews and interface mockups for game session monitoring.
  - **[`week0_explore/CHALLENGES.md`](./week0_explore/CHALLENGES.md)**: Documented technical challenges in automating MUD gameplay.
  - **[`week0_explore/HOW_TO_PLAY.md`](./week0_explore/HOW_TO_PLAY.md)**: Guide covering manual and programmatic commands for tbaMUD.
- **[`week1_baseline/`](./week1_baseline)**: Baseline agent harness (Boukensha) implemented step-by-step across 12 modules.
  - **[`week1_baseline/bin/`](./week1_baseline/bin)**: Step-by-step test binaries (`00_config` through `12_context`).
  - **[`week1_baseline/log_viz/`](./week1_baseline/log_viz)**: Web-based telemetry and log visualizer for session inspection.
  - **[`week1_baseline/python/`](./week1_baseline/python)**: Python implementation of the baseline agent framework (Pending).
  - **[`week1_baseline/ruby/`](./week1_baseline/ruby)**: Ruby implementation of the Boukensha harness, backends, and standard tools.
- **[`week2_capable/`](./week2_capable)**: Capable agent iterations, long-term memory integration, and advanced loops.
