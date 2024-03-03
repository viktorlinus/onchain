import json
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import streamlit as st

# Fetch the webpage
url = "https://checkonchain.com/btconchain/pricing/pricing_sthmvrvindicator/pricing_sthmvrvindicator_light.html"
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
combined_df['STH Cost Basis'] = dataframes['STH Cost Basis']['Value']
combined_df['STH-MVRV (in Profit)'] = dataframes['STH-MVRV (in Profit)']['Value']
combined_df['STH-MVRV (in Loss)'] = dataframes['STH-MVRV (in Loss)']['Value']

combined_df['STH-MVRV Combined'] = np.where(
    combined_df['STH-MVRV (in Profit)'] == 1,
    combined_df['STH-MVRV (in Loss)'],
    np.where(
        combined_df['STH-MVRV (in Loss)'] == 1,
        combined_df['STH-MVRV (in Profit)'],
        np.nan  # or some other default value if neither condition is met
    )
)


def get_dataframe_sth_mvrv():
    return combined_df


# Filter the DataFrame to only include data from 2012 onwards
combined_df_filtered = combined_df[combined_df.index.year >= 2012]

# Calculate the expanding mean and standard deviation
expanding_mean = combined_df_filtered['STH-MVRV Combined'].expanding().mean()
expanding_std = combined_df_filtered['STH-MVRV Combined'].expanding().std()

# Calculate 'Mean + 3σ' using the expanding mean and standard deviation
combined_df_filtered['Mean + 2σ'] = expanding_mean + (expanding_std * 2)
combined_df_filtered['Mean + 2.5σ'] = expanding_mean + (expanding_std * 2.5)
combined_df_filtered['Mean - 1.25σ'] = expanding_mean + (expanding_std * -1.25)

combined_df_filtered = combined_df_filtered[combined_df_filtered.index.year >= 2015]


# Create a subplot with 2 y-axes
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add 'BTC Price' trace with a logarithmic scale
fig.add_trace(
    go.Scatter(x=combined_df_filtered.index, y=combined_df_filtered['BTC Price'], name='BTC Price', mode='lines', line=dict(color='black')),
    secondary_y=False,
)

fig.add_trace(
    go.Scatter(x=combined_df_filtered.index, y=combined_df_filtered['STH Cost Basis'], name='STH Cost Basis', mode='lines', line=dict(color='blue')),
    secondary_y=False,
)

fig.add_trace(
    go.Scatter(x=combined_df_filtered.index, y=combined_df_filtered['STH-MVRV Combined'], name='STH MVRV', mode='lines', line=dict(color='purple')),
    secondary_y=True,
)

fig.add_trace(
    go.Scatter(x=combined_df_filtered.index, y=combined_df_filtered['Mean + 2σ'], name='Mean + 2σ', mode='lines', line=dict(color='orange')),
    secondary_y=True,
)
fig.add_trace(
    go.Scatter(x=combined_df_filtered.index, y=combined_df_filtered['Mean + 2.5σ'], name='Mean + 2.5σ', mode='lines', line=dict(color='red')),
    secondary_y=True,
)

fig.add_trace(
    go.Scatter(x=combined_df_filtered.index, y=combined_df_filtered['Mean - 1.25σ'], name='Mean - 1.25σ', mode='lines', line=dict(color='green')),
    secondary_y=True,
)

# Add a horizontal line at 0 on the secondary y-axis
fig.add_hline(y=1, line=dict(color='gray', dash='dash'), secondary_y=True)

# Set x-axis title
fig.update_xaxes(title_text='Date')

# Set y-axes titles
fig.update_yaxes(title_text='BTC Price (log scale)', secondary_y=False, type='log', tickcolor='blue')
fig.update_yaxes(title_text='STH Cost Basis & MVRV', secondary_y=True, tickcolor='red')

fig.update_layout(height=600,
                    legend=dict(
                    orientation='h',  # Horizontal layout
                    yanchor='bottom', # Anchor legend at the bottom
                    y=1.02,           # Position legend slightly above the plot
                    xanchor='center', # Anchor legend in the center
                    x=0.5             # Center the legend horizontally
))

# Function to create the plot using Plotly
def create_chart_sth_mvrv():
    return fig

fig = create_chart_sth_mvrv()

st.subheader('STH Cost Basis & MVRV')

st.plotly_chart(fig, use_container_width=True)