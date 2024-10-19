import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import speedtest
import ping3
import threading
import time

latency_data = []
upload_data = []
download_data = []
x_data = []
stop_threads = False

# Collect network data
def collect_network_data():
    global stop_threads
    st = speedtest.Speedtest()  # Speedtest instance
    while not stop_threads:
        try:
            latency = ping3.ping('8.8.8.8') * 1000  # Ping Google DNS
            if latency is None:
                latency = 0

            st.get_best_server()
            download_speed = st.download() / 1_000_000  # Convert to Mbps
            upload_speed = st.upload() / 1_000_000  # Convert to Mbps

            latency_data.append(latency)
            upload_data.append(upload_speed)
            download_data.append(download_speed)
            x_data.append(len(latency_data))  

            time.sleep(5) 
        except Exception as e:
            print(f"Error collecting data: {e}")
            time.sleep(5)

# Data collection
data_thread = threading.Thread(target=collect_network_data)
data_thread.start()

# Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(style={
    'textAlign': 'center',
    'backgroundColor': '#f0f4f8',  
    'fontFamily': 'Arial, sans-serif',
    'padding': '20px',
}, children=[
    html.H1("Internet Speed and Latency Monitor", style={
        'color': '#1a76d2',
        'padding': '10px',
        'fontSize': '36px',
        'marginBottom': '10px',
    }),
    html.P("A simple tool to see your current internet performance.", style={
        'fontSize': '20px',
        'color': '#555555',
        'marginBottom': '30px',
    }),

    html.Div(id='live-stats', style={
        'padding': '20px',
        'display': 'flex',
        'justifyContent': 'space-around',
        'flexWrap': 'wrap', 
    }),
    
    dcc.Graph(id='live-graph', style={
        'width': '100%',
        'height': '60vh',  
        'margin': '0 auto',
    }),
    
    dcc.Interval(id='graph-update', interval=5*1000, n_intervals=0),  
])

# Update graph and display stats
@app.callback(
    [Output('live-graph', 'figure'), Output('live-stats', 'children')],
    [Input('graph-update', 'n_intervals')]
)
def update_graph(n):
    latest_latency = latency_data[-1] if latency_data else 0
    latest_upload = upload_data[-1] if upload_data else 0
    latest_download = download_data[-1] if download_data else 0

    live_stats = [
        html.Div([
            html.H2(f"{latest_latency:.2f} ms", style={'color': '#ff6f00'}),
            html.P("Latency (ms)", style={'fontSize': '18px', 'color': '#555'}),
        ], style={
            'padding': '20px',
            'backgroundColor': '#ffe0b2',
            'borderRadius': '10px',
            'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
            'flex': '1',  # Allow responsive sizing
            'margin': '10px',
        }),
        
        html.Div([
            html.H2(f"{latest_upload:.2f} Mbps", style={'color': '#43a047'}),
            html.P("Upload Speed", style={'fontSize': '18px', 'color': '#555'}),
        ], style={
            'padding': '20px',
            'backgroundColor': '#c8e6c9',
            'borderRadius': '10px',
            'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
            'flex': '1',
            'margin': '10px',
        }),
        
        html.Div([
            html.H2(f"{latest_download:.2f} Mbps", style={'color': '#1976d2'}),
            html.P("Download Speed", style={'fontSize': '18px', 'color': '#555'}),
        ], style={
            'padding': '20px',
            'backgroundColor': '#bbdefb',
            'borderRadius': '10px',
            'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
            'flex': '1',
            'margin': '10px',
        })
    ]

    # Traces for each plot
    latency_trace = go.Scatter(
        x=x_data,
        y=latency_data,
        mode='lines+markers',
        name='Latency (ms)',
        line=dict(color='#ff6f00', width=2),
        marker=dict(size=5)
    )

    upload_trace = go.Scatter(
        x=x_data,
        y=upload_data,
        mode='lines+markers',
        name='Upload Speed (Mbps)',
        line=dict(color='#43a047', width=2),
        marker=dict(size=5)
    )

    download_trace = go.Scatter(
        x=x_data,
        y=download_data,
        mode='lines+markers',
        name='Download Speed (Mbps)',
        line=dict(color='#1976d2', width=2),
        marker=dict(size=5)
    )

    # Combined figure
    figure = {
        'data': [latency_trace, upload_trace, download_trace],
        'layout': go.Layout(
            xaxis=dict(title='Time (Intervals)', showline=True, linewidth=1, linecolor='black'),
            yaxis=dict(title='Speed (Mbps) / Latency (ms)', showline=True, linewidth=1, linecolor='black'),
            title='Internet Speed and Latency',
            hovermode='closest',
            plot_bgcolor='#f0f4f8',
            paper_bgcolor='#f0f4f8',
            font=dict(family='Arial, sans-serif', size=12),
            margin=dict(l=40, r=40, t=40, b=40)
        )
    }

    return figure, live_stats

if __name__ == '__main__':
    app.run_server(debug=True)

# Safe stop
stop_threads = True
data_thread.join()
print("Monitoring stopped.\n")