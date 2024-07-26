import numpy as np
import pandas as pd

# Load the dataset
df = pd.read_csv('scrape_output/data0.csv')

# Replace km in mileageFromOdometer
df['mileageFromOdometer'] = df['mileageFromOdometer'].str.replace(' km', '')
df['mileageFromOdometer'] = df['mileageFromOdometer'].str.replace(',', '')
df['mileageFromOdometer'] = df['mileageFromOdometer'].str.replace(' ', '')

# Replace cc in vehicleEngine
df['vehicleEngine'] = df['vehicleEngine'].str.replace('cc', '')
df['vehicleEngine'] = df['vehicleEngine'].str.replace(' ', '')


# Drop rows with missing values
df.dropna(inplace=True)


# Drop rows with missing values in vehicleEngine
df['vehicleEngine'] = df['vehicleEngine'].replace('', np.NaN)
df = df.dropna(subset=['vehicleEngine'])

# Convert mileageFromOdometer and vehicleEngine to numeric
if df['mileageFromOdometer'].all != '':
    df['mileageFromOdometer'] = df['mileageFromOdometer'].astype(np.int64)

df['vehicleEngine'] = df['vehicleEngine'].astype(np.int64)

# save the cleaned data
df.to_csv('scrape_output/data0_clean.csv', index=False)
print("Data cleaned and saved to scrape_output/data0_clean.csv")
