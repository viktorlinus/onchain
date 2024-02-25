import streamlit as st
from streamlit.logger import get_logger
import pandas as pd
from price_models import get_dataframe, create_transformed_cycle
from norm_mvrv import get_norm_mvrv_df, create_norm_mvrv_plot

st.set_page_config(initial_sidebar_state="expanded", page_title="OnChain Data", layout="wide")


LOGGER = get_logger(__name__)


def run():

    st.title("On-Chain Data")

    df_cycles = get_dataframe()

    st.subheader(f"Normalized Transformed Cycle Bands")
    # Call the function to create the plot
    fig_transf_cycles = create_transformed_cycle(df_cycles)

    # Show the figure
    st.plotly_chart(fig_transf_cycles, use_container_width=True)

    df_mvrv = get_norm_mvrv_df()

    st.subheader(f"Range Adjusted MVRV")
    # Call the function to create the plot
    fig_mvrv = create_norm_mvrv_plot(df_mvrv)

    # Show the figure
    st.plotly_chart(fig_mvrv, use_container_width=True)




if __name__ == "__main__":
    run()
