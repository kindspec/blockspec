def d(*bl):
    return "\n\n".join(bl) + "\n"


L1, L2 = "Failed jobs are retried three times", "before an alert is raised."
EXP = "Exports are written to the archive bucket nightly."
ST = "Status: this proposal was approved by TOC vote on 2026-03-04."
H = "## Maintenance windows"
N = "> **Note:** All times in this section are UTC."
W = "Windows open at 02:00 and close at 04:00 on Sundays."
W2 = "Windows open at 03:00 and close at 05:00 on Sundays."
E = "Emergency windows may open at any time with one hour's notice."
NP = "> **Note:** All times on this page are UTC."
F = "Freezes begin at 18:00 on the last Friday of each quarter."

PLANTS = {
    # prereg 2's Appendix B, as a control
    "P2-A": (d("## Ingest service", L1 + "\n" + L2, "## Export service", EXP),
             d("## Ingest service", L1.replace("three", "five") + "\n" + L2,
               "## Export service", EXP, "## Audit trail",
               "Superseded Ingest wording, kept for audit:", L1 + "\n" + L2), 1),
    "P2-B": (d("## Project Alpha", "Alpha moves sandbox telemetry into the shared pipeline.", ST,
               "## Project Beta", "Beta adds a conformance badge to the landscape.", ST),
             d("## Project Alpha", "Alpha was rescoped to cover only audit logs.", ST,
               "## Project Beta", "Beta moves sandbox telemetry into the shared pipeline.", ST), 2),
    "P2-C": (d(H, N, W, E, N), d(H, E, N, W2, N), 4),
    # candidate A: the old wording becomes the stated default
    "A1": (d("## Ingest service", L1 + "\n" + L2, "## Export service", EXP),
           d("## Defaults", L1 + "\n" + L2, "## Ingest service", L1.replace("three", "five") + "\n" + L2,
             "## Export service", EXP), 1),
    # candidate A, variant: the old wording moves to Export
    "A2": (d("## Ingest service", L1 + "\n" + L2, "## Export service", EXP),
           d("## Ingest service", L1.replace("three", "five") + "\n" + L2,
             "## Export service", EXP, L1 + "\n" + L2), 1),
    # candidate C: a page-wide note opens every section
    "C1": (d(H, NP, W, E, "## Release freezes", NP, F),
           d(H, NP, E, "## Sunday windows", NP, W2, "## Release freezes", NP, F), 1),
    "C2": (d(H, NP, W, E, "## Release freezes", NP, F),
           d(H, NP, E, "## Sunday windows", NP, W2, "## Release freezes", NP, F), 5),
    "C3": (d(H, NP, W, E, NP), d(H, NP, E, NP, W2), 4),
}
