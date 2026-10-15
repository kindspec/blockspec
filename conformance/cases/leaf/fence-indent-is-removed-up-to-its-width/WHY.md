CommonMark 0.31.2 §4.5: "If the leading code fence is preceded by N
spaces of indentation, then up to N spaces of indentation are removed from
each line of the content (if present). (If a content line is not
indented, it is preserved unchanged. If it is indented N spaces or less,
all of the indentation is removed.)" The fence is indented one space, so
each content line loses at most one.
