# Release runbook

Before any release, confirm that the staging cluster has fully drained,
that no long-running import jobs remain queued on either worker pool,
and that the nightly reconciliation has reported green.

Rollback is documented separately and requires two approvals from the
platform team.

## Appendix A — escalation

Page the on-call engineer if the drain takes longer than ten minutes.
