#!/usr/bin/env bash
# V6 driver: rehearse the bound harness3 tier-run (prereg3.py tier-run
# --unbound) on synthetic exports, one run at a time, each in its own tmux
# session. Logs the credential file's mtime (stat only) before and after each
# run. An authentication abort is logged and the run is repeated under a new
# label; any other failure stops the series.
#
#   drive_v6.sh <size 30|full> <count> <label prefix>
set -u
SIZE=$1; COUNT=$2; PFX=$3
REPO=<HOME>/repos_kindspec/blockspec
H3=$REPO/spike/harness3
D8=<SCRATCH>/q-prereg2/research/experiments/D8-identity
SRC=<REHEARSAL>
OUT=${V6_OUT:?set V6_OUT}
CRED=$HOME/.claude/.credentials.json
mkdir -p "$OUT"
cmt() { echo "$(date -u +%FT%TZ) credential mtime $(date -u -d @"$(stat -c %Y "$CRED")" +%FT%TZ) ($1)"; }
[ -d "$OUT/gate" ] || python3 -I -S -B "$H3/prereg3_v6.py" gate --out "$OUT/gate" || exit 2
i=1; tries=0
# No full-size run starts within an hour of a predicted credential renewal
# (00:45Z and 08:45Z): it waits until the window has passed.
blocked() { local m=$((10#$(date -u +%H) * 60 + 10#$(date -u +%M)));   { [ $m -ge $((23*60+45)) ] || [ $m -lt $((1*60+45)) ]; } || { [ $m -ge $((7*60+45)) ] && [ $m -lt $((9*60+45)) ]; }; }
while [ "$i" -le "$COUNT" ]; do
  if [ "$SIZE" = full ]; then
    while blocked; do echo "$(date -u +%FT%TZ) waiting: within an hour of a predicted credential renewal"; sleep 300; done
  fi
  tries=$((tries + 1))
  L=$PFX-$i; [ "$tries" -gt "$i" ] && L=$PFX-$i-r$((tries - i))
  D=$OUT/$L
  python3 -I -S -B "$H3/prereg3_v6.py" build --d8-dir "$D8" --source "$SRC/export-486" \
    --source-key "$SRC/rehearsal-key.json" --size "$SIZE" --out "$D/export" --key-out "$D/key.json" || exit 2
  echo "harness HEAD $(git -C "$REPO" rev-parse HEAD); harness3 uncommitted files: $(git -C "$REPO" status --porcelain -- spike/harness3 | wc -l)" > "$D/run-info.txt"
  cmt "before $L" | tee -a "$D/run-info.txt"
  env | grep -q '^ANTHROPIC_API_KEY=' && { echo "refusing: ANTHROPIC_API_KEY is set"; exit 2; }
  tmux new-session -d -s "v6-$(basename "$OUT")-$L" "cd /tmp && env -u ANTHROPIC_API_KEY python3 -I -S -B $H3/prereg3.py tier-run --unbound --transcript-dir $D/transcripts --state-dir $D/state --export $D/export --gate-repo $OUT/gate/spike > $D/tier-run.out 2>&1; echo V6-DONE >> $D/tier-run.out; exec bash"
  until grep -q V6-DONE "$D/tier-run.out" 2>/dev/null; do sleep 15; done
  cmt "after $L" | tee -a "$D/run-info.txt"
  python3 -I -S -B "$H3/prereg3_v6.py" check --state "$D/state" --export "$D/export" --key "$D/key.json" \
    --transcript "$(ls "$D"/transcripts/*.txt | head -1)" > "$D/check.txt" 2>&1
  rc=$?
  cat "$D/check.txt"
  if [ $rc -eq 3 ]; then echo "AUTH ABORT: $L (environment fault); repeating run $i"; continue; fi
  if [ $rc -ne 0 ]; then echo "STOP: $L failed the bar"; exit 1; fi
  i=$((i + 1))
done
echo "V6-SERIES-DONE $PFX $SIZE $COUNT"
