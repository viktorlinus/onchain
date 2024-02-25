import streamlit as st
from price_models import get_dataframe, create_cycle_bands_plot, create_norm_plot, create_transformed_cycle


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