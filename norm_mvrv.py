import json
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import streamlit as st


# Fetch the webpage
url = "https://charts.checkonchain.com/btconchain/pricing/pricing_mvrv/pricing_mvrv_light.html"
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
            # Now 'data' is a Python object, and you can extract the 'x' and 'y' values from each trace
        except json.JSONDecodeError as e:
            print("JSON decode error:", e)
    else:
        print("Could not find the end of the data array.")
else:
    print("Could not find 'Plotly.newPlot(' in the script content.")

import pandas as pd

# Assuming 'data' is the list of dictionaries you've parsed from the JSON

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

# Add the 'Y' data from each trace as a separate column in the combined DataFrame
combined_df['BTC Price'] = dataframes['Price']['Value']
combined_df['MVRV Ratio'] = dataframes['MVRV Ratio']['Value']

df = combined_df.copy()

# Convert the index to datetime if it's not already
df.index = pd.to_datetime(df.index)

# Group by day and calculate the average price
price = df['BTC Price'].resample('D').mean().to_frame('Price')

# Calculate the log base 2 of MVRV
df['mvrv'] = np.log2(df['MVRV Ratio'])

# Calculate the oversold and overbought indicators
df['row_number'] = np.arange(len(df)) + 1
df['oversold'] = np.log(df['row_number'] + 2500) - 9.35
df['overbought'] = -np.log(df['row_number'] + 2000) + 10.75

# Calculate the Adjusted_MVRV
df['Adjusted_MVRV'] = ((df['mvrv'] - df['oversold']) / (df['overbought'] - df['oversold'])) ** 1.5

# Merge the price DataFrame with the calculations on the 'day' column
# Since the index of both DataFrames is the date, we can join on the index
result = price.join(df[['Adjusted_MVRV', 'mvrv', 'oversold', 'overbought']], how='left')

# Rename the columns to match the SQL output
result.rename(columns={'mvrv': 'MVRV', 'oversold': 'Oversold', 'overbought': 'Overbought'}, inplace=True)

def get_norm_mvrv_df():
    return result

def create_norm_mvrv_plot(df):
    df = df[df.index > '2012']
    fig = go.Figure()

    # Create a subplot with 2 y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add 'BTC Price' trace with a logarithmic scale
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Price'], name='BTC Price (log scale)', line=dict(color='blue')),
        secondary_y=False,
    )

    # Add
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Adjusted_MVRV'], name='Range Adjusted MVRV', mode='lines', line=dict(color='purple')),
        secondary_y=True,
    )

    # Set x-axis title
    fig.update_xaxes(title_text='Date')

    # Set y-axes titles
    fig.update_yaxes(title_text='BTC Price (log scale)', secondary_y=False, type='log', tickcolor='blue')
    fig.update_yaxes(title_text='Range Adjusted MVRV', secondary_y=True, tickcolor='red')

    # Set the title
    fig.update_layout(height=600,
                      legend=dict(
                        orientation='h',  # Horizontal layout
                        yanchor='bottom', # Anchor legend at the bottom
                        y=1.02,           # Position legend slightly above the plot
                        xanchor='center', # Anchor legend in the center
                        x=0.5             # Center the legend horizontally
    ))

    return fig
