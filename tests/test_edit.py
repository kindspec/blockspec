# SPDX-License-Identifier: Apache-2.0 OR MIT
"""What `tests/edit-cases/` leaves out: a `TypeError`, which its format has
no field for, inserting into an empty file, which its author left open, and
the refusal class."""

import pytest
from blockspec import Refusal, edit


def test_an_empty_file_takes_an_lf_line():
    assert edit.insert_block("", "A.") == "A.\n"
    assert edit.insert_block("", "A.\r\n") == "A.\n"


def test_an_unchanged_replacement_returns_the_text():
    text = "A.\r\n\r\nB.\n"
    assert edit.replace_block(text, [0], "A.\n") is text


@pytest.mark.parametrize(
    "call",
    [
        lambda: edit.replace_block(b"A.\n", [0], "B."),
        lambda: edit.replace_block("A.\n", [0], None),
        lambda: edit.replace_block("A.\n", 0, "B."),
        lambda: edit.delete_block("A.\n", [True]),
        lambda: edit.insert_block("A.\n", "B.", after="0"),
        lambda: edit.insert_block("A.\n", "B.", before=[0.0]),
    ],
)
def test_a_wrong_type_is_a_type_error_not_a_refusal(call):
    with pytest.raises(TypeError):
        call()


def test_an_api_refusal_is_a_refusal_with_a_reason_of_its_own():
    with pytest.raises(edit.EditRefused) as caught:
        edit.delete_block("A.\n", [1])
    assert isinstance(caught.value, Refusal)
    assert caught.value.code == "no-such-block"
    assert caught.value.code in edit.REASONS


def test_a_bare_cr_before_a_kept_lf_blank_line_reads_as_one_crlf():
    # editing-api.md, delete_block: no bytes hold a bare CR and then an empty
    # LF line, so that blank line is lost; no block changes
    assert edit.delete_block("A.\r\rB.\n\n", [1]) == "A.\r\n"
