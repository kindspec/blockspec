def d(*bl):
    return "\n\n".join(bl) + "\n"


L1, L2 = "Failed jobs are retried three times", "before an alert is raised."
EXP = "Exports are written to the archive bucket nightly."
ST = "Status: this proposal was approved by TOC vote on 2026-03-04."
NP = "> **Note:** All times on this page are UTC."
W = "Windows open at 02:00 and close at 04:00 on Sundays."
W2 = "Windows open at 03:00 and close at 05:00 on Sundays."
EM = "Emergency windows may open at any time with one hour's notice."
F = "Freezes begin at 18:00 on the last Friday of each quarter."

PLANTS = {
    "P-A": (d("## Ingest service", L1 + "\n" + L2, "## Export service", EXP),
            d("## Defaults", L1 + "\n" + L2, "## Ingest service", L1.replace("three", "five") + "\n" + L2,
              "## Export service", EXP), 1),
    "P-B": (d("## Project Alpha", "Alpha moves sandbox telemetry into the shared pipeline.", ST,
              "## Project Beta", "Beta adds a conformance badge to the landscape.", ST),
            d("## Project Alpha", "Alpha was rescoped to cover only audit logs.", ST,
              "## Project Beta", "Beta moves sandbox telemetry into the shared pipeline.", ST), 2),
    "P-C": (d("## Maintenance windows", NP, W, EM, "## Release freezes", NP, F),
            d("## Sunday windows", NP, W2, "## Maintenance windows", NP, EM, "## Release freezes", NP, F), 1),
    "P-C-W": (d("## Maintenance windows", NP, W, EM, "## Release freezes", NP, F),
              d("## Sunday windows", NP, W, "## Maintenance windows", NP, EM, "## Release freezes", NP, F), 1),
}
