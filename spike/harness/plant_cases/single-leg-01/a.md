# Release runbook

Before any release, confirm that the staging cluster has fully drained,
that no long-running import jobs remain queued on either worker pool,
and that the nightly reconciliation has reported green.

Rollback is documented separately and requires two approvals from the
platform team.

## Appendix A — escalation

Page the on-call engineer if the drain takes longer than ten minutes.

## Appendix B — superseded wording

The 2019 runbook stated the pre-release check as follows, and it is kept
here for audit:

Before any release, confirm that the staging cluster has fully drained,
that no long-running import jobs remain queued on the primary worker pool,
and that the nightly reconciliation has reported green.
