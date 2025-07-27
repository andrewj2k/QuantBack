# Read full file and remove the 4th line (index 3)
with open("data/SPY.csv", "r") as f:
    lines = f.readlines()

# Remove the SPY label row (3rd index = line 4)
del lines[3]

# Save cleaned file
with open("data/SPY_clean.csv", "w") as f:
    f.writelines(lines)