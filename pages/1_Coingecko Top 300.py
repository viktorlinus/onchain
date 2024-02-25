import streamlit as st
from streamlit_gsheets import GSheetsConnection
import plotly.graph_objs as go

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(worksheet="Price")
df2 = conn.read(worksheet="30D Change")

st.header('Top 300 Tokens')
st.subheader('Prices')
st.dataframe(df)
st.subheader('30D Change')
st.dataframe(df2)

import pandas as pd

# First, set the 'Date' column as the index if you want to exclude it from calculations
df2['Date'] = pd.to_datetime(df2['Date'])
df2.set_index('Date', inplace=True)

# Now, compare each token's value to BTC and assign 1 or 0 accordingly
comparison_df = df2.apply(lambda row: [1 if value > row['BTC'] else 0 if value > 0 else None for value in row[1:]], axis=1, result_type='expand')

# Set the column names to the original tokens
comparison_df.columns = df2.columns[1:]

# Calculate the average value for each row
comparison_df['avg'] = comparison_df.apply(lambda row: row.dropna().mean(), axis=1)

# Insert the 'avg' column as the first column in the DataFrame
first_col = comparison_df.pop('avg')
comparison_df.insert(0, 'Avg', first_col)

st.subheader('30D Change > BTC?')

# Now, comparison_df contains the comparison results and the average for each row
st.dataframe(comparison_df)

# Convert the index to datetime if it's not already (this step may not be necessary if it's already a datetime index)
comparison_df.index = pd.to_datetime(comparison_df.index)

# Create a Plotly figure
fig_avg = go.Figure()

# Add the line plot
fig_avg.add_trace(go.Scatter(
    x=comparison_df.index, 
    y=comparison_df['Avg'] * 100, 
    mode='lines', 
    name='30D Speculation Index',
    hovertemplate='%{x}<br>30D Speculation Index: %{y:.2f}%<extra></extra>'
))
# Drop rows where 'Avg' is NaN
comparison_df.dropna(subset=['Avg'], inplace=True)

# Get the last date and the last value for the annotation
last_date2 = comparison_df.index[-1]
last_value2 = comparison_df['Avg'].iloc[-1] * 100

# Add text annotation for the last value
fig_avg.add_annotation(
    x=last_date2,
    y=last_value2,
    xshift=30,
    text=f"<b>{last_value2:.2f}%</b>",  # Make text bold using <b> tags
    showarrow=False,
    font=dict(
        size=12,
        color="white"  # Text color
    ),
    align="left",
    bgcolor="blue",  # Background color
    bordercolor="blue",
    borderpad=4,  # Padding around the text
    opacity=0.8
)

# Set layout options
fig_avg.update_layout(
    title='30D Change > BTC',
    xaxis_title='Date',
    yaxis_title='Speculation Index',
    xaxis=dict(
        showline=True, 
        showgrid=False,
        tickformat='%Y-%m-%d'  # Set the tick labels to show only the date
    ),
    yaxis=dict(
        showline=True, 
        showgrid=True
    ),
    height=600
)

# Set the y-axis range between 0 and 100
fig_avg.update_yaxes(range=[0, 100])

# Show the figure
st.plotly_chart(fig_avg, use_container_width=True)

# Check the values before adding the annotation
st.write("Last Date for Annotation:", comparison_df.index[-1].date())
st.write("Last Value for Annotation:", (comparison_df['Avg'].iloc[-1] * 100))