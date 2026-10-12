#!/usr/bin/env bash
# Full-size bar 2' restart (p3i). drive3.sh with three changes:
#  - before and after each run it logs the credential file's mtime, from
#    `stat -c %Y` only (the file's contents are never read);
#  - a run whose transcript shows an authentication failure (HTTP 401/403 or
#    "Failed to authenticate") stops the series: an environment abort;
#  - a run with a wrong plant answer is logged as FAIL but the series goes on,
#    because the bar names all three runs.
#
#   drive4.sh <from> <to> <label-prefix> <packets>
set -u
FROM=$1; TO=$2; PFX=$3; WANT=$4
Q=<SCRATCH>/q-prereg3
D8=$Q/../q-prereg2/research/experiments/D8-identity
R=<REHEARSAL>
CRED=$HOME/.claude/.credentials.json
cmt() { echo "$(date -u +%FT%TZ) credential mtime $(date -u -d @"$(stat -c %Y "$CRED")" +%FT%TZ) ($1)"; }
for i in $(seq "$FROM" "$TO"); do
  L=$PFX-$i
  python3 -I -S -B "$Q/tools/build3.py" full "$Q/proto/spike/harness" "$D8" \
    "$Q/proto/spike/harness/prereg3_plants.py" "$R/export-486" "$R/rehearsal-key.json" \
    "$R/export-$L" "$R/export-$L-key.json" || exit 2
  cmt "before $L"
  tmux new-session -d -s "$L" "$R/rehearse3.sh $L 60 2>&1 | tee $R/tmux-$L.log; echo REHEARSAL-DONE >> $R/tmux-$L.log; exec bash"
  until grep -q REHEARSAL-DONE "$R/tmux-$L.log" 2>/dev/null; do sleep 15; done
  cmt "after $L"
  RUN=$(ls -d "$R"/run-"$L"-2* | tail -1)
  if grep -qE '"error_status":(401|403)|Failed to authenticate' "$RUN"/transcripts/*.txt; then
    echo "STOP: $L ended on an authentication error (environment abort)"; exit 3
  fi
  OUT=$(python3 -I -S -B "$Q/tools/plantwhy.py" "$R" "$L")
  echo "$OUT"
  if echo "$OUT" | grep -qE "MISMATCH|UNTIERED"; then echo "FAIL: $L has a plant mismatch"; fi
  if ! echo "$OUT" | grep -q " $WANT answered"; then echo "FAIL: $L coverage"; fi
done
echo "DRIVE-DONE $FROM..$TO"
