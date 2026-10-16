# SPDX-License-Identifier: Apache-2.0 OR MIT
"""The gate's own checks: a mutation that did not land is never a kill.

The gate itself (`just mutants`) is not run here. Its verdict is the suite's
holes, which are the case author's to close, and `just test` must not go red
on them. What is tested here is that the gate cannot report a kill for a
mutation that changed nothing.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "conformance"))

import mutants  # noqa: E402


def _source():
    with open(mutants.IMPL, encoding="utf-8", newline="") as handle:
        return handle.read()


def test_every_mutant_changes_the_source_and_no_two_are_the_same():
    assert mutants.preflight(_source()) == []


def test_a_splice_that_returns_the_source_unchanged_is_broken(monkeypatch):
    """kindkit refuses a literal no-op (`old == new`) itself, as STALE. The
    hash catches the other way a mutation can fail to land: a splice that
    hands back the source untouched."""
    monkeypatch.setattr(mutants, "apply_mutant", lambda source, old, new: source)
    table = {"lands-nowhere": ("        if _CONFLICT.match(line):", "        if False:")}
    problems = mutants.preflight(_source(), table)
    assert problems == ["BROKEN   lands-nowhere: the mutated source is the unmutated source"], (
        problems
    )


def test_two_spellings_of_one_mutation_are_broken():
    table = {
        "first": ("        if _CONFLICT.match(line):", "        if False:"),
        "second": ("if _CONFLICT.match(line):", "if False:"),
    }
    problems = mutants.preflight(_source(), table)
    assert problems == ["BROKEN   second: the same mutated source as first"], problems


def test_the_probe_reads_the_unmutated_source_after_the_baseline_as_no_verdict(tmp_path):
    source = _source()
    path = tmp_path / "under_test.py"
    path.write_text(source, encoding="utf-8")
    probe = mutants.make_probe(mutants._sha(source))
    baseline = probe(str(path))
    assert baseline.reached and not baseline.failures
    assert not probe(str(path)).reached


def test_a_mutated_reader_can_reach_the_anchor_resolver():
    """The reader's `resolve` loads `anchor.py` from its own directory, so the
    gate's mutated copy has to sit beside it, or every anchor case would fail
    against the unmutated baseline."""
    assert os.path.dirname(mutants.SCRATCH) == os.path.dirname(mutants.IMPL)
    assert os.path.isfile(os.path.join(os.path.dirname(mutants.SCRATCH), "anchor.py"))
