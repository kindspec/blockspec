# SPDX-License-Identifier: Apache-2.0 OR MIT
# blockspec task runner

set dotenv-load := false

# Default: show available recipes
default:
    @just --list

# Install dependencies and set up environment
setup:
    uv sync

# Format code (mutates working tree — use locally)
fmt:
    uv run ruff format .

# Verify formatting (non-mutating — use in CI)
fmt-check:
    uv run ruff format --check .

# Run linters
lint:
    uv run ruff check .

# Format + lint (non-mutating — safe for CI)
check: fmt-check lint

# Everything under tests/: the tree against the reference, the runner's
# no-verdict exit, the reference/ import boundary, the kindkit pins, and the
# gate's own checks. Not the gate's verdict: that is `just mutants`.
test:
    uv run --exact pytest -q

# The conformance tree against the reference implementation
conform:
    uv run python conformance/run_cases.py --impl reference/blockspec/document.py

# The tree itself, with no implementation: the floor, that every case can
# fail, and that every refusal has a control
tree:
    python3 conformance/check_tree.py

# The mutation gate: the tree must be able to FAIL a broken implementation.
# Exit 1 names each surviving mutant, which is a hole in the suite.
mutants:
    uv run python conformance/mutants.py

# Remove build artifacts
clean:
    rm -rf .pytest_cache .ruff_cache **/__pycache__
