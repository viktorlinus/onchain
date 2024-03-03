import streamlit as st
from price_models import get_dataframe, create_cycle_bands_plot, create_norm_plot, create_transformed_cycle, create_all_cycle_bands

df_cycles = get_dataframe()

st.subheader("All Cycle Band Metrics")
fig_all = create_all_cycle_bands(df_cycles)

st.plotly_chart(fig_all, use_container_width=True)

st.subheader(f"Cycle Bands Avg Peaks & Troughs")

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