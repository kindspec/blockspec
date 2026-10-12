#!/usr/bin/env bash
# Run prereg-3 plant rehearsals p3-<from>..p3-<to> one after another, each in
# its own tmux session, building each export just before its run. Stops after
# the first run in which any plant answer differs from its expectation.
#
#   drive.sh <from> <to> [label-prefix] [plants|full] [packets]
set -u
FROM=$1; TO=$2; PFX=${3:-p3}; MODE=${4:-plants}; WANT=${5:-30}
Q=<SCRATCH>/q-prereg3
D8=$Q/../q-prereg2/research/experiments/D8-identity
R=<REHEARSAL>
for i in $(seq "$FROM" "$TO"); do
  L=$PFX-$i
  python3 -I -S -B "$Q/tools/build3.py" "$MODE" "$Q/proto/spike/harness" "$D8" \
    "$Q/proto/spike/harness/prereg3_plants.py" "$R/export-486" "$R/rehearsal-key.json" \
    "$R/export-$L" "$R/export-$L-key.json" || exit 2
  tmux new-session -d -s "$L" "$R/rehearse3.sh $L 60 2>&1 | tee $R/tmux-$L.log; echo REHEARSAL-DONE >> $R/tmux-$L.log; exec bash"
  until grep -q REHEARSAL-DONE "$R/tmux-$L.log" 2>/dev/null; do sleep 15; done
  OUT=$(python3 -I -S -B "$Q/tools/plantwhy.py" "$R" "$L")
  echo "$OUT"
  if echo "$OUT" | grep -qE "MISMATCH|UNTIERED"; then echo "STOP: $L has a plant mismatch"; exit 1; fi
  if ! echo "$OUT" | grep -q " $WANT answered"; then echo "STOP: $L coverage"; exit 1; fi
done
echo "DRIVE-DONE $FROM..$TO"
