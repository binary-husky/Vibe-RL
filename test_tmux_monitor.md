
login
ssh root@localhost -p 8824
goto
/mnt/data_cpfs/qingxu.fu/agentjet/good-luck-agentjet
run with venv and monitor
source .venv/bin/activate && python -m ajet.launcher --conf tests/bench/benchmark_math/benchmark_math.yaml --autokill
