You are answering questions about records from an experiment. Work only with
the files in this directory. Do not open, search for, or fetch any kindspec
repository, issue or pull request, locally or over the network.

Each packet describes one hypothetical reference — a quote anchor or a name —
taken against a "before" file and resolved against an "after" file. It gives
the target the mechanism resolved to and the target an independent oracle
says is correct. They differ. Read the four questions in the packet.

For every packet, answer the four questions from the files alone. If you
cannot answer question 1 or question 2, set `"unplaceable": true` and say
why.

Write one JSON object per line to `tiers.jsonl`:
`{"packet": <name>, "q1": "yes"|"no", "q2": "yes"|"no",
"q3": "yes"|"no", "q4": "yes"|"no", "unplaceable": true|false,
"why": <one line>}`.

Write each line as you decide it, and do not revise a line once it is
written. Stop when every packet has a line.
