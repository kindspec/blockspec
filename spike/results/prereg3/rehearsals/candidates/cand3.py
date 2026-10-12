def d(*bl):
    return "\n\n".join(bl) + "\n"


S1, S2 = "Snapshots are kept for seven days", "before they are pruned."
RS = "Restores are verified against a checksum manifest."
U1, U2 = "Each project may store up to 50 GB", "of build artifacts at a time."
DL = "Downloads are rate-limited to 100 requests per minute."

PLANTS = {
    # P-D: positive control for q3 ("yes"): the misplaced copy is labelled superseded.
    "D1": (d("## Backup service", S1 + "\n" + S2, "## Restore service", RS),
           d("## Backup service", S1.replace("seven", "thirty") + "\n" + S2, "## Restore service", RS,
             "## Change log", "Superseded Backup wording, kept for the change log:", S1 + "\n" + S2), 1),
    # P-E: positive control for q4 ("yes"): a duplicated section left behind by an edit.
    "E1": (d("## Upload limits", U1 + "\n" + U2, "## Download limits", DL),
           d("## Upload limits", U1.replace("50", "80") + "\n" + U2, "## Download limits", DL,
             "## Upload limits", U1 + "\n" + U2), 1),
    "E2": (d("## Upload limits", U1 + "\n" + U2, "## Download limits", DL),
           d("## Upload limits", U1.replace("50", "80") + "\n" + U2, "## Download limits", DL,
             U1 + "\n" + U2), 1),
}
