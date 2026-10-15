CommonMark 0.31.2 §2.2: where spaces define block structure, a tab
behaves as if replaced by spaces with a tab stop of 4. The tab on line 3
reaches column 4, past the item's content column of 2, so `b` is a
second paragraph in the item, and the 2 columns left over are not enough
for indented code. §2.2's example `- foo` / blank / two tabs `bar` has
one more tab and makes indented code; with one tab it is a paragraph.
