from datetime import datetime

# Define your time and date strings
time_str = "14:30"
date_str = "Wed 10 Apr"

# Get the current year
current_year = datetime.now().year

# Convert the date string to a datetime object
date_obj = datetime.strptime(date_str, "%a %d %b")

# Extract the time components
time_components = time_str.split(':')

# Combine them with the date and current year
combined_datetime = date_obj.replace(year=current_year, hour=int(time_components[0]), minute=int(time_components[1]))
print(combined_datetime)

# Get the current datetime
current_datetime = datetime.now()
print(current_datetime)

# Calculate the difference
time_difference = combined_datetime - current_datetime

print("Time difference:", time_difference)
