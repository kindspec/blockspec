### 7.1 Tiers (table)

| tier | shape | qualifies |
|---|---|---|
| **A** | A derived or transcluded value or passage is wrong — transcluded prose that silently resolves to different content than it did before the edit | yes |
| **B** | A reference resolves silently to the wrong target, and the reference carries an assertion about that target | yes |
| **C** | A reference resolves silently to the wrong target, carrying no assertion — a bare "see also" | **no**: report, do not build on |

### 7.2 Questions, and the computed tier

For each packet the tierer answers four questions from the files alone:

1. **Assertion use.** Would a statement that is true of the oracle's target,
   about what it says or what it applies to, be false of the mechanism's
   target?
2. **Transclusion use.** Would rendering the mechanism's target in place of the
   oracle's change what the document says?
3. **Visibility (F7).** Could a reader holding only the after-file and that
   quote or name tell that the reference landed wrong?
4. **Author error (F6).** Is the mis-resolution explained by an author error
   that is visible in the file?

The tier is **computed** from the answers: A if question 2 is yes, otherwise B
if question 1 is yes, otherwise C. If the tierer cannot answer question 1 or
question 2, the packet is UNPLACEABLE, which is not a finding.

## Appendix A — the tierer's prompt, verbatim

> You are answering questions about records from an experiment. Work only with
> the files in this directory. Do not open, search for, or fetch any kindspec
> repository, issue or pull request, locally or over the network.
>
> Each packet describes one hypothetical reference — a quote anchor or a name —
> taken against a "before" file and resolved against an "after" file. It gives
> the target the mechanism resolved to and the target an independent oracle
> says is correct. They differ. Read the four questions in the packet.
>
> For every packet, answer the four questions from the files alone. If you
> cannot answer question 1 or question 2, set `"unplaceable": true` and say
> why.
>
> Write one JSON object per line to `tiers.jsonl`:
> `{"packet": <name>, "q1": "yes"|"no", "q2": "yes"|"no",
> "q3": "yes"|"no", "q4": "yes"|"no", "unplaceable": true|false,
> "why": <one line>}`.
>
> Write each line as you decide it, and do not revise a line once it is
> written. Stop when every packet has a line.
