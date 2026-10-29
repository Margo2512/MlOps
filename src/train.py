import json

nums = [int(x) for x in open("data/train.csv")]
json.dump({"mean": sum(nums) / len(nums)}, open("model.json", "w"))