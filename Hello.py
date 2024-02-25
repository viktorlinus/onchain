import streamlit as st
from streamlit.logger import get_logger
import pandas as pd
from price_models import get_dataframe, create_cycle_bands_plot, create_norm_plot, create_transformed_cycle

st.set_page_config(initial_sidebar_state="expanded", page_title="OnChain Data", layout="wide")


LOGGER = get_logger(__name__)


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
