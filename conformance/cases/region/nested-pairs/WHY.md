0001: a region may nest. READING: a region is every sibling node strictly
between its two markers, and that includes another region's markers. 0002
says "the sibling nodes between the two markers" and makes no exception for
markers, so `outer` holds `inner`'s two markers as well as the three
paragraphs.
