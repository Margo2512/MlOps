import json

mean = json.load(open("model.json"))["mean"]
nums = [int(x) for x in open("data/test.csv")]
mae = sum(abs(n - mean) for n in nums) / len(nums)
json.dump({"mae": round(mae, 2)}, open("metrics.json", "w"))
