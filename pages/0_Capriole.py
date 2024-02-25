import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objs as go

url = "https://docs.google.com/spreadsheets/d/1aUBtfcosN0-KzZrLQhwVYyRWsomGpNmef1ZY7ZySI8w/edit?usp=sharing"

conn_cap = st.connection("gsheets", type=GSheetsConnection)

df = conn_cap.read(spreadsheet=url, usecols=[0, 2], worksheet='speculation_index')

# Convert 'date' column to datetime
df['date'] = pd.to_datetime(df['date'])

# Set the 'date' column as the index
df.set_index('date', inplace=True)

# Create a Plotly figure
fig = go.Figure()

# Add the line plot
fig.add_trace(go.Scatter(x=df.index, 
                         y=df['Speculation Index'], 
                         mode='lines', 
                         name='Speculation Index',
                         hovertemplate='%{x}<br>Speculation Index: %{y:.2f}<extra></extra>'))

# Get the last date and the last value for the annotation
last_date = df.index[-1]
last_value = df['Speculation Index'].iloc[-1]

# Add text annotation for the last value
fig.add_annotation(
    x=last_date,
    y=last_value,
    xshift=30,
    text=f"<b>{last_value:.2f}%</b>",  # Make text bold using <b> tags
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
fig.update_layout(
    title='Speculation Index Over Time',
    xaxis_title='Date',
    yaxis_title='Speculation Index',
    xaxis=dict(showline=True, showgrid=False),
    yaxis=dict(showline=True, showgrid=True),
    height=600
)

# Show the figure
st.plotly_chart(fig, use_container_width=True)

conn_cap2 = st.connection("gsheets", type=GSheetsConnection)

df_breadth = conn_cap2.read(spreadsheet=url, worksheet='breadth_crypto')

# Convert 'date' column to datetime
df_breadth['date'] = pd.to_datetime(df_breadth['date'])

# Set the 'date' column as the index
df_breadth.set_index('date', inplace=True)

# Create a Plotly figure
fig_breadth = go.Figure()

# Add the line plot
fig_breadth.add_trace(go.Scatter(x=df_breadth.index, 
                         y=df_breadth['breadth50'] * 100, 
                         mode='lines', 
                         name='Breadth 50',
                         hovertemplate='%{x}<br>Breadth 50: %{y:.2f}%<extra></extra>'))

fig_breadth.add_trace(go.Scatter(x=df_breadth.index, 
                         y=df_breadth['breadth200'] * 100, 
                         mode='lines', 
                         name='Breadth 200',
                         line=dict(color='red'),
                         hovertemplate='%{x}<br>Breadth 200: %{y:.2f}%<extra></extra>'))

# Set layout options
fig_breadth.update_layout(
    title='Crypto Breadth',
    xaxis_title='Date',
    yaxis_title='Breadth',
    xaxis=dict(showline=True, showgrid=False),
    yaxis=dict(showline=True, showgrid=True),
    height=600
)

# Show the figure
st.plotly_chart(fig_breadth, use_container_width=True)