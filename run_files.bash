n=6
for i in $(seq 1 $n); do
  python3 main.py --port $((5000 + i)) --uuid $i --file connections.json &
done
