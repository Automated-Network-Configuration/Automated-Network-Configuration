import csv

# Input and output file paths
input_file = "names.txt"
output_file = "gatelesis_emails.csv"

# Function to convert full name to email
def name_to_email(full_name):
    parts = full_name.strip().split()
    if len(parts) < 2:
        return None  # Skip invalid lines
    first_initial = parts[0][0].lower()
    last_name = parts[-1].lower()
    return f"{first_initial}{last_name}@gatelesis.com"

# Read names and generate emails
emails = []
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        email = name_to_email(line)
        if email:
            emails.append([email])

# Write emails to CSV
with open(output_file, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Email"])
    writer.writerows(emails)

print(f"Emails written to '{output_file}'")
