import streamlit as st
from streamlit.logger import get_logger
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd

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
    fig.update_layout(title='BTC Price and Young-NUPL Over Time')

    return fig

# Assuming the CSV file has columns 'Date', 'BTC Price', and 'Young-NUPL'
# and that 'Date' is in a format that pandas can parse as a datetime object
csv_file_path = 'nupl.csv'  # Replace with the path to your CSV file

# Load the data from the CSV file
combined_df = pd.read_csv(csv_file_path, index_col='Date', parse_dates=True)


def run():
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )

    st.title("On-Chain Data")

    # Plot the chart using the function defined above
    fig = create_chart(combined_df)
    st.plotly_chart(fig)


if __name__ == "__main__":
    run()
