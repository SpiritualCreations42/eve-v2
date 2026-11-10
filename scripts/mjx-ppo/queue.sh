#!/bin/bash
# usage: queue.sh GPU  "TAG:ASCALE:SEED:YW:YPW" ...
cd ~/ai-envs; source mjx/bin/activate
G=$1; shift
for cfg in "$@"; do
  IFS=: read TAG AS SEED YW YPW <<< "$cfg"
  [ -f STOP ] && break
  echo "$(date +%H:%M) start $TAG" >> queue_gpu$G.log
  CUDA_VISIBLE_DEVICES=$G XLA_PYTHON_CLIENT_PREALLOCATE=false XML=aurora.xml MASS=1.16 TAG=$TAG ASCALE=$AS SEED=$SEED YAW_W=$YW Y_W=$YPW NENV=4096 T=20 UPDATES=2400 python ppo_aurora.py > out_$TAG.txt 2>&1
  echo "$(date +%H:%M) done $TAG, eval:" >> queue_gpu$G.log
  python eval_cpu.py $TAG $AS aurora.xml >> queue_gpu$G.log 2>&1
done
echo "$(date +%H:%M) queue finished" >> queue_gpu$G.log
