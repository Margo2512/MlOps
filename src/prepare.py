import json

p = json.load(open("params.json"))["prepare"]
nums = [int(x) for x in open("data/raw.csv")]
kept = [n for n in nums if n >= p["min_value"]]
open("data/clean.csv", "w").write("\n".join(map(str, kept)) + "\n")
