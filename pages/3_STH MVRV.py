from bs4 import BeautifulSoup as bs
import requests
import re
import json
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import streamlit as st

# Fetch the webpage
url = "https://chainexposed.com/RealizedPriceRibbonIsolated.html"  # Replace with the actual URL
raw = requests.get(url)
soup = bs(raw.text, "html.parser")

# Select the correct <script> tag by index
script_tags = soup.find_all("script")
for script_tag in script_tags:
    if 'var trace' in script_tag.text:
        script_content = script_tag.text
        break

# Initialize an empty list to hold all the trace data
all_traces_data = []

# Check if script_content is not None
if script_content:
    # Split the script content by 'var trace' to separate the traces
    traces = script_content.split('var trace')[1:]  # Skip the first split as it's before the first 'var trace'

    # Iterate over each trace
    for trace_str in traces:
        # Use regex to find the x, y, and name values
        x_match = re.search(r"x:\s*(\[.*?\]),", trace_str, re.DOTALL)
        y_match = re.search(r"y:\s*(\[.*?\]),", trace_str, re.DOTALL)
        name_match = re.search(r"name:\s*('.*?'),", trace_str)

        # Extract the values using the matches
        x_values = json.loads(x_match.group(1)) if x_match else []
        y_values = json.loads(y_match.group(1)) if y_match else []
        name_value = name_match.group(1).strip("'") if name_match else ""

        # Append the extracted data to the list
        all_traces_data.append({
            'x': x_values,
            'y': y_values,
            'name': name_value
        })

# Create an empty list to store the individual DataFrames
dfs = []

# Loop through each trace and create a DataFrame
for trace in all_traces_data:
    # Create a DataFrame for the current trace with 'x' as the index and 'y' as the values
    trace_df = pd.DataFrame({
        trace['name']: trace['y']
    }, index=trace['x'])
    dfs.append(trace_df)

# Concatenate all individual DataFrames along the columns
final_df = pd.concat(dfs, axis=1)

final_df = final_df.dropna(axis = 1)

final_df.index = pd.to_datetime(final_df.index)

# Now 'final_df' is a DataFrame with each 'y' in its own column, named after the 'name' value
print(final_df.info())

final_df['STH Cost Basis'] = final_df['1m to 3m'].astype(float)
final_df['STH MVRV'] = final_df['Price'].astype(float) / final_df['1m to 3m'].astype(float)

df = final_df.copy()

def sth_mvrv_df():
    return df

df = df[df.index >= pd.to_datetime('2012')]
# Assuming 'final_df' is your DataFrame and it has a 'Date' index in datetime format
# and columns named 'True Market Mean' and 'BTC Price'

# Plot the 'BTC Price' on a logarithmic scale and the standard deviation bands using Plotly
fig = go.Figure()

# Create a subplot with 2 y-axes
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add 'BTC Price' trace with a logarithmic scale
fig.add_trace(
    go.Scatter(x=df.index, y=df['Price'], name='BTC Price (log scale)', line=dict(color='black')),
    secondary_y=False,
)

# Add 'HODL Waves' trace on second y-axis
fig.add_trace(
    go.Scatter(x=df.index, y=df['STH Cost Basis'], name='STH Cost Basis', mode='lines', line=dict(color='brown')),
    secondary_y=False,
)
fig.add_trace(
    go.Scatter(x=df.index, y=df['STH MVRV'], name='STH MVRV', mode='lines', line=dict(color='purple')),
    secondary_y=True,
)

# Add a horizontal line at 0 on the secondary y-axis
fig.add_hline(y=1, line=dict(color='black', dash='dash'), secondary_y=True)

# Set x-axis title
fig.update_xaxes(title_text='Date')

# Set y-axes titles
fig.update_yaxes(title_text='BTC Price & STH Cost Basis', secondary_y=False, type='log', tickcolor='blue')
fig.update_yaxes(title_text='STH MVRV', secondary_y=True, tickcolor='red')

fig.update_layout(height=600,
                    legend=dict(
                    orientation='h',  # Horizontal layout
                    yanchor='bottom', # Anchor legend at the bottom
                    y=1.02,           # Position legend slightly above the plot
                    xanchor='center', # Anchor legend in the center
                    x=0.5             # Center the legend horizontally
))

def create_sth_mvrv_plot():
    return fig
    
fig = create_sth_mvrv_plot()

st.subheader('BTC Price and STH-MVRV')

st.plotly_chart(fig, use_container_width=True)