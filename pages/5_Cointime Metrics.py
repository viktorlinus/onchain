import json
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import streamlit as st
from aviv_nupl import aviv_nupl_df

# Fetch the webpage
url = "https://checkonchain.com/btconchain/cointime/cointime_pricing_mvrv_aviv_1/cointime_pricing_mvrv_aviv_1_light.html"
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
combined_df['AVIV Ratio'] = dataframes['AVIV Ratio']['Value']
combined_df['Mean + 2σ'] = dataframes['Mean + 2σ']['Value']
combined_df['Mean - 1σ'] = dataframes['Mean - 1σ']['Value']


# Calculate the expanding mean and standard deviation
expanding_mean = combined_df['AVIV Ratio'].expanding().mean()
expanding_std = combined_df['AVIV Ratio'].expanding().std()

# Calculate 'Mean + 3σ' using the expanding mean and standard deviation
combined_df['Mean + 3σ'] = expanding_mean + (expanding_std * 3)

def get_dataframe_aviv():
    return combined_df


# Filter the DataFrame to only include data from 2012 onwards
combined_df_filtered = combined_df[combined_df.index.year >= 2012]

# Create a subplot with 2 y-axes
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add 'BTC Price' trace with a logarithmic scale
fig.add_trace(
    go.Scatter(x=combined_df_filtered.index, y=combined_df_filtered['BTC Price'], name='BTC Price', mode='lines', line=dict(color='black')),
    secondary_y=False,
)

fig.add_trace(
    go.Scatter(x=combined_df_filtered.index, y=combined_df_filtered['True Market Mean'], name='True Market Mean', mode='lines', line=dict(color='blue')),
    secondary_y=False,
)

fig.add_trace(
    go.Scatter(x=combined_df_filtered.index, y=combined_df_filtered['AVIV Ratio'], name='AVIV Ratio', mode='lines', line=dict(color='purple')),
    secondary_y=True,
)

fig.add_trace(
    go.Scatter(x=combined_df_filtered.index, y=combined_df_filtered['Mean + 2σ'], name='Mean + 2σ', mode='lines', line=dict(color='orange')),
    secondary_y=True,
)
fig.add_trace(
    go.Scatter(x=combined_df_filtered.index, y=combined_df_filtered['Mean + 3σ'], name='Mean + 3σ', mode='lines', line=dict(color='red')),
    secondary_y=True,
)

fig.add_trace(
    go.Scatter(x=combined_df_filtered.index, y=combined_df_filtered['Mean - 1σ'], name='Mean - 1σ', mode='lines', line=dict(color='green')),
    secondary_y=True,
)

# Add a horizontal line at 0 on the secondary y-axis
fig.add_hline(y=0, line=dict(color='gray', dash='dash'), secondary_y=True)

# Set x-axis title
fig.update_xaxes(title_text='Date')

# Set y-axes titles
fig.update_yaxes(title_text='BTC Price (log scale)', secondary_y=False, type='log', tickcolor='blue')
fig.update_yaxes(title_text='True Market Mean & AVIV Ratio', secondary_y=True, tickcolor='red')

fig.update_layout(height=600,
                    legend=dict(
                    orientation='h',  # Horizontal layout
                    yanchor='bottom', # Anchor legend at the bottom
                    y=1.02,           # Position legend slightly above the plot
                    xanchor='center', # Anchor legend in the center
                    x=0.5             # Center the legend horizontally
))

# Function to create the plot using Plotly
def create_chart_aviv():
    return fig

fig = create_chart_aviv()

st.subheader('True Market Mean & AVIV Ratio')

st.plotly_chart(fig, use_container_width=True)

aviv_nupl = aviv_nupl_df()

expanding_mean_nupl_before = aviv_nupl['AVIV NUPL'].expanding().mean()
expanding_std_nupl_before = aviv_nupl['AVIV NUPL'].expanding().std()

aviv_nupl['Mean - 2σ'] = expanding_mean_nupl_before + (expanding_std_nupl_before * -2)
aviv_nupl['Mean + 1.25σ'] = expanding_mean_nupl_before + (expanding_std_nupl_before * 1.25)


# Filter the DataFrame to only include data from 2012 onwards
combined_df_filtered_nupl = aviv_nupl[combined_df.index.year >= 2012]

# Calculate the expanding mean and standard deviation
expanding_mean_nupl = combined_df_filtered_nupl['AVIV NUPL'].expanding().mean()
expanding_std_nupl = combined_df_filtered_nupl['AVIV NUPL'].expanding().std()

# Calculate 'Mean + 3σ' using the expanding mean and standard deviation
combined_df_filtered_nupl['Mean + 1.5σ'] = expanding_mean_nupl + (expanding_std_nupl * 1.5)
combined_df_filtered_nupl['Mean + 2σ'] = expanding_mean_nupl + (expanding_std_nupl * 2)


# Create a subplot with 2 y-axes
fig1 = make_subplots(specs=[[{"secondary_y": True}]])

# Add 'BTC Price' trace with a logarithmic scale
fig1.add_trace(
    go.Scatter(x=combined_df_filtered_nupl.index, y=combined_df_filtered_nupl['BTC Price'], name='BTC Price', mode='lines', line=dict(color='black')),
    secondary_y=False,
)

fig1.add_trace(
    go.Scatter(x=combined_df_filtered_nupl.index, y=combined_df_filtered_nupl['True Market Mean'], name='True Market Mean', mode='lines', line=dict(color='blue')),
    secondary_y=False,
)

fig1.add_trace(
    go.Scatter(x=combined_df_filtered_nupl.index, y=combined_df_filtered_nupl['AVIV NUPL'], name='AVIV NUPL', mode='lines', line=dict(color='purple')),
    secondary_y=True,
)

#fig1.add_trace(
#    go.Scatter(x=combined_df_filtered_nupl.index, y=combined_df_filtered_nupl['Mean + 2σ'], name='Mean + 2σ', mode='lines', line=dict(color='red')),
#    secondary_y=True,
#)
#fig1.add_trace(
#    go.Scatter(x=combined_df_filtered_nupl.index, y=combined_df_filtered_nupl['Mean + 1.5σ'], name='Mean + 1.5σ', mode='lines', line=dict(color='orange')),
#    secondary_y=True,
#)
fig1.add_trace(
    go.Scatter(x=combined_df_filtered_nupl.index, y=combined_df_filtered_nupl['Mean - 2σ'], name='Mean - 2σ', mode='lines', line=dict(color='green')),
    secondary_y=True,
)
fig1.add_trace(
    go.Scatter(x=combined_df_filtered_nupl.index, y=combined_df_filtered_nupl['Mean + 1.25σ'], name='Mean + 1.25σ', mode='lines', line=dict(color='red')),
    secondary_y=True,
)

# Add a horizontal line at 0 on the secondary y-axis
fig1.add_hline(y=0, line=dict(color='gray', dash='dash'), secondary_y=True)

# Set x-axis title
fig1.update_xaxes(title_text='Date')

# Set y-axes titles
fig1.update_yaxes(title_text='BTC Price (log scale)', secondary_y=False, type='log', tickcolor='blue')
fig1.update_yaxes(title_text='True Market Mean & AVIV NUPL', secondary_y=True, tickcolor='red')

fig1.update_layout(height=600,
                    legend=dict(
                    orientation='h',  # Horizontal layout
                    yanchor='bottom', # Anchor legend at the bottom
                    y=1.02,           # Position legend slightly above the plot
                    xanchor='center', # Anchor legend in the center
                    x=0.5             # Center the legend horizontally
))

st.subheader('True Market Mean & AVIV NUPL')

st.plotly_chart(fig1, use_container_width=True)