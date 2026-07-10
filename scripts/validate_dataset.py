import json
for f in ["dataset/train.json","dataset/validation.json","dataset/test.json"]:
    with open(f) as fh:
        json.load(fh)
print("Dataset valid.")
