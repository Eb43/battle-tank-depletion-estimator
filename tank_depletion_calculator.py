import csv
import matplotlib.pyplot as plt

from datetime import datetime
from datetime import timedelta

# Define the path to the CSV file
#csv_file_path = r'c:\russia_losses_equipment.csv'
print(f"--------------------------------------")
print(f"Enter the file path of the Kaggle dataset CSV file.")
print(f"Download the dataset at https://www.kaggle.com/datasets/piterfm/2022-ukraine-russian-war")
csv_file_path = input("Write the filepath to CSV file: ")
print(f"Analyzing CSV file: {csv_file_path}")
print(f" ")

# Initial number of tanks
initial_tanks = 17500
print(f"Sources determine number of tanks before FEB 2022: {initial_tanks}")

# Number of monthly tank repair rate 
#tanks_monthly_repair_rate = 15
print(f"Set tanks monthly repair rate (integer between 8 and 23). Sources determine the repair rate somewhere from 8 to 23 repaired tanks per month")
tanksmonthly_repair_rate = int(input("Monthly repair rate: "))
if 8 <= tanksmonthly_repair_rate <= 23:
    tanks_monthly_repair_rate = tanksmonthly_repair_rate
else:
    tanks_monthly_repair_rate = 15

# Initialize the datetankdata array
datetankdata = []


# Read the CSV file and process it
with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    header = next(csvreader)  # Skip the header row
    
    # Iterate through each row in the CSV file
    for row in csvreader:
        date_str = row[0]  # Get the date from the first column
        tank_count = row[4]  # Get the tank value from the 4th column
        
        # Convert the date string to a datetime object for sorting
        date = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Append the [date, tank] list to the datetankdata list
        # datetankdata [][0] is date
        # datetankdata [][1] is date in string format
        # datetankdata [][2] is number of daily sum of total tank losses
        # datetankdata [][3] is daily number of tank losses
        # datetankdata [][4] is monthly tank losses
        # datetankdata [][5] is number of days in month (dataset may contain less days for a month than calendar month)
        datetankdata.append([date, date_str, int(tank_count), int(tank_count), 0, 0])

# Sort the datetankdata by date (from oldest to most recent)
datetankdata.sort(key=lambda x: x[0])

# Initialize the monthly loss variable
monthly_loss = 0

# Initialize the variable for the number of days in the month
days_in_month = 1

total_tank_lost_for_known_dataset = 0
total_number_of_days_in_known_dataset = 1

# Calculate daily and monthly tank losses (difference between today and yesterday)
for i in range(1, len(datetankdata)):  # Start from the second row (index 1)
    daily_difference = datetankdata[i][2] - datetankdata[i - 1][2]  # Difference from previous day
    datetankdata[i][3] = daily_difference  # Assign the daily difference to the last column
    total_tank_lost_for_known_dataset = total_tank_lost_for_known_dataset + daily_difference
    total_number_of_days_in_known_dataset = total_number_of_days_in_known_dataset + 1
    
    # Check if the month is the same as the previous month
    if datetankdata[i][0].month == datetankdata[i - 1][0].month:
        # If in the same month, accumulate the monthly loss
        monthly_loss += daily_difference
        days_in_month = days_in_month + 1
    else:
        # If month changes, reset the monthly loss to the current day's difference
        monthly_loss = daily_difference
        days_in_month = 1
        
    
    # Assign the monthly loss to the new column
    datetankdata[i][4] = monthly_loss
    datetankdata[i][5] = days_in_month
    if datetankdata[i][0].month == datetankdata[i - 1][0].month:
        datetankdata[i-1][4] = 0
        datetankdata[i-1][5] = 0
            

    
datetankdata[0][3] = 0



# Fill the zero values of Days in Month (datetankdata[i][5]) with actual number of days in the dataset for the particular month

for i in range(len(datetankdata) - 1, 0, -1):  # Start from the last row
    # Check if the two consecutive rows belong to the same month
    if datetankdata[i][0].month == datetankdata[i - 1][0].month:
        # If the earlier row's monthly loss is zero, update it
        if datetankdata[i - 1][4] == 0:
            datetankdata[i - 1][4] = datetankdata[i][4]
            datetankdata[i - 1][5] = datetankdata[i][5]


# Calculating average daily rate of lost tanks 
average_daily_rate_of_lost_tanks = total_tank_lost_for_known_dataset // total_number_of_days_in_known_dataset


# Prepare data for plotting
# Create an empty list to hold date and tank count pairs
remaining_tanks = []

# Initialize the remaining tank count with the initial value
numberof_tanks = initial_tanks

# Loop through each entry in the datetankdata
for i in range(len(datetankdata)):
    # Get the current date
    current_date = datetankdata[i][0]
    
    # Subtract the daily loss from the remaining tank count, add 7 on the 15th day, and add 8 on the last day of the month
    if current_date == 15:  # Check if it's the 15th day of the month
        numberof_tanks -= datetankdata[i][3] + tanks_monthly_repair_rate //2
    elif current_date == days_in_month:  # Check if it's the last day of the month
        numberof_tanks -= datetankdata[i][3] + tanks_monthly_repair_rate // 2
    else:
        numberof_tanks -= datetankdata[i][3]

    # Append the current date and remaining tanks as a pair to the array
    remaining_tanks.append([current_date, numberof_tanks])

print(f"Daily rate of tanks lost: {average_daily_rate_of_lost_tanks}")
print(f"Remaining tanks at the end of known historical dataset timeframe: {numberof_tanks}")


# Make prediction data for dates outside of historical dataset
last_date = datetankdata[-1][0]  # Get the last date from the dataset
max_days = 365 * 1  # Set a limit of 10 years into the future to prevent overflow
days_predicted = 0  # Counter for the number of predicted days

while numberof_tanks >= 15:
    # Increment the last date by one day
    last_date += timedelta(days=1)  # New date to the dates list
    
    # Get the day of the month for the current date
    day_of_month = last_date.day
    # Get the last day of the current month
    days_in_month = (last_date.replace(day=28) + timedelta(days=4)).day - 3

    # Adjust the number of tanks based on the day of the month
    if day_of_month == 15:  # Check if it's the 15th day of the month
        numberof_tanks = numberof_tanks - average_daily_rate_of_lost_tanks + tanks_monthly_repair_rate // 2
    elif day_of_month == days_in_month:  # Check if it's the last day of the month
        numberof_tanks = numberof_tanks - average_daily_rate_of_lost_tanks + tanks_monthly_repair_rate // 2
    else:
        numberof_tanks = numberof_tanks - average_daily_rate_of_lost_tanks

    # Append the remaining tanks to the list
    remaining_tanks.append([last_date, numberof_tanks])

    # Increment the days predicted counter
    days_predicted += 1



print(f"Number of predicted days before tank stock depleted: {days_predicted}")

#for row in remaining_tanks:
#    print(f"Date: {row[0]}, Tanks: {row[1]}")

print(f"--------------------------------------")

# Extract dates and tank counts
dates = [row[0] for row in remaining_tanks]
tank_counts = [row[1] for row in remaining_tanks]

# Plotting the tank count decrease over time
plt.figure(figsize=(10, 6))

# Determine the split point
split_date = datetankdata[-1][0]

# Separate the data into two parts
dates_before = [date for date in dates if date <= split_date]
tank_counts_before = tank_counts[:len(dates_before)]

dates_after = [date for date in dates if date > split_date]
tank_counts_after = tank_counts[len(dates_before):]

# Plot the solid line for dates before or equal to the split date
plt.plot(dates_before, tank_counts_before, label='Remaining Tanks (Historical data)', color='tab:red', linestyle='-', marker='o')

# Plot the dotted line for dates after the split date
plt.plot(dates_after, tank_counts_after, label='Remaining Tanks (Prediction)', color='tab:grey', linestyle=':', marker='+')

# Add stock depleted line
plt.axhline(y=0, color='red', linestyle='--', label="Tank Stock Depleted")

# Add labels, title, and legend
plt.xlabel('Date')
plt.ylabel('Remaining Tanks')
plt.title('Tank Losses Over Time')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.legend()
plt.show()

