n=6
for i in $(seq 1 $n); do
  python3 main.py --ip 127.0.0.1 --port $((5000 + i)) --uuid $i --file connections.json &
done
