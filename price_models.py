import json
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np

# Fetch the webpage
url = "https://charts.checkonchain.com/btconchain/pricing/pricing_onchainoriginals/pricing_onchainoriginals_light.html"
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
combined_df['Cointime Price'] = dataframes['Cointime Price']['Value']
combined_df['Delta Price'] = dataframes['Delta Price']['Value']
combined_df['Vaulted Price'] = dataframes['Vaulted Price']['Value']
combined_df['Realized Price'] = dataframes['Realized Price']['Value']
combined_df['Balanced Price'] = dataframes['Balanced Price']['Value']
combined_df['True Mean Price'] = dataframes['True Mean Price']['Value']
combined_df['Delta Top'] = combined_df['Delta Price'] * 7
combined_df['Vaulted Top'] = combined_df['Vaulted Price'] * 1.75
combined_df['Transferred Price'] = combined_df['Realized Price'] - combined_df['Balanced Price']
combined_df['Terminal Price'] = combined_df['Transferred Price'] * 21
combined_df['Transferred Price AVIV'] = combined_df['True Mean Price'] - combined_df['Balanced Price']
combined_df['Terminal Price AVIV'] = combined_df['Transferred Price AVIV'] * 6

df = combined_df.copy()
df = df[df.index >= pd.to_datetime('2012')]

df['Avg Top'] = df[['Vaulted Top', 'Terminal Price AVIV', 'Delta Top']].mean(axis = 1)
df['Avg Bot'] = df[['Delta Price', 'Cointime Price', 'Realized Price']].mean(axis = 1)

df['Normalized Price'] = (df['BTC Price'] - df['Avg Bot']) / (df['Avg Top'] - df['Avg Bot'])

# Calculate the row numbers based on the date index
df['Row Number'] = np.arange(len(df))

# Define the overbought and oversold functions using the row numbers
df['Overbought'] = -np.log(1.1 * df['Row Number'] + 4000) + 9.8
df['Oversold'] = np.log(0.25 * df['Row Number'] + 11000) - 9.4

# Calculate the Adjusted Normalized Price to fluctuate between the overbought and oversold curves
df['Adjusted Normalized Price'] = (df['Normalized Price'] - df['Oversold']) / (df['Overbought'] - df['Oversold'])

def create_all_cycle_bands(df):
    df = df[df.index >= pd.to_datetime('2012')]
    # Assuming 'final_df' is your DataFrame and it has a 'Date' index in datetime format
    # and columns named 'True Market Mean' and 'BTC Price'

    # Plot the 'BTC Price' on a logarithmic scale and the standard deviation bands using Plotly
    fig = go.Figure()

    # Create a subplot with 2 y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add 'BTC Price' trace with a logarithmic scale
    fig.add_trace(
        go.Scatter(x=df.index, y=df['BTC Price'], name='BTC Price (log scale)', line=dict(color='blue')),
        secondary_y=False,
    )

    # Add
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Terminal Price'], name='Terminal Price', mode='lines', line=dict(color='red')),
        secondary_y=False,
    )
    # Add
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Terminal Price AVIV'], name='Terminal Price AVIV', mode='lines', line=dict(color='black')),
        secondary_y=False,
    )
    # Add
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Balanced Price'], name='Balanced Price', mode='lines', line=dict(color='green')),
        secondary_y=False,
    )
    # Add
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Realized Price'], name='Realized Price', mode='lines', line=dict(color='indigo')),
        secondary_y=False,
    )
    # Add
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Delta Top'], name='Delta Top', mode='lines', line=dict(color='purple')),
        secondary_y=False,
    )
    # Add
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Vaulted Price'], name='Vaulted Price', mode='lines', line=dict(color='violet')),
        secondary_y=False,
    )
    # Add
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Vaulted Top'], name='Vaulted Top', mode='lines', line=dict(color='red')),
        secondary_y=False,
    )
    # Add
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Cointime Price'], name='Cointime Price', mode='lines', line=dict(color='orange')),
        secondary_y=False,
    )

    # Set x-axis title
    fig.update_xaxes(title_text='Date')

    # Set y-axes titles
    fig.update_yaxes(title_text='BTC Price (log scale)', secondary_y=False, type='log', tickcolor='blue')
    # fig.update_yaxes(title_text='HODL Waves (BTC)', secondary_y=True, tickcolor='red')

    # Set the title
    fig.update_layout(height = 600,
                      legend=dict(
                        orientation='h',  # Horizontal layout
                        yanchor='bottom', # Anchor legend at the bottom
                        y=1.02,           # Position legend slightly above the plot
                        xanchor='center', # Anchor legend in the center
                        x=0.5             # Center the legend horizontally
    ))

    return fig

def get_dataframe():
    return df


def create_cycle_bands_plot(df):
    # Assuming 'df' is your DataFrame and it has a 'Date' index in datetime format
    # and columns named 'True Market Mean' and 'BTC Price'

    # Filter the DataFrame for dates after 2012
    df = df[df.index >= pd.to_datetime('2012')]

    # Create a subplot with 2 y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add 'BTC Price' trace with a logarithmic scale
    fig.add_trace(
        go.Scatter(x=df.index, y=df['BTC Price'], name='BTC Price (log scale)', line=dict(color='blue')),
        secondary_y=False,
    )

    # Add 'Avg Top' trace
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Avg Top'], name='Avg Top', mode='lines', line=dict(color='red')),
        secondary_y=False,
    )

    # Add 'Avg Bot' trace
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Avg Bot'], name='Avg Bot', mode='lines', line=dict(color='green')),
        secondary_y=False,
    )

    # Set x-axis title
    fig.update_xaxes(title_text='Date')

    # Set y-axes titles
    fig.update_yaxes(title_text='BTC Price (log scale)', secondary_y=False, type='log', tickcolor='blue')

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

def create_norm_plot(df):
    fig = go.Figure()

    # Create a subplot with 2 y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add 'BTC Price' trace with a logarithmic scale
    fig.add_trace(
        go.Scatter(x=df.index, y=df['BTC Price'], name='BTC Price (log scale)', line=dict(color='blue')),
        secondary_y=False,
    )

    # Add
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Normalized Price'], name='Normalized Cycle Range', mode='lines', line=dict(color='purple')),
        secondary_y=True,
    )
    # Add
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Overbought'], name='Transformed Top', mode='lines', line=dict(color='red')),
        secondary_y=True,
    )
    # Add
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Oversold'], name='Transformed Bottom', mode='lines', line=dict(color='green')),
        secondary_y=True,
    )

    # Set x-axis title
    fig.update_xaxes(title_text='Date')

    # Set y-axes titles
    fig.update_yaxes(title_text='BTC Price (log scale)', secondary_y=False, type='log', tickcolor='blue')
    #fig.update_yaxes(title_text='HODL Waves (BTC)', secondary_y=True, tickcolor='red')

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

def create_transformed_cycle(df):
    fig = go.Figure()

    # Create a subplot with 2 y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add 'BTC Price' trace with a logarithmic scale
    fig.add_trace(
        go.Scatter(x=df.index, y=df['BTC Price'], name='BTC Price (log scale)', line=dict(color='blue')),
        secondary_y=False,
    )

    # Add
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Adjusted Normalized Price'], name='Transformed Cycle Range', mode='lines', line=dict(color='purple')),
        secondary_y=True,
    )

    # Set x-axis title
    fig.update_xaxes(title_text='Date')

    # Set y-axes titles
    fig.update_yaxes(title_text='BTC Price (log scale)', secondary_y=False, type='log', tickcolor='blue')
    #fig.update_yaxes(title_text='HODL Waves (BTC)', secondary_y=True, tickcolor='red')

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
