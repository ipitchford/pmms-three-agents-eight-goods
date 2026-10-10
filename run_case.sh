#!/bin/zsh
# usage: run_case.sh RUNDIR   -- CaDiCaL with LRAT proof streamed through gzip
set -u
d=$1
fifo=$d/proof.fifo
rm -f $fifo; mkfifo $fifo
gzip -3 < $fifo > $d/proof.lrat.gz &
gz=$!
start=$(date +%s)
cadical --lrat=true --binary=false $d/base.cnf $fifo > $d/cadical.out 2>&1
rc=$?
wait $gz
end=$(date +%s)
rm -f $fifo
echo "exit $rc elapsed $((end-start)) s" >> $d/cadical.out
grep -E "^s " $d/cadical.out
