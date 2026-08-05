# Step 9 — Global Executable

Package BOUKENSHA as a gem so the `boukensha` command works from anywhere on your machine.

## What this step adds

- `boukensha.gemspec` — declares the gem: name, version, which files to include, and the `bin/boukensha` executable
- `bin/boukensha` — the shebang script that becomes the global command
- `lib/boukensha_loader.rb` — resolves *which step folder* to load from, then boots the REPL
- `lib/boukensha.rb` + `lib/boukensha/` — step 7's lib, bundled as the default

## Install

```bash
cd 09_global_executable
gem build boukensha.gemspec
gem install boukensha-0.9.0.gem
```

After that, `boukensha` is on your `$PATH` and works from any directory.

## Switching steps with BOUKENSHA_PATH

The loader resolves in this order:

| Priority | Source | Example |
|----------|--------|---------|
| 1 | `BOUKENSHA_PATH` env var | `BOUKENSHA_PATH=~/Sites/boukensha/07_the_repl_loop boukensha` |
| 2 | `BOUKENSHA_PATH` in `~/.boukensharc` | `echo "BOUKENSHA_PATH=~/Sites/boukensha/07_the_repl_loop" > ~/.boukensharc` |
| 3 | Bare path in `~/.boukensharc` (legacy) | `echo ~/Sites/boukensha/07_the_repl_loop > ~/.boukensharc` |
| 4 | Bundled default | just run `boukensha` |

`BOUKENSHA_PATH` must point to a step folder that contains `lib/boukensha.rb`.

## Config directory with BOUKENSHA_DIR

The config directory (settings.yaml, .env, prompts/) resolves in this order:

| Priority | Source | Example |
|----------|--------|---------|
| 1 | `BOUKENSHA_DIR` env var | `BOUKENSHA_DIR=~/projects/mybot/.boukensha boukensha` |
| 2 | `BOUKENSHA_DIR` in `~/.boukensharc` | see below |
| 3 | `~/.boukensha` (default) | just run `boukensha` |

## ~/.boukensharc format

The file supports key=value lines (one per line). Lines starting with `#` are comments.

```
# Point to a specific step:
BOUKENSHA_PATH=~/Sites/boukensha/07_the_repl_loop

# Custom config directory:
BOUKENSHA_DIR=~/projects/mybot/.boukensha
```

A bare path (no `KEY=`) is treated as `BOUKENSHA_PATH` for backwards compatibility:

```
~/Sites/boukensha/07_the_repl_loop
```

## Running a specific step

```bash
# step 7 (interactive REPL)
BOUKENSHA_PATH=~/Sites/boukensha/07_the_repl_loop boukensha

# step 6 doesn't have a REPL — loader tells you how to run it
BOUKENSHA_PATH=~/Sites/boukensha/06_the_run_dsl boukensha
# => boukensha: the step at .../06_the_run_dsl does not support the interactive REPL
#    Run its examples directly, e.g.: ruby .../06_the_run_dsl/examples/*.rb
```

## Debug mode

```bash
BOUKENSHA_DEBUG=1 boukensha
# => [boukensha] loading from: /path/to/step
```

## The key idea

The gem is just a **wrapper and a default**. All the teaching material stays in the numbered step folders exactly as it was. The gem doesn't copy or symlink anything — it just knows where to look.
