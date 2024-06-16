tokens = ["0", "1"]
rules = [
    ["00", "1"],
    ["01", "1"],
    ["10", "1"],
    ["11", "0"]
]

seq = "00"

steps = 100

for i in range(steps):
    for rule in rules:
        if seq[-2:] == rule[0]:
            seq += rule[1]
            break

print(seq)