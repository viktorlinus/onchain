import streamlit as st
from streamlit.logger import get_logger
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
from streamlit_lightweight_charts import renderLightweightCharts
from price_models import get_dataframe, create_cycle_bands_plot, create_norm_plot, create_transformed_cycle

st.set_page_config(initial_sidebar_state="expanded", page_title="OnChain Data", layout="wide")


#st.markdown(
#    """
#<style>
#    [data-testid="collapsedControl"] {
#        display: none
#    }
#</style>
#""",
#    unsafe_allow_html=True,
#)


LOGGER = get_logger(__name__)


# Function to create the plot using Plotly
def create_chart(combined_df):
    # Filter the DataFrame to only include data from 2012 onwards
    combined_df_filtered = combined_df[combined_df.index.year >= 2012]

    # Create a subplot with 2 y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add 'BTC Price' trace with a logarithmic scale
    fig.add_trace(
        go.Scatter(x=combined_df_filtered.index, y=combined_df_filtered['BTC Price'], name='BTC Price', mode='lines', line=dict(color='blue')),
        secondary_y=False,
    )

    # Add 'Young-NUPL' trace
    fig.add_trace(
        go.Scatter(x=combined_df_filtered.index, y=combined_df_filtered['Young-NUPL'], name='Young-NUPL', mode='lines', line=dict(color='red')),
        secondary_y=True,
    )

    # Add a horizontal line at 0 on the secondary y-axis
    fig.add_hline(y=0, line=dict(color='green', dash='dash'), secondary_y=True)

    # Set x-axis title
    fig.update_xaxes(title_text='Date')

    # Set y-axes titles
    fig.update_yaxes(title_text='BTC Price (log scale)', secondary_y=False, type='log', tickcolor='blue')
    fig.update_yaxes(title_text='Young-NUPL (linear scale)', secondary_y=True, tickcolor='red')

    # Set the title
    fig.update_layout(title='BTC Price and Young-NUPL Over Time',
                      height=600)

    return fig

# Function to resample the DataFrame based on the selected timeframe
def resample_data(dataframe, timeframe):
    if timeframe == '1W':
        # Resample to weekly data, taking the mean of 'Adjusted_MVRV' for the week
        dataframe = dataframe.resample('W', on='Date').mean().reset_index()
    return dataframe

# Assuming the CSV file has columns 'Date', 'BTC Price', and 'Young-NUPL'
# and that 'Date' is in a format that pandas can parse as a datetime object
csv_file_path = 'nupl.csv'  # Replace with the path to your CSV file

# Load the data from the CSV file
combined_df = pd.read_csv(csv_file_path, index_col='Date', parse_dates=True)

# Load Norm MVRV Data
df = pd.read_csv('norm_mvrv.csv')

# Ensure 'Date' column is in datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Filter the DataFrame to include only data from September 2, 2010, onwards
df = df[df['Date'] >= '2010-09-02']

# Replace NaN values with a default value or use a method like 'ffill' or 'bfill'
df['Adjusted_MVRV'] = df['Adjusted_MVRV'].fillna(0)  # or df['Adjusted_MVRV'].fillna(method='ffill')


def run():

    st.title("On-Chain Data")

    # Plot the chart using the function defined above
    fig = create_chart(combined_df)
    # st.plotly_chart(fig, use_container_width=True)

    # Select the timeframe with a radio button
    # timeframe = st.radio("Select Timeframe:", ('1D', '1W'))

    # Resample the data based on the selected timeframe
    # df_resampled = resample_data(df, timeframe)

    # Convert 'Date' to the string format expected by Lightweight Charts
    # df_resampled['Date'] = df_resampled['Date'].dt.strftime('%Y-%m-%d')

    # Prepare the data for the chart
    # mrvr_series = [{
    #     "time": row['Date'],
    #     "value": row['Adjusted_MVRV']
    # } for index, row in df_resampled.iterrows()]

    # btc_price_series = [{
    #     "time": row['Date'],
    #     "value": row['BTC Price']
    # } for index, row in df_resampled.iterrows()]

    # Define the chart options
    chart_options = [
        {
            "rightPriceScale": {
                "mode": 1
            },
            "layout": {
                "textColor": 'black',
                "background": {
                    "type": 'solid',
                    "color": 'white'
                }
            }
        },
        {
            "layout": {
                "textColor": 'black',
                "background": {
                    "type": 'solid',
                    "color": 'white'
                }
            }
        }
    ]

    # Define the series for the line chart
    # seriesMVRV = [
    #     {
    #         "type": 'Line',
    #         "data": mrvr_series,
    #         "options": {
    #             "color": 'blue',
    #             "lineWidth": 2,
     #        }
     #    }
    # ]
    # seriesPrice = [
    #     {
    #         "type": 'Line',
     #        "data": btc_price_series,
    #         "options": {
    #             "color": 'red',
    #             "lineWidth": 2,
    #         }
    #     }
    # ]

    # Render the chart in Streamlit using the renderLightweightCharts function
    # st.subheader(f"Normalized MVRV Score on: {timeframe} Timeframe")
    
    # renderLightweightCharts([
    #    {
    #        "chart": chart_options[0],
    #        "series": seriesPrice
    #    },
    #    {
    #        "chart": chart_options[1],
    #        "series": seriesMVRV
    #    }
    #], 'multipane')

    st.subheader(f"Cycle Bands Avg Peaks & Troughs")
    df_cycles = get_dataframe()
    # Call the function to create the plot
    fig_cycles = create_cycle_bands_plot(df_cycles)

    # Show the figure
    st.plotly_chart(fig_cycles, use_container_width=True)

    st.subheader(f"Normalized Cycle Bands")
    # Call the function to create the plot
    fig_norm_cycles = create_norm_plot(df_cycles)

    # Show the figure
    st.plotly_chart(fig_norm_cycles, use_container_width=True)

    st.subheader(f"Normalized Transformed Cycle Bands")
    # Call the function to create the plot
    fig_transf_cycles = create_transformed_cycle(df_cycles)

    # Show the figure
    st.plotly_chart(fig_transf_cycles, use_container_width=True)


if __name__ == "__main__":
    run()
