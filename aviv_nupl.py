import json
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd

# Fetch the webpage
url = "https://charts.checkonchain.com/btconchain/cointime/cointime_pricing_mvrv_nupl/cointime_pricing_mvrv_nupl_light.html"
raw = requests.get(url)
soup = bs(raw.text, "lxml")

# Find the <script> tag containing the Plotly data
raw_data = soup.find_all("script")[2]
string_data = str(raw_data).replace("\\", "")

# Find the start of the JSON-like structure by looking for 'Plotly.newPlot('
start_index = string_data.find('Plotly.newPlot(')
if start_index != -1:
    # Find the start of the data array by looking for the first '[' after 'Plotly.newPlot('
    start_index = string_data.find('[', start_index)
    # Find the end of the data array by looking for the matching ']' bracket
    end_index = start_index
    bracket_count = 1
    while end_index < len(string_data) and bracket_count > 0:
        end_index += 1
        if string_data[end_index] == '[':
            bracket_count += 1
        elif string_data[end_index] == ']':
            bracket_count -= 1

    # Extract the JSON-like string and convert it to a Python object
    if end_index < len(string_data):
        data_json_string = string_data[start_index:end_index+1]
        try:
            data = json.loads(data_json_string)

        except json.JSONDecodeError as e:
            print("JSON decode error:", e)
    else:
        print("Could not find the end of the data array.")
else:
    print("Could not find 'Plotly.newPlot(' in the script content.")

# Initialize an empty dictionary to store the dataframes
dataframes = {}

# Iterate over each trace in the data
for trace in data:
    if 'x' in trace and 'y' in trace:
        # Convert 'x' data to datetime and 'y' data to float, coercing errors to NaN
        df = pd.DataFrame({
            'Date': pd.to_datetime(trace['x']),
            'Value': pd.to_numeric(trace['y'], errors='coerce')
        }).set_index('Date')

        # Use the trace name as the key in the dictionary of dataframes
        trace_name = trace.get('name', 'Unnamed Trace')
        dataframes[trace_name] = df

# Now you have a dictionary of dataframes with datetime index and float values    

# Create a new DataFrame for the combined data
combined_df = pd.DataFrame(index=dataframes['Price'].index)
# combined_df.index = combined_df.index.strftime('%Y-%m-%d')

# Add the 'Y' data from each trace as a separate column in the combined DataFrame
combined_df['BTC Price'] = dataframes['Price']['Value']
combined_df['True Market Mean'] = dataframes['True Market Mean']['Value']
combined_df['AVIV NUPL'] = dataframes['AVIV NUPL']['Value']

df = combined_df.copy()

def aviv_nupl_df():
    return df