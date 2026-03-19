import streamlit as st
import sys
import os
import pandas as pd
import numpy as np
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import require_auth
from image_processor import ImageProcessor

require_auth()

def show_monitoring_page():
    """Main monitoring page function"""
    st.title("🛰️ Forest Monitoring & Analysis")
    
    # Initialize processor in session state
    if 'processor' not in st.session_state:
        st.session_state.processor = ImageProcessor()
    
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    processor = st.session_state.processor
    
    tab1, tab2, tab3, tab4 = st.tabs(["📸 Single Image Analysis", "🔄 Change Detection", "📊 Batch Processing", "📈 Analysis History"])
    
    with tab1:
        show_single_image_analysis(processor)
    with tab2:
        show_change_detection(processor)
    with tab3:
        show_batch_processing(processor)
    with tab4:
        show_analysis_history()

def show_single_image_analysis(processor):
    """Single image analysis"""
    st.subheader("🔬 Detailed Image Analysis")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Upload Image")
        uploaded_file = st.file_uploader(
            "Choose an image for detailed analysis",
            type=['png', 'jpg', 'jpeg', 'tif', 'tiff'],
            key="single_image_detailed"
        )
        
        st.markdown("### Analysis Settings")
        analysis_type = st.radio(
            "Analysis Type",
            ["Quick Scan", "Standard Analysis", "Deep Analysis"],
            index=1
        )
        
        generate_report = st.checkbox("Generate Detailed Report", value=True)
        analyze_btn = st.button("🔍 Analyze Image", type="primary", use_container_width=True)
    
    with col2:
        if uploaded_file:
            st.image(uploaded_file, caption="Original Image", use_column_width=True)
            st.markdown(f"**File:** {uploaded_file.name}")
    
    if uploaded_file and analyze_btn:
        with st.spinner("Processing image..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Loading image...")
            image = Image.open(uploaded_file)
            progress_bar.progress(20)
            
            status_text.text("Preprocessing...")
            processed = processor.preprocess_image(image)
            progress_bar.progress(40)
            
            if processed is not None:
                status_text.text("Calculating NDVI...")
                ndvi = processor.calculate_ndvi(processed)
                progress_bar.progress(60)
                
                status_text.text("Extracting features...")
                features = processor.extract_features(processed)
                progress_bar.progress(80)
                
                status_text.text("Classifying...")
                classification = processor.classify_land_cover(processed)
                progress_bar.progress(100)
                
                status_text.text("Complete!")
                time.sleep(0.5)
                
                progress_bar.empty()
                status_text.empty()
                
                st.markdown("---")
                st.markdown("## 📊 Analysis Results")
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Mean NDVI", f"{features.get('ndvi_mean', 0):.3f}")
                with col2:
                    st.metric("Forest Cover", f"{features.get('forest_cover', 0):.1f}%")
                with col3:
                    if classification:
                        st.metric("Forest Class", f"{classification['class_percentages'].get('forest', 0):.1f}%")
                with col4:
                    risk_score = (100 - features.get('forest_cover', 50)) * 2
                    risk_score = min(100, max(0, risk_score))
                    st.metric("Risk Score", f"{risk_score:.0f}")
                
                # Tabs
                res_tab1, res_tab2, res_tab3 = st.tabs(["🌿 NDVI", "🗺️ Classification", "📊 Features"])
                
                with res_tab1:
                    if ndvi is not None:
                        # Using ONLY named colorscale - NO custom colorscale
                        fig = go.Figure(data=go.Heatmap(
                            z=ndvi,
                            colorscale='Viridis',  # Named colorscale only
                            showscale=True
                        ))
                        fig.update_layout(title="NDVI Heatmap", height=400)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        fig2 = px.histogram(x=ndvi.flatten(), nbins=50, title="NDVI Distribution")
                        fig2.add_vline(x=0.3, line_dash="dash", line_color="red")
                        st.plotly_chart(fig2, use_container_width=True)
                
                with res_tab2:
                    if classification:
                        col1, col2 = st.columns(2)
                        with col1:
                            class_df = pd.DataFrame(
                                list(classification['class_percentages'].items()),
                                columns=['Class', 'Percentage']
                            )
                            fig = px.pie(class_df, values='Percentage', names='Class', title='Land Cover Distribution')
                            st.plotly_chart(fig, use_container_width=True)
                        with col2:
                            fig = px.bar(class_df, x='Class', y='Percentage', title='Land Cover Percentages')
                            st.plotly_chart(fig, use_container_width=True)
                
                with res_tab3:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("#### Vegetation Features")
                        for k in ['ndvi_mean', 'ndvi_std', 'evi_mean', 'forest_cover']:
                            if k in features:
                                st.metric(k.replace('_',' ').title(), f"{features[k]:.3f}")
                    with col2:
                        st.markdown("#### Texture Features")
                        for k in ['texture_mean', 'texture_std', 'edge_density']:
                            if k in features:
                                st.metric(k.replace('_',' ').title(), f"{features[k]:.4f}")
                
                # Save to history
                st.session_state.analysis_history.append({
                    'timestamp': datetime.now(),
                    'filename': uploaded_file.name,
                    'ndvi': features.get('ndvi_mean', 0)
                })
                
                if generate_report:
                    st.markdown("---")
                    report_path = processor.generate_report(processed)
                    if report_path:
                        with open(report_path, 'r') as f:
                            st.download_button("📥 Download Report", f.read(), file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

def show_change_detection(processor):
    """Change detection"""
    st.subheader("🔄 Change Detection Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Before")
        before = st.file_uploader("Upload earlier image", type=['png','jpg','jpeg'], key="before")
        if before:
            st.image(before, use_column_width=True)
    with col2:
        st.markdown("### After")
        after = st.file_uploader("Upload later image", type=['png','jpg','jpeg'], key="after")
        if after:
            st.image(after, use_column_width=True)
    
    if before and after:
        if st.button("🔄 Detect Changes", type="primary", use_container_width=True):
            with st.spinner("Analyzing..."):
                img1 = Image.open(before)
                img2 = Image.open(after)
                
                proc1 = processor.preprocess_image(img1)
                proc2 = processor.preprocess_image(img2)
                
                changes = processor.detect_changes(proc1, proc2)
                
                if changes:
                    st.markdown("### Results")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Change", f"{changes['total_change_percent']:.1f}%")
                    col2.metric("Deforestation", f"{changes['deforestation_percent']:.1f}%")
                    col3.metric("Reforestation", f"{changes['reforestation_percent']:.1f}%")
                    
                    # Using ONLY named colorscale
                    if 'change_map' in changes:
                        fig = go.Figure(data=go.Heatmap(
                            z=changes['change_map'],
                            colorscale='RdBu',  # Named colorscale only
                            showscale=False
                        ))
                        fig.update_layout(title="Change Map", height=400)
                        st.plotly_chart(fig, use_container_width=True)

def show_batch_processing(processor):
    """Batch processing"""
    st.subheader("📦 Batch Processing")
    
    files = st.file_uploader("Choose multiple images", type=['png','jpg','jpeg'], accept_multiple_files=True)
    
    if files:
        st.markdown(f"**Selected:** {len(files)} images")
        if st.button("🚀 Process Batch", type="primary", use_container_width=True):
            progress = st.progress(0)
            results = []
            for i, file in enumerate(files):
                image = Image.open(file)
                processed = processor.preprocess_image(image)
                features = processor.extract_features(processed)
                results.append({'filename': file.name, 'ndvi_mean': features.get('ndvi_mean', 0)})
                progress.progress((i + 1) / len(files))
            
            st.success(f"✅ Processed {len(results)} images")
            df = pd.DataFrame(results)
            st.dataframe(df)
            
            csv = df.to_csv(index=False)
            st.download_button("📥 Download CSV", csv, file_name=f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

def show_analysis_history():
    """Show history"""
    st.subheader("📋 Analysis History")
    if st.session_state.analysis_history:
        st.dataframe(pd.DataFrame(st.session_state.analysis_history))
        if st.button("Clear History"):
            st.session_state.analysis_history = []
            st.rerun()
    else:
        st.info("No analysis history yet")

__all__ = ['show_monitoring_page']

if __name__ == "__main__":
    show_monitoring_page()
