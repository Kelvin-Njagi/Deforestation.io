import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import hashlib
import json
import os
import logging
from pathlib import Path
import base64
from PIL import Image
import io

logger = logging.getLogger(__name__)

class UIManager:
    @staticmethod
    def set_page_config():
        st.set_page_config(
            page_title="Deforestation Monitoring System",
            page_icon="🌲",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    @staticmethod
    def apply_custom_css():
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 2rem;
            color: white;
            animation: fadeIn 1s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .main-header h1 {
            margin: 0;
            font-size: 2.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .main-header h3 {
            margin: 0.5rem 0 0;
            opacity: 0.9;
        }
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.8rem;
            text-align: center;
            z-index: 999;
            font-size: 0.9rem;
        }
        .stButton > button {
            width: 100%;
            border-radius: 25px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .metric-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 1.2rem;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin: 0.5rem 0;
            transition: transform 0.3s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
        }
        .metric-card h3 {
            margin: 0;
            font-size: 1rem;
            color: #555;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #2c3e50;
            margin: 0.5rem 0;
        }
        .alert-box {
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        .alert-success {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        .alert-warning {
            background-color: #fff3cd;
            border: 1px solid #ffeeba;
            color: #856404;
        }
        .alert-danger {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        </style>
        """, unsafe_allow_html=True)

class DataManager:
    @staticmethod
    def load_sample_data():
        """Load sample forest monitoring data"""
        dates = pd.date_range(start='2024-01-01', end='2025-03-19', freq='W')
        
        # Generate realistic forest cover data with trend
        np.random.seed(42)
        forest_cover = 100 - np.cumsum(np.random.normal(0.3, 0.1, len(dates)))
        forest_cover = np.clip(forest_cover, 60, 100)
        
        # Generate NDVI data
        ndvi = 0.3 + 0.4 * np.random.random(len(dates))
        ndvi = ndvi * (forest_cover / 100)  # Correlate with forest cover
        
        # Generate alerts
        alerts = np.random.poisson(forest_cover * 0.05, len(dates))
        
        df = pd.DataFrame({
            'date': dates,
            'forest_cover': forest_cover,
            'ndvi_mean': ndvi,
            'alerts': alerts,
            'deforested_area': np.random.exponential(5, len(dates)),
            'temperature': 20 + 5 * np.random.random(len(dates)),
            'rainfall': np.random.gamma(2, 10, len(dates))
        })
        
        return df
    
    @staticmethod
    def calculate_statistics(df):
        """Calculate statistics from data"""
        stats = {
            'total_forest': df['forest_cover'].iloc[-1],
            'forest_change': df['forest_cover'].iloc[-1] - df['forest_cover'].iloc[0],
            'avg_ndvi': df['ndvi_mean'].mean(),
            'total_alerts': df['alerts'].sum(),
            'avg_deforested': df['deforested_area'].mean(),
            'max_deforested': df['deforested_area'].max(),
            'total_deforested': df['deforested_area'].sum()
        }
        return stats

class ChartManager:
    @staticmethod
    def create_forest_cover_chart(df):
        """Create forest cover trend chart"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['forest_cover'],
            mode='lines+markers',
            name='Forest Cover',
            line=dict(color='#2ecc71', width=3),
            fill='tozeroy',
            fillcolor='rgba(46, 204, 113, 0.2)'
        ))
        
        fig.update_layout(
            title='🌲 Forest Cover Trend',
            xaxis_title='Date',
            yaxis_title='Forest Cover (%)',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_ndvi_trend_chart(df):
        """Create NDVI trend chart"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['ndvi_mean'],
            mode='lines',
            name='NDVI',
            line=dict(color='#3498db', width=3)
        ))
        
        fig.add_hline(y=0.3, line_dash="dash", line_color="#e74c3c",
                     annotation_text="Deforestation Threshold")
        
        fig.update_layout(
            title='📊 NDVI (Vegetation Health) Trend',
            xaxis_title='Date',
            yaxis_title='NDVI Value',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_alert_distribution_chart(df):
        """Create alert distribution chart"""
        df_monthly = df.resample('M', on='date').sum().reset_index()
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df_monthly['date'],
            y=df_monthly['alerts'],
            name='Alerts',
            marker_color='#e74c3c',
            marker_line_color='#c0392b',
            marker_line_width=1.5
        ))
        
        fig.update_layout(
            title='⚠️ Monthly Alert Distribution',
            xaxis_title='Month',
            yaxis_title='Number of Alerts',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_deforestation_heatmap(df):
        """Create deforestation heatmap"""
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year
        
        pivot = df.pivot_table(
            values='deforested_area',
            index='month',
            columns='year',
            aggfunc='mean'
        )
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            colorscale='Reds',
            texttemplate='%{z:.1f}',
            textfont={"size": 10},
            colorbar_title="Hectares"
        ))
        
        fig.update_layout(
            title='🔥 Deforestation Intensity Heatmap (hectares)',
            xaxis_title='Year',
            yaxis_title='Month',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    @staticmethod
    def create_forest_map():
        """Create forest monitoring map"""
        forest_locations = pd.DataFrame({
            'lat': [-0.15, -0.95, -0.45, 0.28, -1.3, -2.3],
            'lon': [37.3, 36.2, 36.7, 34.85, 36.8, 40.2],
            'name': ['Mt. Kenya', 'Mau Complex', 'Aberdare', 'Kakamega', 'Tsavo', 'Arabuko Sokoke'],
            'status': ['Stable', 'Critical', 'Warning', 'Stable', 'Warning', 'Stable'],
            'forest_cover': [72, 45, 58, 85, 62, 78]
        })
        
        # Color mapping
        colors = {'Stable': 'green', 'Warning': 'orange', 'Critical': 'red'}
        
        fig = go.Figure()
        
        fig.add_trace(go.Scattergeo(
            lon=forest_locations['lon'],
            lat=forest_locations['lat'],
            text=[f"{name}<br>Cover: {cover}%<br>Status: {status}" 
                  for name, cover, status in zip(forest_locations['name'], 
                                                forest_locations['forest_cover'],
                                                forest_locations['status'])],
            mode='markers+text',
            marker=dict(
                size=forest_locations['forest_cover'],
                color=[colors[status] for status in forest_locations['status']],
                symbol='circle',
                line=dict(width=2, color='white')
            ),
            textposition="top center",
            textfont=dict(size=10)
        ))
        
        fig.update_layout(
            title='🗺️ Kenya Forest Monitoring Network',
            geo=dict(
                scope='africa',
                projection_type='natural earth',
                showland=True,
                landcolor='rgb(243, 243, 243)',
                countrycolor='rgb(204, 204, 204)',
                center=dict(lat=0.5, lon=37.5),
                lataxis=dict(range=[-5, 5]),
                lonaxis=dict(range=[33, 42])
            ),
            height=600
        )
        
        return fig

class FileManager:
    @staticmethod
    def save_uploaded_file(uploaded_file, folder="uploads"):
        """Save uploaded file to disk"""
        try:
            Path(folder).mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{uploaded_file.name}"
            filepath = os.path.join(folder, filename)
            
            with open(filepath, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            return filepath
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            return None
    
    @staticmethod
    def get_file_download_link(filepath, text="Download File"):
        """Generate download link for file"""
        with open(filepath, 'rb') as f:
            data = f.read()
        
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="{os.path.basename(filepath)}">{text}</a>'
        return href
    
    @staticmethod
    def load_image(filepath):
        """Load image from filepath"""
        try:
            return Image.open(filepath)
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return None
