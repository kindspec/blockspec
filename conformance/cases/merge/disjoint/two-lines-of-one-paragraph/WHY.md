# Two branches edit different lines of one paragraph

The paragraph's first and last lines change on different branches, and the
unchanged middle line keeps them apart. Stock git merges them, and the merged
paragraph is a text neither side wrote. 0003 §8 lists exactly this:

> | two branches edit different lines of the anchored leaf and merge cleanly | as the edit of the merged text | as the edit of the merged text | resolves |

SPEC.md §6.3 gives the leaf's content with `\n` line endings.
