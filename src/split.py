import json

p = json.load(open("params.json"))["split"]
nums = [int(x) for x in open("data/clean.csv")]
cut = int(len(nums) * (1 - p["test_ratio"]))
open("data/train.csv", "w").write("\n".join(map(str, nums[:cut])) + "\n")
open("data/test.csv", "w").write("\n".join(map(str, nums[cut:])) + "\n")
