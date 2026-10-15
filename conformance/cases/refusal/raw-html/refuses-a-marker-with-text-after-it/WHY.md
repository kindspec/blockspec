0001, What draft 0 carries: `<!-- #name -->` "on its own line" is a
marker. Here text follows it on the line, so it is not a marker. The line
still opens an HTML block (CommonMark 0.31.2 §4.6, type 2, which ends on
the line holding `-->`), and 0001 refuses raw HTML other than the
markers.
