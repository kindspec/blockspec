def d(*bl):
    return "\n\n".join(bl) + "\n"


ST = "Status: this proposal was approved by TOC vote on 2026-03-04."
RV = "Status: this proposal is under review."
PLANTS = {
    # P-B variant: the status line is unique in the before-file, so the
    # reference's origin is unambiguous; the edit approves Beta with the same line.
    "B2": (d("## Project Alpha", "Alpha moves sandbox telemetry into the shared pipeline.", ST,
             "## Project Beta", "Beta adds a conformance badge to the landscape.", RV),
           d("## Project Alpha", "Alpha was rescoped to cover only audit logs.", ST,
             "## Project Beta", "Beta moves sandbox telemetry into the shared pipeline.", ST), 2),
}
