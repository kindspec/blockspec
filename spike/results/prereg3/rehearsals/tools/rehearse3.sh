#!/usr/bin/env bash
# Rehearse the prereg-3 tier-run on a synthetic export. Unbound; commits nothing.
#
# This is rehearse.sh with three changes, and no others:
#   1. H is the PROTOTYPE harness (a scratch copy of wt-tier's spike/harness with
#      the PACKETS.txt manifest, prereg 3's Appendix A and the candidate plants).
#      The bound harness in wt-tier cannot run an export that holds PACKETS.txt:
#      its validator refuses any root file but PROMPT.md and packets/.
#   2. The monitor's key is the export's own key file, export-<label>-key.json,
#      when it exists, else rehearsal-key.json as before.
#   3. run-info.txt also records the prototype harness's tree hash.
# Same tier-run code path otherwise: same sandbox, model (tier-model.json copy),
# argv, credential mount, and no API key.
#
#   rehearse3.sh <label> [poll-seconds]      (export: export-<label>)
set -u
N=${1:?usage: rehearse3.sh <label> [poll-seconds]}
POLL=${2:-60}
ROOT=<REHEARSAL>
WT=<SCRATCH>/q-prereg2/wt-tier
PROTO=<SCRATCH>/q-prereg3/proto/spike
H=$PROTO/harness/prereg2.py
SC=e46e320a0245e99211aea95bd436609029436f49
EXPORT=$ROOT/export-$N
KEY=$ROOT/export-$N-key.json
[ -f "$KEY" ] || KEY=$ROOT/rehearsal-key.json
[ -d "$EXPORT/packets" ] || { echo "no export $EXPORT"; exit 2; }
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then echo "refusing: ANTHROPIC_API_KEY is set; tiering uses the subscription only"; exit 2; fi
RUN=$ROOT/run-$N-$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$RUN/state" "$RUN/transcripts"
cp "$WT/spike/results/prereg2/tier-model.json" "$RUN/state/tier-model.json"
{
  echo "start_utc $(date -u +%FT%TZ)"
  echo "export $EXPORT ($(ls "$EXPORT/packets" | wc -l) packets)"
  echo "key $KEY"
  echo "claude $(readlink -f "$(command -v claude)") $(claude --version 2>&1)"
  echo "bwrap $(bwrap --version)"
  echo "harness PROTOTYPE $PROTO (tree sha256 $(cd "$PROTO" && find harness PRE-REGISTRATION-3.md -type f ! -path '*__pycache__*' -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -c1-16)); bound harness $(git -C "$WT" rev-parse HEAD)"
  echo "prompt_sha256 $(sha256sum "$EXPORT/PROMPT.md" | cut -c1-64)"
} > "$RUN/run-info.txt"
cd /tmp || exit 1
T0=$(date +%s)
env -u GIT_EDITOR -u ANTHROPIC_API_KEY python3 -I -S -B "$H" tier-run --unbound \
  --transcript-dir "$RUN/transcripts" --state-dir "$RUN/state" --export "$EXPORT" \
  --repo "$WT/spike" --scoring-commit "$SC" > "$RUN/tier-run.out" 2>&1 &
PID=$!
echo "rehearsal $N started: run dir $RUN, pid $PID"
python3 -I -S "$ROOT/monitor.py" "$RUN" "$PID" "$KEY" "$POLL" "$EXPORT" > "$RUN/monitor.out" 2>&1 &
MPID=$!
wait "$PID"; RC=$?
wait "$MPID"
T1=$(date +%s)
{ echo "end_utc $(date -u +%FT%TZ)"; echo "wall_seconds $((T1 - T0))"; echo "tier_run_exit $RC"; } >> "$RUN/run-info.txt"
cat "$RUN/run-info.txt" "$RUN/monitor.out"
echo "details: $RUN/summary.json  $RUN/tiers-poll.log  $RUN/tier-run.out  $RUN/transcripts/"
