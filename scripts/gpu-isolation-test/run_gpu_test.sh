#!/usr/bin/env bash
# Standalone GPU test, no ComfyUI. Run on EvE:  ~/gputest/run_gpu_test.sh [long]
# Stops at the first Xid error. Logs in $HOME/gputest-logs/latest/
set -u
cd "$(dirname "$0")"
OUT=$HOME/gputest-logs/gputest-$(date +%Y%m%d-%H%M%S)
mkdir -p "$OUT"
ln -sfn "$OUT" $HOME/gputest-logs/latest
LONG=${1:-}
SUM="$OUT/summary.txt"
xids() { sudo -n dmesg | grep -c 'NVRM: Xid'; }
rxerr() { sudo -n dmesg | grep -c 'RxErr'; }
BASE_X=$(xids)
echo "start $(date)  baseline xid=$BASE_X rxerr=$(rxerr)" | tee -a "$SUM"
docker stop comfyui > /dev/null 2>&1 || true   # keep ComfyUI out of the picture
sudo -n dmesg > "$OUT/dmesg_before.txt"
nvidia-smi --query-gpu=timestamp,index,temperature.gpu,power.draw,utilization.gpu,memory.used,clocks.sm,pcie.link.gen.current,pcie.link.width.current,clocks_throttle_reasons.active --format=csv -l 1 > "$OUT/gpu.csv" 2>&1 &
LOGGER=$!
trap 'kill $LOGGER 2>/dev/null' EXIT

run() {  # phase secs gpu...
  local phase=$1 secs=$2; shift 2
  echo "=== phase=$phase gpus=$* secs=$secs  $(date +%T)" | tee -a "$SUM"
  local pids=() rc=0
  for g in "$@"; do
    timeout $((secs * 12 + 120)) docker compose run --rm -T --name "gpuload-$g" gpu-load --gpu "$g" --phase "$phase" --secs "$secs" >> "$OUT/load_gpu$g.log" 2>&1 &
    pids+=($!)
  done
  for p in "${pids[@]}"; do wait "$p" || rc=$?; done
  for g in "$@"; do docker rm -f "gpuload-$g" > /dev/null 2>&1; done
  local x; x=$(xids)
  echo "    exit=$rc  xid=$((x - BASE_X))  rxerr_total=$(rxerr)" | tee -a "$SUM"
  if [ "$x" -gt "$BASE_X" ] || [ "$rc" -ne 0 ]; then
    echo "FAULT in phase $phase on gpus $* -- stopping" | tee -a "$SUM"
    sudo -n dmesg > "$OUT/dmesg_after.txt"
    echo "DONE (fault)" >> "$SUM"
    exit 1
  fi
}

for g in 0 1; do
  run soak 180 $g
  run steps 45 $g
  run ramp 10 $g
  run pcie 120 $g
  run mixed 180 $g
done
run p2p 120 0
run soak 300 0 1
run steps 45 0 1
run mixed 300 0 1
if [ "$LONG" = "long" ]; then run mixed 2400 0 1; fi
sudo -n dmesg > "$OUT/dmesg_after.txt"
echo "DONE (no fault)  $(date)" | tee -a "$SUM"
