Control: the addendum's GitHub reading "trims form feeds and vertical tabs
from cells as well as spaces and tabs", and no other character. A
no-break space is none of these, so `---` and a no-break space is no
delimiter row to any of the three readers, and it is not a setext
underline or a thematic break either (CommonMark 0.31.2 §4.3, §4.1, §2.1).
The two lines are one paragraph, the no-break space kept. pandoc 3.1.11.1
(`-f gfm`) and markdown-it-py 3.0.0 read one paragraph.
