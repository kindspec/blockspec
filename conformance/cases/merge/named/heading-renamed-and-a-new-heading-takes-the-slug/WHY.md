# A heading renamed on one side, and the old heading text added on the other

Ours renames `# Scope` to `# Range`; theirs adds a new `# Scope` at the end.
Each alone leaves one heading with that slug. After the merge the slug `scope`
resolves to the heading theirs added, where it resolved to the first heading
at the base. Anything that used the slug follows it to new content, with no
sign. The format says so itself: slugs are not durable.

SPEC.md §8.3:

> **A heading slug is a convenience, not a reference blockspec promises to
> keep** (0001, *What draft 0 carries*).

This is one of the silently wrong merges reported with this set.
