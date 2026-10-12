#!/usr/bin/env bash
# Rehearse prereg 2's tier-run on a synthetic export. It is unbound and commits nothing.
# It runs the same harness code path, sandbox, PROMPT.md, model, flags and credential
# mount as the bound tier-run.
#
#   rehearse.sh 120|486 [poll-seconds]
#
# The agent is the default `claude`. `--agent-cmd` is left unset, so tierrun.agent_argv
# builds the same argv as the bound run, with the model taken from tier-model.json,
# which is a copy of the committed one. Credentials are the --credentials default,
# ~/.claude/.credentials.json, bind-mounted read-only. No API key is used.
set -u
N=${1:?usage: rehearse.sh 120|486 [poll-seconds]}
POLL=${2:-60}
ROOT=<REHEARSAL>
WT=<SCRATCH>/q-prereg2/wt-tier
H=$WT/spike/harness/prereg2.py
SC=e46e320a0245e99211aea95bd436609029436f49
EXPORT=$ROOT/export-$N
[ -d "$EXPORT/packets" ] || { echo "no export $EXPORT"; exit 2; }
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then echo "refusing: ANTHROPIC_API_KEY is set; tiering uses the subscription only"; exit 2; fi
RUN=$ROOT/run-$N-$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$RUN/state" "$RUN/transcripts"
cp "$WT/spike/results/prereg2/tier-model.json" "$RUN/state/tier-model.json"
{
  echo "start_utc $(date -u +%FT%TZ)"
  echo "export $EXPORT ($(ls "$EXPORT/packets" | wc -l) packets)"
  echo "claude $(readlink -f "$(command -v claude)") $(claude --version 2>&1)"
  echo "bwrap $(bwrap --version)"
  echo "harness $(git -C "$WT" rev-parse HEAD)"
} > "$RUN/run-info.txt"
cd /tmp || exit 1
T0=$(date +%s)
env -u GIT_EDITOR -u ANTHROPIC_API_KEY python3 -I -S -B "$H" tier-run --unbound \
  --transcript-dir "$RUN/transcripts" --state-dir "$RUN/state" --export "$EXPORT" \
  --repo "$WT/spike" --scoring-commit "$SC" > "$RUN/tier-run.out" 2>&1 &
PID=$!
echo "rehearsal $N started: run dir $RUN, pid $PID"
python3 -I -S "$ROOT/monitor.py" "$RUN" "$PID" "$ROOT/rehearsal-key.json" "$POLL" "$EXPORT" > "$RUN/monitor.out" 2>&1 &
MPID=$!
wait "$PID"; RC=$?
wait "$MPID"
T1=$(date +%s)
{ echo "end_utc $(date -u +%FT%TZ)"; echo "wall_seconds $((T1 - T0))"; echo "tier_run_exit $RC"; } >> "$RUN/run-info.txt"
cat "$RUN/run-info.txt" "$RUN/monitor.out"
echo "details: $RUN/summary.json  $RUN/tiers-poll.log  $RUN/tier-run.out  $RUN/transcripts/"
