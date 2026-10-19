# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Unit tests of the reference anchor resolver, `reference/blockspec/anchor.py`.

These are the implementation's own tests, not conformance cases: SPEC.md
section 11's cases come from an author who has not read the resolver, into
`conformance/cases/` as the `anchor` kind. Each expectation here is argued
from SPEC.md section 11, which each test names.
"""

import hashlib
import unicodedata

import pytest
from blockspec import anchor as A
from blockspec import document

R = "doc.md.notes/01J9Z3M8Q4X7V2K6T0R5N1B8CD.md"
R2 = "doc.md.notes/01J9Z3M8Q4X7V2K6T0R5N1B8CE.md"

# Paragraphs that share little with each other, so that only the ones a test
# means to be similar are.
ALPHA = "Alpha paragraph about the reactor housing."
BRAVO = "Bravo paragraph on coolant flow limits."
CHARLIE = "Charlie paragraph regarding operator training."
SCRAM = "The scram threshold is 4.2 sigma above baseline, measured over a rolling window."
DIGITS = "0123456789" * 4


def oid(text, fmt="sha1"):
    data = text.encode("utf-8")
    return getattr(hashlib, fmt)(b"blob %d\0" % len(data) + data).hexdigest()


def doc(*paragraphs):
    return "\n\n".join(paragraphs) + "\n"


def make_anchor(base, leaf_text, span, *, kind="p", nth=0, at=None, replace=None, fmt="sha1"):
    text = unicodedata.normalize("NFC", leaf_text)
    start = text.index(span) if at is None else at
    end = start + len(span)
    return A.Anchor(
        oid(base, fmt),
        kind,
        nth,
        text,
        span,
        text[max(0, start - A.CONTEXT) : start],
        text[end : end + A.CONTEXT],
        replace,
    )


def record(anchor, status="open"):
    kind = "comment" if anchor.replace is None else "suggestion"
    return (
        f"---\nanchor: {A.write_anchor(anchor)}\nkind: {kind}\nstatus: {status}\n---\n\nA note.\n"
    )


def run(tree, blobs=(), records=(R,), transclusions=(), fmt="sha1"):
    repo = {
        "object_format": fmt,
        "tree": dict(tree),
        "blobs": {oid(t, fmt): t for t in [*tree.values(), *blobs]},
    }
    return A.resolve(repo, {"records": list(records), "transclusions": list(transclusions)})


def resolve_one(base, current, leaf_text, span, *, status="open", **kw):
    """One record made against `base`, resolved against `current`."""
    anchor = make_anchor(base, leaf_text, span, **kw)
    got = run({"doc.md": current, R: record(anchor, status)}, blobs=[base])
    return got["records"][R]


# --- canonical form (section 11.1, 0003 addendum detail 1) ------------------


def test_canonical_strings_escape_exactly_the_listed_code_points():
    raw = 'a"b\\c\nd\te\x7f\x85\u2028\u2029\ufeff\ufffe\uffff/é\U0001f600'
    assert A.canonical_string(raw) == (
        '"a\\"b\\\\c\\nd\\u0009e\\u007f\\u0085\\u2028\\u2029\\ufeff\\ufffe\\uffff/é\U0001f600"'
    )


def test_an_anchor_round_trips_through_its_canonical_form():
    anchor = make_anchor(doc(SCRAM), SCRAM, "4.2 sigma", replace="5 sigma")
    line = A.write_anchor(anchor)
    assert line.startswith('{"base": "')
    assert ', "leaf": {"type": "p", "nth": 0, "text": "The scram' in line
    assert line.endswith(', "replace": "5 sigma"}')
    assert A.read_anchor(line, "sha1") == anchor


@pytest.mark.parametrize(
    "change",
    [
        lambda s: s.replace('": ', '":'),  # other spacing
        lambda s: s.replace(", ", ","),
        lambda s: s.replace('{"base"', '{ "base"'),
        lambda s: s.replace('"span": "4.2 sigma", "prefix"', '"prefix"', 1).replace(
            '"suffix"', '"span": "4.2 sigma", "suffix"'
        ),  # key order
        lambda s: s.replace('"nth": 0', '"nth": 0, "nth": 0'),  # a duplicate key
        lambda s: s.replace('"base"', "base"),  # an unquoted key
        lambda s: s.replace('"nth": 0', '"nth": 00'),
        lambda s: s.replace('"nth": 0', '"nth": -0'),
        lambda s: s.replace('"nth": 0', '"nth": 0.0'),
        lambda s: s.replace('"nth": 0', '"nth": 0e0'),
        lambda s: s.replace('"nth": 0', '"nth": "0"'),
        lambda s: s.replace('"nth": 0', '"nth": false'),
        lambda s: s.replace('"type": "p"', '"type": "h7"'),
        lambda s: s.replace('"type": "p"', '"type": "paragraph"'),
        lambda s: s.replace("4.2 sigma", "4.2\\u0020sigma", 1),  # an escape not in the set
        lambda s: s.replace("The scram", "The\\/scram", 1),
        lambda s: s + " ",
        lambda s: " " + s,
    ],
)
def test_an_anchor_written_any_other_way_is_not_read(change):
    line = A.write_anchor(make_anchor(doc(SCRAM), SCRAM, "4.2 sigma"))
    assert A.read_anchor(line, "sha1") is not None
    assert A.read_anchor(change(line), "sha1") is None


def test_base_is_lower_case_hex_of_the_object_formats_length():
    anchor = make_anchor(doc(SCRAM), SCRAM, "4.2 sigma")
    line = A.write_anchor(anchor)
    assert A.read_anchor(line.replace(anchor.base, anchor.base.upper()), "sha1") is None
    assert A.read_anchor(line, "sha256") is None
    sha256 = make_anchor(doc(SCRAM), SCRAM, "4.2 sigma", fmt="sha256")
    assert len(sha256.base) == 64
    assert A.read_anchor(A.write_anchor(sha256), "sha256") == sha256
    assert A.read_anchor(A.write_anchor(sha256), "sha1") is None


def test_a_u_escape_is_lower_case_and_an_astral_character_is_written_as_itself():
    anchor = make_anchor(doc("A\ttab and \U0001f600 here."), "A\ttab and \U0001f600 here.", "tab")
    line = A.write_anchor(anchor)
    assert "\\u0009" in line and "\U0001f600" in line
    assert A.read_anchor(line.replace("\\u0009", "\\u0009".upper()), "sha1") is None
    assert A.read_anchor(line.replace("\U0001f600", "\\ud83d\\ude00"), "sha1") is None


def lines_of(anchor, kind="comment", status="open"):
    return [f"anchor: {A.write_anchor(anchor)}", f"kind: {kind}", f"status: {status}"]


def test_the_record_grammar_is_exactly_its_lines():
    comment = make_anchor(doc(SCRAM), SCRAM, "4.2 sigma")
    suggestion = make_anchor(doc(SCRAM), SCRAM, "4.2 sigma", replace="5")
    assert A.read_record(lines_of(comment), "sha1").kind == "comment"
    assert A.read_record(lines_of(suggestion, "suggestion"), "sha1").kind == "suggestion"
    for status in A.STATUSES:
        assert A.read_record(lines_of(comment, status=status), "sha1").status == status
    broken = [
        None,  # no frontmatter
        lines_of(comment)[:2],
        [*lines_of(comment), "author: me"],
        [lines_of(comment)[1], lines_of(comment)[0], lines_of(comment)[2]],
        lines_of(comment, status="closed"),
        lines_of(comment, kind="note"),
        [lines_of(comment)[0], "kind: comment ", lines_of(comment)[2]],
        [lines_of(comment)[0], "kind:  comment", lines_of(comment)[2]],
        lines_of(comment, kind="suggestion"),  # a suggestion with no replace
        lines_of(suggestion, kind="comment"),  # a comment with a replace
    ]
    for lines in broken:
        assert A.read_record(lines, "sha1") is None, lines


def test_the_reply_grammar():
    assert A.read_record(['reply-to: "01J9Z3M8Q4X7V2K6T0R5N1B8CD"', "kind: comment"], "sha1") == (
        A.Record("comment", None, None, "01J9Z3M8Q4X7V2K6T0R5N1B8CD")
    )
    for lines in (
        ["reply-to: 01J9Z3M8Q4X7V2K6T0R5N1B8CD", "kind: comment"],
        ['reply-to: "01J9Z3M8Q4X7V2K6T0R5N1B8CD"', "kind: suggestion"],
        ['reply-to: "01J9Z3M8Q4X7V2K6T0R5N1B8CD"', "kind: comment", "status: open"],
        ['reply-to:  "01J9Z3M8Q4X7V2K6T0R5N1B8CD"', "kind: comment"],
    ):
        assert A.read_record(lines, "sha1") is None, lines


# --- leaves and keys (section 11.2) -----------------------------------------


def test_a_tables_text_escapes_cell_pipes_and_joins_rows():
    assert A.table_text([["a | b"], ["c"]]) == "a \\| b\nc"
    assert A.table_text([["a", "b"], ["c", ""]]) == "a | b\nc | "
    assert A.table_text([["a | b"]]) != A.table_text([["a", "b"]])


def test_keys_carry_the_heading_level_and_nfc_text():
    snapshot = A.Snapshot(A._default_reader(), "## Caf\u0065\u0301\n\n> - e\u0301\n")
    assert [leaf.key for leaf in snapshot.leaves] == [("h2", "Café"), ("p", "é")]


# --- similarity and its thresholds (section 11.3, addendum detail 5) -------


def test_thresholds_compare_exactly():
    assert 22 / 30 - 42 / 72 < 0.15  # what floating point says
    assert A.exceeds_by_margin((11, 30), (21, 72))  # 22/30 - 42/72 is exactly 0.15
    assert not A.exceeds_by_margin((11, 30), (22, 72))
    assert A.at_least_half((5, 20)) and not A.at_least_half((4, 17))


def test_similarity_is_over_the_written_keys():
    reader = A._default_reader()
    one = A.Snapshot(reader, "abcd\n").leaves[0]
    two = A.Snapshot(reader, "abxy\n").leaves[0]
    # "p\x1fabcd" and "p\x1fabxy": L = 4, T = 12.
    assert A.similarity(one, two) == (4, 12)


def test_the_alignment_skips_the_first_sequence_when_that_keeps_the_lcs():
    # At a and b: skipping a keeps the LCS of what remains at 1, so a goes.
    assert A.lcs_alignment("ab", "ba") == {1: 0}
    assert A.lcs_alignment("abc", "abc") == {0: 0, 1: 1, 2: 2}
    assert A.lcs_alignment("aXb", "ab") == {0: 0, 2: 1}
    assert A.lcs_alignment("ab", "aXb") == {0: 0, 1: 2}


# --- correspondence (section 11.3) ------------------------------------------


def test_the_chain_is_the_leftmost_of_the_longest():
    assert A.leftmost_chain([(0, 1), (1, 0)]) == [(1, 0)]  # a swap: the leaf now first
    assert A.leftmost_chain([(0, 2), (1, 0), (2, 1)]) == [(1, 0), (2, 1)]
    assert A.leftmost_chain([(0, 1), (1, 0), (2, 3), (3, 2)]) == [(1, 0), (3, 2)]
    assert A.leftmost_chain([]) == []


def _corr(base, current):
    reader = A._default_reader()
    return A.Correspondence(A.Snapshot(reader, base).leaves, A.Snapshot(reader, current).leaves)


def test_unique_pairs_on_the_chain_are_exact_and_the_rest_moved():
    corr = _corr(doc(ALPHA, BRAVO, CHARLIE), doc(BRAVO, CHARLIE, ALPHA))
    assert corr.pair == {0: (2, "MOVED"), 1: (0, "EXACT"), 2: (1, "EXACT")}


def test_repeated_keys_pair_by_lcs_inside_a_gap():
    corr = _corr(doc(ALPHA, DIGITS, DIGITS, BRAVO), doc(ALPHA, DIGITS, BRAVO))
    assert corr.pair == {0: (0, "EXACT"), 1: (1, "EXACT"), 3: (2, "EXACT")}


def test_an_edit_pairs_only_with_a_clear_and_mutual_lead():
    edited = SCRAM.replace("rolling window", "rolling 30-second window")
    corr = _corr(doc(ALPHA, SCRAM, BRAVO), doc(ALPHA, edited, BRAVO))
    assert corr.pair[1] == (1, "EDITED")
    # Two candidates as near as each other: no lead of 0.15, no pair.
    twin = SCRAM.replace("rolling window", "rolling 60-second window")
    corr = _corr(doc(ALPHA, SCRAM, BRAVO), doc(ALPHA, edited, twin, BRAVO))
    assert 1 not in corr.pair
    # Below 0.5: no pair.
    corr = _corr(doc(ALPHA, SCRAM, BRAVO), doc(ALPHA, DIGITS, BRAVO))
    assert 1 not in corr.pair


def test_a_moved_leaf_is_left_out_of_the_gaps():
    # SCRAM moves to the end; its old gap pairs nothing with it.
    corr = _corr(doc(ALPHA, SCRAM, BRAVO, CHARLIE), doc(ALPHA, BRAVO, CHARLIE, SCRAM))
    assert corr.pair[1] == (3, "MOVED")
    assert corr.gap(1) == (range(1, 2), range(1, 1))


# --- the anchored leaf (section 11.4) ---------------------------------------


def test_resolved_when_other_leaves_change():
    base = doc(ALPHA, SCRAM, BRAVO)
    got = resolve_one(base, doc(ALPHA, SCRAM, BRAVO + " More."), SCRAM, "4.2 sigma")
    assert got == {
        "status": "RESOLVED",
        "leaf": {"node": [1], "type": "paragraph"},
        "span": [23, 32],
        "suggestion": None,
    }


def test_moved_keeps_the_span():
    base = doc(ALPHA, SCRAM, BRAVO, CHARLIE)
    got = resolve_one(base, doc(ALPHA, BRAVO, CHARLIE, SCRAM), SCRAM, "4.2 sigma")
    assert got == {
        "status": "MOVED",
        "leaf": {"node": [3], "type": "paragraph"},
        "span": [23, 32],
        "suggestion": None,
    }


def test_orphaned_when_the_leaf_is_gone():
    got = resolve_one(doc(ALPHA, SCRAM, BRAVO), doc(ALPHA, BRAVO), SCRAM, "4.2 sigma")
    assert got == {"status": "ORPHANED", "leaf": None, "span": None, "suggestion": None}


def test_no_pair_with_a_copy_left_is_an_unaccounted_copy():
    base = doc(ALPHA, SCRAM, BRAVO, SCRAM)
    got = resolve_one(base, doc(SCRAM, ALPHA, BRAVO), SCRAM, "4.2 sigma")
    assert got["status"] == "REFUSED(unaccounted-copy)"


def test_exact_with_repeats_needs_as_many_copies_in_its_gap():
    base = doc(ALPHA, SCRAM, SCRAM, BRAVO)
    got = resolve_one(base, doc(ALPHA, SCRAM, BRAVO), SCRAM, "4.2 sigma")
    assert got["status"] == "REFUSED(repeat)"
    got = resolve_one(base, doc(ALPHA, SCRAM, BRAVO), SCRAM, "4.2 sigma", nth=1)
    assert got["status"] == "REFUSED(unaccounted-copy)"


def test_identical_copies_kept_apart_by_unique_leaves_resolve():
    base = doc(ALPHA, SCRAM, BRAVO, SCRAM, CHARLIE)
    current = doc(ALPHA, SCRAM, BRAVO + " More.", SCRAM, CHARLIE)
    got = resolve_one(base, current, SCRAM, "4.2 sigma", nth=1)
    assert (got["status"], got["leaf"]) == ("RESOLVED", {"node": [3], "type": "paragraph"})


def test_a_copy_that_crossed_a_unique_leaf_leaves_its_twin_unaccounted():
    # Two copies stay two, but both now sit in the second one's gap: the LCS
    # there pairs the second, and the first has no pair while copies remain.
    base = doc(ALPHA, SCRAM, BRAVO, SCRAM, CHARLIE)
    current = doc(ALPHA, BRAVO, SCRAM, SCRAM, CHARLIE)
    got = resolve_one(base, current, SCRAM, "4.2 sigma", nth=0)
    assert got["status"] == "REFUSED(unaccounted-copy)"
    got = resolve_one(base, current, SCRAM, "4.2 sigma", nth=1)
    assert got["status"] == "REFUSED(repeat)"  # two copies in its gap now, one at base


def test_exact_with_an_unmatched_near_copy_is_refused():
    variant = SCRAM.replace("rolling window", "rolling 30-second window")
    base = doc(ALPHA, SCRAM, BRAVO)
    got = resolve_one(base, doc(ALPHA, SCRAM, BRAVO, variant), SCRAM, "4.2 sigma")
    assert got["status"] == "REFUSED(near-copy)"


def test_moved_with_an_unmatched_near_copy_is_refused():
    variant = SCRAM.replace("rolling window", "rolling 30-second window")
    base = doc(ALPHA, SCRAM, BRAVO, CHARLIE)
    current = doc(ALPHA, variant, BRAVO, CHARLIE, SCRAM)
    assert resolve_one(base, current, SCRAM, "4.2 sigma")["status"] == "REFUSED(near-copy)"


def test_moved_with_its_old_gap_refilled_is_refused():
    base = doc(ALPHA, SCRAM, BRAVO, CHARLIE)
    current = doc(ALPHA, DIGITS, BRAVO, CHARLIE, SCRAM)
    assert resolve_one(base, current, SCRAM, "4.2 sigma")["status"] == "REFUSED(refilled-gap)"


EDITED_SCRAM = SCRAM.replace("rolling window", "rolling 30-second window")


def test_edited_with_an_unmatched_copy_of_its_old_text_is_refused():
    base = doc(ALPHA, SCRAM, BRAVO, SCRAM, CHARLIE)
    current = doc(ALPHA, EDITED_SCRAM, BRAVO, CHARLIE, SCRAM)
    assert resolve_one(base, current, SCRAM, "4.2 sigma")["status"] == "REFUSED(exact-copy)"


def test_edited_beside_a_paired_twin_is_not_an_exact_copy():
    # 0003 Q12: a copy that is some base leaf's pair does not count.
    base = doc(ALPHA, SCRAM, BRAVO, SCRAM, CHARLIE)
    current = doc(ALPHA, EDITED_SCRAM, BRAVO, SCRAM, CHARLIE)
    got = resolve_one(base, current, SCRAM, "4.2 sigma")
    assert (got["status"], got["span"]) == ("EDITED", [23, 32])


def test_edited_with_its_gap_crowded_is_refused():
    base = doc(ALPHA, SCRAM, BRAVO)
    current = doc(ALPHA, EDITED_SCRAM, DIGITS, BRAVO)
    assert resolve_one(base, current, SCRAM, "4.2 sigma")["status"] == "REFUSED(crowded-gap)"


def test_edited_with_an_unmatched_near_copy_elsewhere_is_refused():
    other = SCRAM.replace("rolling window", "rolling 60-second window")
    base = doc(ALPHA, SCRAM, BRAVO, CHARLIE)
    current = doc(ALPHA, EDITED_SCRAM, BRAVO, CHARLIE, other)
    assert resolve_one(base, current, SCRAM, "4.2 sigma")["status"] == "REFUSED(near-copy)"


def test_a_heading_that_changes_level_is_edited():
    base = "## Scram threshold and its basis\n\n" + doc(ALPHA)
    current = "### Scram threshold and its basis\n\n" + doc(ALPHA)
    got = resolve_one(base, current, "Scram threshold and its basis", "threshold", kind="h2")
    assert got == {
        "status": "EDITED",
        "leaf": {"node": [0], "type": "heading"},
        "span": [6, 15],
        "suggestion": None,
    }


# --- the span (section 11.5) ------------------------------------------------


def test_edited_outside_the_context_finds_the_span():
    base = doc(ALPHA, SCRAM, BRAVO)
    current = doc(ALPHA, "Now: " + EDITED_SCRAM, BRAVO)
    # The prefix is short because the leaf's start was near, so it holds only
    # at the start (addendum detail 6): prepending text breaks it. A comment
    # follows on its suffix (0004); a suggestion needs both sides.
    got = resolve_one(base, current, SCRAM, "4.2 sigma")
    assert (got["status"], got["span"]) == ("EDITED", [28, 37])
    got = resolve_one(base, current, SCRAM, "4.2 sigma", replace="5 sigma")
    assert got["status"] == "DETACHED"
    got = resolve_one(base, doc(ALPHA, EDITED_SCRAM, BRAVO), SCRAM, "4.2 sigma")
    assert (got["status"], got["span"]) == ("EDITED", [23, 32])


def test_edited_inside_the_context_keeps_a_comment_on_its_other_side():
    base = doc(ALPHA, SCRAM, BRAVO)
    current = doc(ALPHA, SCRAM.replace("above baseline", "over baseline"), BRAVO)
    # One side edited: a comment follows on the other (0004), a suggestion not.
    got = resolve_one(base, current, SCRAM, "4.2 sigma")
    assert (got["status"], got["span"]) == ("EDITED", [23, 32])
    got = resolve_one(base, current, SCRAM, "4.2 sigma", replace="5 sigma")
    assert got["status"] == "DETACHED"
    edited = SCRAM.replace("scram threshold", "trip threshold").replace("above", "over")
    got = resolve_one(base, doc(ALPHA, edited, BRAVO), SCRAM, "4.2 sigma")
    assert got == {
        "status": "DETACHED",
        "leaf": {"node": [1], "type": "paragraph"},
        "span": None,
        "suggestion": None,
    }


LONG = (
    "Operators shall record every reading in the shift log before handover, and "
    "the threshold of 4.2 sigma applies to every channel that the safety system "
    "monitors during normal operation of the plant."
)


def test_two_hits_are_span_ambiguous():
    base = doc(ALPHA, LONG, BRAVO)
    current = doc(ALPHA, LONG + " Again: " + LONG, BRAVO)
    got = resolve_one(base, current, LONG, "4.2 sigma")
    assert got["status"] == "REFUSED(span-ambiguous)"


def test_a_full_context_hit_may_move_inside_the_leaf():
    base = doc(ALPHA, LONG, BRAVO)
    current = doc(ALPHA, "Note well. " + LONG, BRAVO)
    got = resolve_one(base, current, LONG, "4.2 sigma")
    start = LONG.index("4.2 sigma") + len("Note well. ")
    assert (got["status"], got["span"]) == ("EDITED", [start, start + 9])


def test_the_alignment_must_carry_the_span_onto_the_hit():
    # The span's sentence is rewritten in place and its old wording re-added
    # later with the same context; the alignment carries the old span to the
    # rewritten place, not onto the copy, so the anchor detaches (0003 §5).
    ctx1, ctx2 = "c" * 32, "d" * 32
    base_leaf = ctx1 + "xy" + ctx2
    current_leaf = ctx1 + "yx" + ctx2 + " " + ctx1 + "xy" + ctx2
    start = A.CONTEXT
    anchor = make_anchor(doc(base_leaf), base_leaf, "xy", at=start)
    reader = A._default_reader()
    base = A.Snapshot(reader, doc(base_leaf)).leaves[0]
    current = A.Snapshot(reader, doc(current_leaf)).leaves[0]
    assert A.find_span(anchor, start, base, current) == ("DETACHED", None)
    hit = len(ctx1 + "yx" + ctx2 + " " + ctx1)
    assert A.lcs_alignment(base.text, current.text).get(start) != hit


# --- inputs and consistency (sections 11.1, 11.10) --------------------------


def test_unusable_inputs_each_have_their_reason():
    base = doc(ALPHA, SCRAM)
    anchor = make_anchor(base, SCRAM, "4.2 sigma")
    rec = record(anchor)
    got = run({R: rec}, blobs=[base])["records"][R]
    assert got["status"] == "REFUSED(document-missing)"
    got = run({"doc.md": base, R: rec})["records"][R]
    assert got["status"] == "RESOLVED"  # the control: base is the current blob
    got = run({"doc.md": doc(ALPHA, SCRAM, "x"), R: rec})["records"][R]
    assert got["status"] == "REFUSED(base-unavailable)"
    refused = "<div>\n\n" + base
    anchor = make_anchor(refused, SCRAM, "4.2 sigma")
    got = run({"doc.md": base, R: record(anchor)}, blobs=[refused])["records"][R]
    assert got["status"] == "REFUSED(not-in-profile)"
    conflicted = doc(ALPHA, "<<<<<<< HEAD\nx\n=======\ny\n>>>>>>> b1", SCRAM)
    got = run({"doc.md": conflicted, R: record(make_anchor(base, SCRAM, "4.2 sigma"))}, [base])
    assert got["records"][R]["status"] == "REFUSED(not-in-profile)"


@pytest.mark.parametrize(
    "change",
    [
        lambda a: a.__class__(**{**a.__dict__, "nth": 1}),
        lambda a: a.__class__(**{**a.__dict__, "text": a.text + " x"}),
        lambda a: a.__class__(**{**a.__dict__, "type": "h1"}),
        lambda a: a.__class__(**{**a.__dict__, "prefix": a.prefix[1:]}),
        lambda a: a.__class__(**{**a.__dict__, "suffix": a.suffix[:-1]}),
        lambda a: a.__class__(**{**a.__dict__, "span": "", "suffix": "4.2 sigma" + a.suffix[:23]}),
    ],
)
def test_a_record_inconsistent_with_base_is_refused(change):
    base = doc(ALPHA, LONG)
    anchor = change(make_anchor(base, LONG, "4.2 sigma"))
    got = run({"doc.md": base, R: record(anchor)})["records"][R]
    assert got["status"] == "REFUSED(record-inconsistent)"


def test_a_context_that_occurs_twice_is_inconsistent():
    text = "ab ab"
    anchor = A.Anchor(oid(doc(text)), "p", 0, text, "ab", "", "", None)
    assert run({"doc.md": doc(text), R: record(anchor)})["records"][R]["status"] == (
        "REFUSED(record-inconsistent)"
    )


def test_a_record_with_no_frontmatter_is_inconsistent():
    got = run({"doc.md": doc(ALPHA), R: "Just a note.\n"})["records"][R]
    assert got == {
        "status": "REFUSED(record-inconsistent)",
        "leaf": None,
        "span": None,
        "suggestion": None,
    }


def test_input_problems_are_reported_in_data_dependency_order():
    """Section 11.10, *Which reason is reported*: grammar, document-missing,
    the document's profile, base-unavailable, base's profile, leaf at nth."""
    base = doc(ALPHA, SCRAM)
    good = make_anchor(base, SCRAM, "4.2 sigma")
    twice = A.Anchor(**{**good.__dict__, "text": SCRAM + " " + SCRAM})
    absent = A.Anchor(**{**good.__dict__, "nth": 1})
    refused_base = "<div>\n\n" + base
    on_refused = A.Anchor(**{**good.__dict__, "base": oid(refused_base)})
    conflicted = doc(ALPHA, "<<<<<<< HEAD", SCRAM)

    def status(tree_doc, anchor, blobs=()):
        tree = {R: record(anchor)}
        if tree_doc is not None:
            tree["doc.md"] = tree_doc
        return run(tree, blobs=blobs)["records"][R]["status"]

    # 1 before 2: a triple that occurs twice, with no document and no base.
    assert status(None, twice) == "REFUSED(record-inconsistent)"
    # 2 before 3 cannot both hold; 2 before 4.
    assert status(None, good) == "REFUSED(document-missing)"
    # 3 before 4.
    assert status(conflicted, good) == "REFUSED(not-in-profile)"
    # 4 before 6: the leaf at nth cannot be checked without base.
    assert status(doc(BRAVO), absent) == "REFUSED(base-unavailable)"
    # 5 before 6.
    assert status(doc(BRAVO), on_refused, [refused_base]) == "REFUSED(not-in-profile)"
    # 6 alone.
    assert status(doc(BRAVO), absent, [base]) == "REFUSED(record-inconsistent)"


@pytest.mark.parametrize(
    "path",
    [
        "doc.md.notes/not-a-ulid.md",
        "doc.md.notes/01j9z3m8q4x7v2k6t0r5n1b8cd.md",
        "doc.md.notes/81J9Z3M8Q4X7V2K6T0R5N1B8CD.md",
        "doc.md.notes/01J9Z3M8Q4X7V2K6T0R5N1B8CD.txt",
        "doc.md.notes/sub/01J9Z3M8Q4X7V2K6T0R5N1B8CD.md",
    ],
)
def test_an_entry_of_a_notes_directory_that_is_not_a_record_is_inconsistent(path):
    # Second addendum, item 5, before every other input problem (step 1).
    base = doc(ALPHA, SCRAM)
    got = run({path: record(make_anchor(base, SCRAM, "4.2"))}, records=[path])
    assert got["records"][path]["status"] == "REFUSED(record-inconsistent)"


def test_a_path_in_no_notes_directory_is_undecided():
    path = "doc.md/01J9Z3M8Q4X7V2K6T0R5N1B8CD.md"
    base = doc(ALPHA, SCRAM)
    got = run({"doc.md": base, path: record(make_anchor(base, SCRAM, "4.2"))}, records=[path])
    assert got["records"][path]["status"] == "UNDECIDED"


def test_a_context_longer_than_32_is_inconsistent():
    base = doc(ALPHA, LONG)
    anchor = make_anchor(base, LONG, "4.2 sigma")
    start = LONG.index("4.2 sigma")
    end = start + len("4.2 sigma")
    for change in ({"prefix": LONG[start - 33 : start]}, {"suffix": LONG[end : end + 33]}):
        longer = A.Anchor(**{**anchor.__dict__, **change})
        got = run({R: record(longer)})["records"][R]  # before document-missing
        assert got["status"] == "REFUSED(record-inconsistent)", change


def test_a_record_whose_body_the_profile_refuses_is_inconsistent():
    base = doc(ALPHA, SCRAM)
    rec = record(make_anchor(base, SCRAM, "4.2 sigma", replace="5")) + "\nText\n===\n"
    got = run({R: rec})["records"][R]  # before document-missing
    assert got == {
        "status": "REFUSED(record-inconsistent)",
        "leaf": None,
        "span": None,
        "suggestion": {"gate": "stale", "reason": None},
    }


# --- replies and warnings (section 11.8) ------------------------------------


def test_replies():
    base = doc(ALPHA, SCRAM)
    parent = record(make_anchor(base, SCRAM, "4.2 sigma"))
    reply = '---\nreply-to: "01J9Z3M8Q4X7V2K6T0R5N1B8CD"\nkind: comment\n---\n\nAgreed.\n'
    got = run({"doc.md": base, R: parent, R2: reply}, records=[R2])["records"][R2]
    assert got == {"status": "REPLY", "leaf": None, "span": None, "suggestion": None}
    got = run({"doc.md": base, R2: reply}, records=[R2])["records"][R2]
    assert got["status"] == "#REF!(reply-to)"
    for bad in (
        reply.replace('"01J9Z3M8Q4X7V2K6T0R5N1B8CD"', "01J9Z3M8Q4X7V2K6T0R5N1B8CD"),
        reply.replace("01J9Z3M8Q4X7V2K6T0R5N1B8CD", "01j9z3m8q4x7v2k6t0r5n1b8cd"),
        reply.replace("01J9Z3M8Q4X7V2K6T0R5N1B8CD", "../x"),
    ):
        got = run({"doc.md": base, R: parent, R2: bad}, records=[R2])["records"][R2]
        assert got["status"] == "REFUSED(record-inconsistent)", bad


def test_a_record_id_in_two_notes_directories_is_reported():
    tree = {
        "a.md.notes/01J9Z3M8Q4X7V2K6T0R5N1B8CD.md": "",
        "archive/a.md.notes/01J9Z3M8Q4X7V2K6T0R5N1B8CD.md": "",
        "a.md.notes/01J9Z3M8Q4X7V2K6T0R5N1B8CE.md": "",
    }
    assert A.duplicate_record_ids(tree) == {
        "01J9Z3M8Q4X7V2K6T0R5N1B8CD": ["a.md.notes", "archive/a.md.notes"]
    }


# --- suggestions and write-back (section 11.7) ------------------------------


def suggest(base, current, leaf_text, span, replace, status="open", **kw):
    anchor = make_anchor(base, leaf_text, span, replace=replace, **kw)
    return run({"doc.md": current, R: record(anchor, status)}, blobs=[base])["records"][R]


def test_a_suggestion_applies_only_when_open_and_resolved_or_edited():
    base = doc(ALPHA, SCRAM, BRAVO)
    got = suggest(base, base, SCRAM, "4.2 sigma", "5 sigma")
    assert got["suggestion"] == {"gate": "apply", "written": base.replace("4.2 sigma", "5 sigma")}
    for status in ("accepted", "rejected", "resolved"):
        got = suggest(base, base, SCRAM, "4.2 sigma", "5 sigma", status=status)
        assert got["suggestion"] == {"gate": "stale", "reason": None}, status
    current = doc(ALPHA, EDITED_SCRAM, BRAVO)
    got = suggest(base, current, SCRAM, "4.2 sigma", "5 sigma")
    assert got["suggestion"] == {
        "gate": "apply",
        "written": current.replace("4.2 sigma", "5 sigma"),
    }


def test_a_suggestion_is_stale_on_moved_detached_and_refused():
    base = doc(ALPHA, SCRAM, BRAVO, CHARLIE)
    moved = suggest(base, doc(ALPHA, BRAVO, CHARLIE, SCRAM), SCRAM, "4.2 sigma", "5")
    assert (moved["status"], moved["suggestion"]) == ("MOVED", {"gate": "stale", "reason": None})
    detached = doc(ALPHA, SCRAM.replace("above", "over"), BRAVO, CHARLIE)
    got = suggest(base, detached, SCRAM, "4.2 sigma", "5")
    assert (got["status"], got["suggestion"]) == ("DETACHED", {"gate": "stale", "reason": None})
    got = suggest(base, doc(ALPHA, BRAVO), SCRAM, "4.2 sigma", "5")
    assert (got["status"], got["suggestion"]) == ("ORPHANED", {"gate": "stale", "reason": None})


def test_a_suggestion_with_broken_grammar_is_stale():
    base = doc(ALPHA, SCRAM)
    anchor = make_anchor(base, SCRAM, "4.2 sigma", replace="5")
    rec = record(anchor).replace("status: open", "status: maybe")
    got = run({"doc.md": base, R: rec})["records"][R]
    assert got["suggestion"] == {"gate": "stale", "reason": None}
    assert got["status"] == "REFUSED(record-inconsistent)"


def test_write_back_keeps_crlf_and_writes_a_break_as_the_lines_ending():
    base = "Alpha one.\r\n\r\nThe value is\r\nfour point two here.\r\n"
    leaf = "The value is\nfour point two here."
    got = suggest(base, base, leaf, "is\nfour", "is\nnow\nfour")
    assert got["suggestion"]["written"] == (
        "Alpha one.\r\n\r\nThe value is\r\nnow\r\nfour point two here.\r\n"
    )
    # Only a \n is rewritten: a CR in `replace` is written as stored.
    got = suggest(base, base, leaf, "is\nfour", "is\r\nfour")
    assert got["suggestion"]["written"] == (
        "Alpha one.\r\n\r\nThe value is\r\r\nfour point two here.\r\n"
    )


def test_write_back_in_a_bare_cr_file():
    base = "Alpha one.\r\rThe value is\rfour point two here.\r"
    leaf = "The value is\nfour point two here."
    got = suggest(base, base, leaf, "value is\nfour", "value\nis four")
    assert got["suggestion"]["written"] == "Alpha one.\r\rThe value\ris four point two here.\r"


def test_write_back_over_a_line_break_drops_the_next_lines_prefix():
    base = "> The value is\n> four point two here.\n"
    leaf = "The value is\nfour point two here."
    got = suggest(base, base, leaf, "is\nfour", "is four")
    assert got["suggestion"]["written"] == "> The value is four point two here.\n"


def test_write_back_prefixes_a_new_line_in_a_block_quote():
    base = "> > The value is four\n> > point two here.\n"
    leaf = "The value is four\npoint two here."
    got = suggest(base, base, leaf, "is four", "is\nfour")
    assert got["suggestion"]["written"] == "> > The value is\n> > four\n> > point two here.\n"


def test_write_back_prefixes_a_new_line_in_a_list_items_continuation():
    base = "- Item one.\n- The value is four\n  point two here.\n"
    leaf = "The value is four\npoint two here."
    got = suggest(base, base, leaf, "two here", "two\nhere")
    assert got["suggestion"]["written"] == (
        "- Item one.\n- The value is four\n  point two\n  here.\n"
    )
    # A break in the item's first line, whose prefix is the list marker.
    got = suggest(base, base, leaf, "is four", "is\nfour")
    assert got["suggestion"] == {"gate": "stale", "reason": "unmappable-offset"}


def test_write_back_maps_through_lost_indentation():
    base = "   The value is\n     four point two.\n"
    leaf = "The value is\nfour point two."
    got = suggest(base, base, leaf, "is\nfour", "was four")
    assert got["suggestion"]["written"] == "   The value was four point two.\n"


def test_write_back_leaves_the_rest_of_the_leaf_in_its_normalisation_form():
    nfd = "Cafe\u0301 au lait at 4.2 sigma, cafe\u0301 noir."
    base = doc(ALPHA, nfd)
    got = suggest(base, base, unicodedata.normalize("NFC", nfd), "4.2", "5.0")
    assert got["suggestion"]["written"] == doc(ALPHA, nfd.replace("4.2", "5.0"))
    # A span that is a composed character maps onto its decomposed bytes.
    got = suggest(base, base, unicodedata.normalize("NFC", nfd), "é", "e", at=3)
    assert got["suggestion"]["written"] == doc(ALPHA, nfd.replace("e\u0301", "e", 1))


def test_a_span_that_does_not_map_is_unmappable():
    # NFC composes a with the acute across the cedilla, so no prefix of the
    # raw content normalises to the span "á".
    text = "Then a\u0327\u0301 here at the end."
    base = doc(ALPHA, text)
    got = suggest(base, base, unicodedata.normalize("NFC", text), "\u00e1", "a")
    assert got["status"] == "RESOLVED"
    assert got["suggestion"] == {"gate": "stale", "reason": "unmappable-offset"}


def test_write_back_into_a_heading_and_a_code_block():
    base = "# The 4.2 limit\n\n```\nlimit = 4.2\n```\n"
    got = suggest(base, base, "The 4.2 limit", "4.2", "5.0", kind="h1")
    assert got["suggestion"]["written"] == base.replace("The 4.2", "The 5.0")
    got = suggest(base, base, "limit = 4.2\n", "4.2", "5.0", kind="code")
    assert got["suggestion"]["written"] == base.replace("= 4.2", "= 5.0")


def test_write_back_into_a_table_is_undecided():
    base = "| a | b |\n| - | - |\n| 4.2 | x |\n"
    text = "a | b\n4.2 | x"
    got = suggest(base, base, text, "4.2", "5.0", kind="table")
    assert got["status"] == "UNDECIDED"
    got = suggest(base, base, text, "4.2", "5.0", kind="table", status="accepted")
    assert (got["status"], got["suggestion"]) == ("RESOLVED", {"gate": "stale", "reason": None})


def test_a_break_in_a_last_line_with_no_ending_is_unmappable():
    base = "The value is four"
    got = suggest(base, base, "The value is four", "four", "four\nfive")
    assert got["suggestion"] == {"gate": "stale", "reason": "unmappable-offset"}
    got = suggest(base, base, "The value is four", "four", "five")
    assert got["suggestion"] == {"gate": "apply", "written": "The value is five"}


def test_the_document_hook_loads_the_resolver_by_path():
    base = doc(ALPHA, SCRAM)
    anchor = make_anchor(base, SCRAM, "4.2 sigma")
    repo = {"object_format": "sha1", "tree": {"doc.md": base, R: record(anchor)}}
    repo["blobs"] = {oid(base): base}
    assert document.resolve(repo, {"records": [R]})["records"][R]["status"] == "RESOLVED"


# --- transclusion (section 11.9) --------------------------------------------

TARGET = doc(ALPHA, "<!-- #scram -->\n" + SCRAM, BRAVO)


def referrer(*paragraphs, pins=None, path="policy.md", blob=None):
    head = ""
    if pins is not None:
        head = "---\npins:\n" + "".join(f"  - {p}\n" for p in pins) + "---\n\n"
    elif blob is not None:
        head = f'---\npins:\n  - {{"path": "{path}", "blob": "{blob}"}}\n---\n\n'
    return head + doc(*paragraphs)


LINK = '[Scram](policy.md#scram "transclude")'


def transclude(tree, blobs=(), name="guide.md"):
    got = run(tree, blobs, records=(), transclusions=[name])
    return got["transclusions"][name]


def test_a_transclusion_resolves_to_what_the_name_binds():
    tree = {"policy.md": TARGET, "guide.md": referrer(ALPHA, LINK, blob=oid(TARGET))}
    assert transclude(tree) == [
        {
            "leaf": {"node": [1], "type": "paragraph"},
            "status": "RESOLVED",
            "unit": {"document": "policy.md", "target": {"node": [2], "type": "paragraph"}},
        }
    ]


def test_a_region_resolves_and_editing_inside_it_still_resolves():
    region = "<!-- #part:begin -->\n\n" + doc(SCRAM, BRAVO) + "\n<!-- #part:end -->\n"
    target = doc(ALPHA) + "\n" + region
    edited = target.replace("rolling window", "rolling 30-second window")
    link = '[Part](policy.md#part "transclude")'
    tree = {"policy.md": edited, "guide.md": referrer(link, blob=oid(target))}
    got = transclude(tree, blobs=[target])
    assert got[0]["status"] == "RESOLVED"
    assert got[0]["unit"]["target"] == {
        "region": [{"node": [2], "type": "paragraph"}, {"node": [3], "type": "paragraph"}]
    }


def test_a_name_that_binds_nothing_now_is_ref():
    moved = TARGET.replace("<!-- #scram -->\n", "")
    tree = {"policy.md": moved, "guide.md": referrer(LINK, blob=oid(TARGET))}
    got = transclude(tree, blobs=[TARGET])
    assert got[0]["status"] == "#REF!(scram)" and got[0]["unit"] is None


def test_a_leaf_inserted_under_a_one_line_marker_rebinds_the_name():
    rebound = TARGET.replace("<!-- #scram -->\n", "<!-- #scram -->\n" + DIGITS + "\n\n")
    tree = {"policy.md": rebound, "guide.md": referrer(LINK, blob=oid(TARGET))}
    assert transclude(tree, blobs=[TARGET])[0]["status"] == "REFUSED(name-rebound)"


def test_a_pinned_leaf_that_is_gone_or_refused_refuses_the_transclusion():
    gone = doc(ALPHA, "<!-- #scram -->\n" + DIGITS, BRAVO)
    tree = {"policy.md": gone, "guide.md": referrer(LINK, blob=oid(TARGET))}
    assert transclude(tree, blobs=[TARGET])[0]["status"] == "REFUSED(pinned-orphaned)"
    crowded = doc(ALPHA, "<!-- #scram -->\n" + EDITED_SCRAM, DIGITS, BRAVO)
    tree = {"policy.md": crowded, "guide.md": referrer(LINK, blob=oid(TARGET))}
    assert transclude(tree, blobs=[TARGET])[0]["status"] == "REFUSED(pinned-crowded-gap)"


def test_transclusion_inputs_each_have_their_reason():
    pin = oid(TARGET)
    assert transclude({"guide.md": referrer(LINK, blob=pin)}, [TARGET])[0]["status"] == (
        "REFUSED(document-missing)"
    )
    tree = {"policy.md": TARGET, "guide.md": referrer(LINK, blob="0" * 40)}
    assert transclude(tree)[0]["status"] == "REFUSED(base-unavailable)"
    conflicted = TARGET + "<<<<<<< HEAD\n"
    tree = {"policy.md": conflicted, "guide.md": referrer(LINK, blob=pin)}
    assert transclude(tree, [TARGET])[0]["status"] == "REFUSED(not-in-profile)"
    unnamed = TARGET.replace("<!-- #scram -->\n", "")
    tree = {"policy.md": TARGET, "guide.md": referrer(LINK, blob=oid(unnamed))}
    assert transclude(tree, [unnamed])[0]["status"] == "REFUSED(record-inconsistent)"


@pytest.mark.parametrize(
    "path",
    ["/policy.md", "https://example.org/policy.md", "C:/policy.md", "../policy.md"],
)
def test_an_absolute_path_or_one_above_the_root_is_unresolvable(path):
    link = f'[Scram]({path}#scram "transclude")'
    tree = {"policy.md": TARGET, "guide.md": referrer(link, path=path, blob=oid(TARGET))}
    assert transclude(tree)[0]["status"] == "REFUSED(unresolvable-path)"


def test_paths_resolve_from_the_referrers_directory():
    assert A.resolve_path("docs/guide.md", "policy.md") == "docs/policy.md"
    assert A.resolve_path("docs/guide.md", "../policy.md") == "policy.md"
    assert A.resolve_path("docs/guide.md", "./a/../policy.md") == "docs/policy.md"
    assert A.resolve_path("guide.md", "my%20doc.md") == "my%20doc.md"
    link = '[Scram](../policy.md#scram "transclude")'
    tree = {
        "policy.md": TARGET,
        "docs/guide.md": referrer(link, path="../policy.md", blob=oid(TARGET)),
    }
    got = transclude(tree, name="docs/guide.md")
    assert got[0]["unit"]["document"] == "policy.md"
    tree = {"Policy.md": TARGET, "guide.md": referrer(LINK, blob=oid(TARGET))}
    assert transclude(tree)[0]["status"] == "REFUSED(document-missing)"


def test_the_pins_grammar():
    pin = '{"path": "a.md", "blob": "' + "0" * 40 + '"}'
    pin_b = '{"path": "b.md", "blob": "' + "1" * 40 + '"}'
    assert A.read_pins(["pins:", f"  - {pin}", f"  - {pin_b}"], "sha1") == {
        "a.md": "0" * 40,
        "b.md": "1" * 40,
    }
    assert A.read_pins(["title: x"], "sha1") == {}
    assert A.read_pins(None, "sha1") == {}
    assert A.read_pins(["pins:", f"  - {pin}", "other: x", f"  - {pin_b}"], "sha1") == {
        "a.md": "0" * 40
    }
    for lines in (
        ["pins:", f"  - {pin_b}", f"  - {pin}"],  # out of order
        ["pins:", f"  - {pin}", f"  - {pin}"],  # a path twice
        ["pins: ", f"  - {pin}"],
        ["pins:", f"  - {pin}", "pins:"],
        ["pins:", f"  - {pin.replace(', ', ',')}"],
        ["pins:", f"  - {pin.replace('0' * 40, 'A' * 40)}"],
        ["pins:", f"  - {pin.replace('0' * 40, '0' * 64)}"],
        ["pins:", "  - " + '{"blob": "' + "0" * 40 + '", "path": "a.md"}'],
        ["pins:", f"  - {pin}", "", f"  - {pin_b}"],
        ["pins:", f"  - {pin}", "# note", f"  - {pin_b}"],
        ["pins:", f"  - {pin}", "   ", f"  - {pin_b}"],
    ):
        assert A.read_pins(lines, "sha1") is None, lines


def test_broken_pins_refuse_every_transclusion():
    other = '[Other](other.md#scram "transclude")'
    pins = [
        '{"path": "policy.md", "blob": "' + oid(TARGET) + '"}',
        '{"path": "other.md", "blob": "' + oid(TARGET) + '"}',
    ]  # out of order
    tree = {"policy.md": TARGET, "other.md": TARGET, "guide.md": referrer(LINK, other, pins=pins)}
    assert [t["status"] for t in transclude(tree)] == ["REFUSED(record-inconsistent)"] * 2


@pytest.mark.parametrize(
    "paragraph, question",
    [
        ('See [Scram](policy.md#scram "transclude") here.', "other text"),
        ('[Scram](<policy.md#scram> "transclude")', "angle brackets"),
        ("[Scram](policy.md#scram 'transclude')", "quoting form"),
        ("[Scram](policy.md#scram (transclude))", "quoting form"),
        ('[Scram](policy.md#scram "&#116;ransclude")', "quoting form"),
        ('[Scram](policy.md#scram "trans\\clude")', None),
        ('[Scram](policy.md "transclude")', "no `#name`"),
        ('[Scram](#scram "transclude")', "no path"),
        ('[`Scram`](policy.md#scram "transclude")', "code span"),
        ('[Scram](policy.md#scram "Transclude")', None),
        ("[Scram](policy.md#scram)", None),
    ],
)
def test_shapes_section_12_leaves_open_are_undecided(paragraph, question):
    tree = {"policy.md": TARGET, "guide.md": referrer(paragraph, blob=oid(TARGET))}
    got = transclude(tree)
    if question is None:
        assert got == []
    else:
        assert got[0]["status"] == "UNDECIDED" and question in got[0]["question"], got


def test_a_transclusion_in_a_list_item_or_with_no_pin_is_undecided():
    tree = {"policy.md": TARGET, "guide.md": referrer("- " + LINK, blob=oid(TARGET))}
    assert "list item" in transclude(tree)[0]["question"]
    tree = {"policy.md": TARGET, "guide.md": doc(LINK)}
    assert transclude(tree)[0]["question"] == "a transclusion with no pin"


def test_a_document_that_transcludes_itself_is_undecided():
    self_link = '[Me](guide.md#me "transclude")'
    tree = {
        "guide.md": referrer("<!-- #me -->\n" + ALPHA, self_link, path="guide.md", blob="0" * 40)
    }
    assert "transcludes itself" in transclude(tree)[0]["question"]
    back = '[Back](guide.md#me "transclude")'
    tree = {
        "policy.md": referrer("<!-- #scram -->\n" + SCRAM, back, path="guide.md", blob="0" * 40),
        "guide.md": referrer("<!-- #me -->\n" + ALPHA, LINK, blob=oid(TARGET)),
    }
    assert "transcludes itself" in transclude(tree)[0]["question"]


def test_an_empty_segment_or_a_file_that_is_not_markdown_is_undecided():
    for path, question in (
        ("a//policy.md", "an empty segment in a transclusion path"),
        ("policy.txt", "a transclusion path that names a file that is not markdown"),
    ):
        link = f'[Scram]({path}#scram "transclude")'
        tree = {"guide.md": referrer(link, path=path, blob=oid(TARGET)), path: TARGET}
        got = transclude(tree, blobs=[TARGET])[0]
        assert (got["status"], got["question"]) == ("UNDECIDED", question), path


def test_write_back_through_a_partly_consumed_tab():
    # The item's two columns take two of the tab's four, and the reader gives
    # the other two as spaces no raw character is alone the source of.
    base = "- ```\n\tx = 4.2\n  ```\n"
    got = suggest(base, base, "  x = 4.2\n", "4.2", "5.0", kind="code")
    assert got["suggestion"]["written"] == "- ```\n\tx = 5.0\n  ```\n"
    got = suggest(base, base, "  x = 4.2\n", " x", "y", kind="code")
    assert got["suggestion"] == {"gate": "stale", "reason": "unmappable-offset"}


def test_a_negative_nth_is_not_read():
    line = A.write_anchor(make_anchor(doc(SCRAM), SCRAM, "4.2 sigma"))
    assert A.read_anchor(line.replace('"nth": 0', '"nth": -1'), "sha1") is None


def test_an_edit_needs_a_lead_over_the_other_base_leaves_too():
    # One current leaf, two base leaves near it: no mutual lead, no pair.
    near = SCRAM.replace("rolling window", "rolling 60-second window")
    base = doc(ALPHA, SCRAM, near, BRAVO)
    got = resolve_one(base, doc(ALPHA, EDITED_SCRAM, BRAVO), SCRAM, "4.2 sigma")
    assert got["status"] == "ORPHANED"


def test_a_copy_added_beside_an_unchanged_leaf_is_a_repeat():
    # The rule fires when either side holds more than one copy.
    base = doc(ALPHA, SCRAM, BRAVO)
    got = resolve_one(base, doc(ALPHA, SCRAM, SCRAM, BRAVO), SCRAM, "4.2 sigma")
    assert got["status"] == "REFUSED(repeat)"


def test_an_unmatched_exact_copy_elsewhere_is_no_near_copy_of_an_exact_leaf():
    base = doc(ALPHA, SCRAM, BRAVO, CHARLIE)
    got = resolve_one(base, doc(ALPHA, SCRAM, BRAVO, CHARLIE, SCRAM), SCRAM, "4.2 sigma")
    assert (got["status"], got["leaf"]) == ("RESOLVED", {"node": [1], "type": "paragraph"})


def test_a_full_context_that_occurs_twice_is_inconsistent():
    half = "c" * 32 + "span" + "d" * 32
    text = half + " " + half
    anchor = A.Anchor(oid(doc(text)), "p", 0, text, "span", "c" * 32, "d" * 32, None)
    got = run({"doc.md": doc(text), R: record(anchor)})["records"][R]
    assert got["status"] == "REFUSED(record-inconsistent)"


def test_overlapping_occurrences_count():
    text = "ab" * 60
    anchor = A.Anchor(oid(doc(text)), "p", 0, text, "ab", text[8:40], text[42:74], None)
    got = run({"doc.md": doc(text), R: record(anchor)})["records"][R]
    assert got["status"] == "REFUSED(record-inconsistent)"
    assert A.occurrences("aaa", "aa") == [0, 1]


def test_a_short_suffix_must_end_at_the_leafs_end():
    leaf = "Operators note that the scram threshold for every channel is 4.2."
    base = doc(ALPHA, leaf, BRAVO)
    current = doc(ALPHA, leaf + " It was 4.0.", BRAVO)
    # The suffix "." is short, so it holds only at the leaf's end. A comment
    # follows on its prefix (0004); a suggestion, or a comment whose prefix
    # was edited too, detaches.
    assert resolve_one(base, current, leaf, "4.2")["status"] == "EDITED"
    assert resolve_one(base, current, leaf, "4.2", replace="5")["status"] == "DETACHED"
    both = doc(ALPHA, leaf.replace("for every", "on each") + " It was 4.0.", BRAVO)
    assert resolve_one(base, both, leaf, "4.2")["status"] == "DETACHED"
    current = doc(ALPHA, "Today, o" + leaf[1:], BRAVO)
    got = resolve_one(base, current, leaf, "4.2")
    assert got["status"] == "EDITED"


def test_a_break_in_a_lazy_line_or_through_a_tab_prefix_is_unmappable():
    leaf = "The value is four\npoint two here."
    stale = {"gate": "stale", "reason": "unmappable-offset"}
    for base in (
        "- The value is four\npoint two here.\n",
        "> The value is four\npoint two here.\n",
    ):
        assert suggest(base, base, leaf, "two here", "two\nhere")["suggestion"] == stale, base
        # Without a break, the lazy line maps.
        got = suggest(base, base, leaf, "two here", "two there")
        assert got["suggestion"]["gate"] == "apply", base
    base = ">\tThe value is four\n>\tpoint two here.\n"
    assert suggest(base, base, leaf, "two here", "two\nhere")["suggestion"] == stale


def test_the_runner_resolves_an_anchor_case_with_the_reference(tmp_path):
    """End to end: placeholders, git's ids, a stock merge and the hook, through
    `run_cases.py --impl reference/blockspec/document.py`, on a synthetic case
    in a temporary tree (not a conformance case)."""
    import json
    import os
    import subprocess
    import sys

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base = doc(ALPHA, SCRAM, BRAVO)
    ours = doc(ALPHA + " Ours.", SCRAM, BRAVO)
    theirs = doc(ALPHA, SCRAM, BRAVO + " Theirs.")
    anchor = make_anchor(base, SCRAM, "4.2 sigma")
    line = A.write_anchor(anchor).replace(anchor.base, "{{blob:merge/base/doc.md}}")
    rec = f"---\nanchor: {line}\nkind: comment\nstatus: open\n---\n"
    case = tmp_path / "cases" / "anchor" / "one"
    files = {
        "merge/base/doc.md": base,
        "merge/ours/doc.md": ours,
        "merge/theirs/doc.md": theirs,
        f"tree/{R}": rec,
        "WHY.md": "Synthetic.\n",
    }
    expect = {
        "kind": "anchor",
        "merge": {"doc.md": "clean"},
        "records": {
            R: {
                "status": "RESOLVED",
                "leaf": {"node": [1], "type": "paragraph"},
                "span": [23, 32],
                "suggestion": None,
            }
        },
    }
    for rel, text in {**files, "expect.json": json.dumps(expect)}.items():
        (case / rel).parent.mkdir(parents=True, exist_ok=True)
        (case / rel).write_text(text, encoding="utf-8")
    done = subprocess.run(
        [
            sys.executable,
            os.path.join(root, "conformance", "run_cases.py"),
            "--impl",
            os.path.join(root, "reference", "blockspec", "document.py"),
            str(tmp_path / "cases"),
            "--min-cases",
            "1",
        ],
        capture_output=True,
        text=True,
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
    )
    assert done.returncode == 0, done.stdout + done.stderr
    expect["records"][R]["status"] = "EDITED"
    (case / "expect.json").write_text(json.dumps(expect), encoding="utf-8")
    done = subprocess.run(done.args, capture_output=True, text=True)
    assert done.returncode == 1, done.stdout + done.stderr


# --- the order of a transclusion's steps (section 11.9, second addendum) ---


def test_a_referrer_the_profile_refuses_is_refused_as_a_whole():
    for body in (
        referrer(LINK, blob=oid(TARGET)).replace("pins:", "pins:\n<<<<<<< HEAD", 1),
        referrer(LINK, "```\n=======\n```", blob=oid(TARGET)),
        referrer(LINK, "Title\n=====", blob=oid(TARGET)),
    ):
        got = run({"policy.md": TARGET, "guide.md": body}, records=(), transclusions=["guide.md"])
        assert got["transclusions"]["guide.md"] == "REFUSED(not-in-profile)", body


def test_an_unresolvable_path_comes_before_broken_pins():
    link = '[Scram](/policy.md#scram "transclude")'
    pins = [
        '{"path": "b.md", "blob": "' + "0" * 40 + '"}',
        '{"path": "a.md", "blob": "' + "0" * 40 + '"}',
    ]
    tree = {"policy.md": TARGET, "guide.md": referrer(link, pins=pins)}
    assert transclude(tree)[0]["status"] == "REFUSED(unresolvable-path)"


def test_broken_pins_come_before_a_missing_document():
    pins = ['{"path": "policy.md", "blob": "' + "0" * 40 + '"}'] * 2  # a path twice
    tree = {"guide.md": referrer(LINK, pins=pins)}
    assert transclude(tree)[0]["status"] == "REFUSED(record-inconsistent)"


def test_the_current_target_comes_before_the_pin():
    bad_pin = referrer(LINK, blob="0" * 40)  # an unreadable pinned blob
    assert transclude({"guide.md": bad_pin})[0]["status"] == "REFUSED(document-missing)"
    conflicted = TARGET + "<<<<<<< HEAD\n"
    got = transclude({"policy.md": conflicted, "guide.md": bad_pin})
    assert got[0]["status"] == "REFUSED(not-in-profile)"


def test_a_name_only_a_heading_slug_matches_is_ref_before_the_pin_is_read():
    slugged = doc("# Scram", ALPHA, SCRAM, BRAVO)
    bad_pin = referrer(LINK, blob="0" * 40)
    got = transclude({"policy.md": slugged, "guide.md": bad_pin})
    assert (got[0]["status"], got[0]["unit"]) == ("#REF!(scram)", None)
    unslugged = doc("# Other", ALPHA, SCRAM, BRAVO)
    got = transclude({"policy.md": unslugged, "guide.md": bad_pin})
    assert got[0]["status"] == "REFUSED(base-unavailable)"
    # A marker name that is also a heading's slug binds through the marker.
    both = "# Scram\n\n" + TARGET
    got = transclude({"policy.md": both, "guide.md": referrer(LINK, blob=oid(TARGET))}, [TARGET])
    assert got[0]["unit"] == {"document": "policy.md", "target": {"node": [3], "type": "paragraph"}}


def test_the_pinned_blob_is_read_before_its_binding():
    refused = TARGET + "\nTitle\n=====\n"
    tree = {"policy.md": TARGET, "guide.md": referrer(LINK, blob=oid(refused))}
    assert transclude(tree, [refused])[0]["status"] == "REFUSED(not-in-profile)"


def test_of_several_pinned_reasons_the_first_leaf_in_the_pinned_blob_decides():
    def region(*leaves):
        return "<!-- #r:begin -->\n\n" + doc(*leaves) + "\n<!-- #r:end -->\n"

    edited_bravo = BRAVO.replace("limits", "limits today")
    link = '[R](policy.md#r "transclude")'
    for pinned_leaves, current_leaves, want in (
        ((SCRAM, BRAVO), (edited_bravo, DIGITS), "REFUSED(pinned-orphaned)"),
        ((BRAVO, SCRAM), (edited_bravo, DIGITS), "REFUSED(pinned-crowded-gap)"),
    ):
        pinned = doc(ALPHA) + "\n" + region(*pinned_leaves) + "\n" + doc(CHARLIE)
        current = doc(ALPHA) + "\n" + region(*current_leaves) + "\n" + doc(CHARLIE)
        tree = {"policy.md": current, "guide.md": referrer(link, blob=oid(pinned))}
        assert transclude(tree, [pinned])[0]["status"] == want, pinned_leaves


# --- found in review ---------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    ["[1]", "[[1, 2, 3]]", "[]", "1", "null", '"x"'],
)
def test_json_that_is_not_an_object_is_not_an_anchor_or_a_pin(value):
    assert A.read_anchor(value, "sha1") is None
    assert A.read_pins(["pins:", f"  - {value}"], "sha1") is None
    rec = f"---\nanchor: {value}\nkind: comment\nstatus: open\n---\n"
    got = run({"doc.md": doc(ALPHA), R: rec})["records"][R]
    assert got["status"] == "REFUSED(record-inconsistent)"


def test_a_leaf_that_is_an_array_is_inconsistent():
    line = A.write_anchor(make_anchor(doc(SCRAM), SCRAM, "4.2 sigma"))
    start = line.index('{"type"')
    broken = line[:start] + "[1]" + line[line.index("}", start) + 1 :]
    assert A.read_anchor(broken, "sha1") is None


def test_link_text_holding_a_link_is_no_link():
    # CommonMark 0.31.2, example 518: the inner link wins.
    nested = '[a [b](c.md) d](policy.md#scram "transclude")'
    tree = {"policy.md": TARGET, "guide.md": referrer(nested, blob=oid(TARGET))}
    assert transclude(tree) == []
    # Brackets that are not a link leave the outer link standing.
    plain = '[a [b] (c d) e](policy.md#scram "transclude")'
    tree = {"policy.md": TARGET, "guide.md": referrer(plain, blob=oid(TARGET))}
    assert transclude(tree, [TARGET])[0]["status"] == "RESOLVED"


def test_a_self_transclusion_behind_an_undecided_paragraph_is_found():
    back = '[Back](guide.md#me "transclude")'
    undecided = "[X](policy.md#scram 'transclude')"
    tree = {
        "policy.md": referrer(
            "<!-- #scram -->\n" + SCRAM, undecided, back, path="guide.md", blob="0" * 40
        ),
        "guide.md": referrer("<!-- #me -->\n" + ALPHA, LINK, blob=oid(TARGET)),
    }
    assert "transcludes itself" in transclude(tree)[0]["question"]


def test_a_moved_leaf_stays_out_of_its_gap_for_the_lcs():
    """Leaving the MOVED leaf in the current gap would let the LCS skip the
    first twin and pair the second, swapping the two outcomes."""
    moved, one, twin, two = SCRAM, ALPHA, BRAVO, CHARLIE
    base = doc(moved, one, twin, twin, two)
    current = doc(one, moved, twin, two)
    assert resolve_one(base, current, twin, "coolant", nth=0)["status"] == "REFUSED(repeat)"
    got = resolve_one(base, current, twin, "coolant", nth=1)
    assert got["status"] == "REFUSED(unaccounted-copy)"


@pytest.mark.parametrize(
    "paragraph",
    [
        '![Scram](policy.md#scram "transclude")',  # an image, no link
        'Prose that says (see "transclude") with no link.',
        '[Scram](policy.md#scram "&#116ransclude")',  # no `;`: not decoded
    ],
)
def test_shapes_commonmark_reads_as_no_transclusion(paragraph):
    tree = {"policy.md": TARGET, "guide.md": referrer(paragraph, blob=oid(TARGET))}
    assert transclude(tree) == []


def test_a_title_may_be_followed_by_a_line_ending():
    link = '[Scram](policy.md#scram "transclude"\n)'
    tree = {"policy.md": TARGET, "guide.md": referrer(link, blob=oid(TARGET))}
    assert transclude(tree, [TARGET])[0]["status"] == "RESOLVED"


# --- the third addendum ------------------------------------------------------


def test_overlapping_hits_are_two_and_ambiguous():
    base_leaf = "Za" * 33  # the triple is the whole leaf, so it occurs once
    base = doc(ALPHA, base_leaf, BRAVO)
    anchor = A.Anchor(
        oid(base), "p", 0, base_leaf, base_leaf[32:34], base_leaf[:32], base_leaf[34:], None
    )
    current = doc(ALPHA, "Za" * 34, BRAVO)  # the triple starts at 0 and at 2
    got = run({"doc.md": current, R: record(anchor)}, blobs=[base])["records"][R]
    assert got["status"] == "REFUSED(span-ambiguous)"


def test_a_reply_goes_through_its_documents_checks():
    reply = '---\nreply-to: "01J9Z3M8Q4X7V2K6T0R5N1B8CD"\nkind: comment\n---\n\nAgreed.\n'
    got = run({R2: reply}, records=[R2])["records"][R2]
    assert got["status"] == "REFUSED(document-missing)"
    got = run({"doc.md": "Title\n=====\n", R2: reply}, records=[R2])["records"][R2]
    assert got["status"] == "REFUSED(not-in-profile)"
    bad = reply.replace("kind: comment", "kind: other")
    got = run({R2: bad}, records=[R2])["records"][R2]
    assert got["status"] == "REFUSED(record-inconsistent)"  # grammar first


def test_a_span_ending_with_a_code_blocks_final_line_ending_is_unmappable():
    base = "```\nlimit = 4.2\n```\n"
    stale = {"gate": "stale", "reason": "unmappable-offset"}
    for replace in ("5.0", "5.0\n"):
        got = suggest(base, base, "limit = 4.2\n", "4.2\n", replace, kind="code")
        assert got["suggestion"] == stale, replace
    got = suggest(base, base, "limit = 4.2\n", "4.2", "5.0", kind="code")
    assert got["suggestion"]["gate"] == "apply"


def test_a_fences_own_indentation_leaves_tab_spaces_that_do_not_map():
    base = "  ```\nx = 1\n\tfoo = 2\n  ```\n"
    text = "x = 1\n  foo = 2\n"
    stale = {"gate": "stale", "reason": "unmappable-offset"}
    assert suggest(base, base, text, " foo", "bar", kind="code")["suggestion"] == stale
    # Ending right before the leftover spaces: the span ends with a line ending.
    assert suggest(base, base, text, "1\n", "1;", kind="code")["suggestion"] == stale
    got = suggest(base, base, text, "foo", "bar", kind="code")
    assert got["suggestion"] == {"gate": "apply", "written": base.replace("foo", "bar")}
