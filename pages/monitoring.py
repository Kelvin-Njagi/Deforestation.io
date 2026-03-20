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
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import require_auth
from image_processor import ImageProcessor

require_auth()

# Initialize all session state variables at the start
def init_session_state():
    """Initialize all session state variables"""
    if 'processor' not in st.session_state:
        st.session_state.processor = ImageProcessor()
    
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    if 'last_analysis_time' not in st.session_state:
        st.session_state.last_analysis_time = None
    
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = False
    
    if 'change_results' not in st.session_state:
        st.session_state.change_results = None
    
    if 'batch_results' not in st.session_state:
        st.session_state.batch_results = None

# Call initialization
init_session_state()

def show_monitoring_page():
    """Main monitoring page function"""
    st.title("🛰️ Forest Monitoring & Analysis")
    
    # Debug toggle in sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("### Debug Options")
        st.session_state.debug_mode = st.checkbox("Show Debug Info", value=st.session_state.debug_mode)
        
        if st.session_state.debug_mode:
            st.markdown("**Session State Keys:**")
            for key in st.session_state.keys():
                if key not in ['processor']:
                    st.write(f"- {key}: {type(st.session_state[key]).__name__}")
    
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
    """Single image analysis with persistent results"""
    st.subheader("🔬 Detailed Image Analysis")
    
    # Create a form to group the inputs and prevent reruns on interaction
    with st.form(key="analysis_form"):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Upload Image")
            uploaded_file = st.file_uploader(
                "Choose an image for detailed analysis",
                type=['png', 'jpg', 'jpeg', 'tif', 'tiff'],
                key="single_image_uploader_form",
                help="Upload satellite or drone imagery for deforestation analysis"
            )
            
            st.markdown("### Analysis Settings")
            analysis_type = st.radio(
                "Analysis Type",
                ["Quick Scan", "Standard Analysis", "Deep Analysis"],
                index=1,
                key="analysis_type_radio_form"
            )
            
            generate_report = st.checkbox("Generate Detailed Report", value=True, key="generate_report_checkbox_form")
        
        with col2:
            if uploaded_file is not None:
                st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
                st.markdown(f"**Filename:** {uploaded_file.name}")
                st.markdown(f"**File size:** {uploaded_file.size / 1024:.1f} KB")
        
        # Submit button inside the form
        analyze_clicked = st.form_submit_button("🔍 Analyze Image", type="primary", use_container_width=True)
    
    # Process image when form is submitted
    if analyze_clicked and uploaded_file is not None:
        with st.spinner("🔄 Processing image... This may take a few moments"):
            try:
                # Load image
                image = Image.open(uploaded_file)
                processed = processor.preprocess_image(image)
                
                if processed is not None:
                    # Calculate NDVI
                    ndvi = processor.calculate_ndvi(processed)
                    evi = processor.calculate_evi(processed)
                    
                    # Extract features
                    features = processor.extract_features(processed)
                    
                    # Classify land cover
                    classification = processor.classify_land_cover(processed)
                    
                    # Calculate risk score
                    risk_score = calculate_risk_score(features)
                    
                    # Store results in session state with timestamp
                    st.session_state.analysis_results = {
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'filename': uploaded_file.name,
                        'ndvi': ndvi,
                        'evi': evi,
                        'features': features,
                        'classification': classification,
                        'risk_score': risk_score,
                        'processed_image': processed,
                        'analysis_type': analysis_type
                    }
                    
                    st.session_state.last_analysis_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Add to history
                    history_entry = {
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'filename': uploaded_file.name,
                        'ndvi_mean': features.get('ndvi_mean', 0),
                        'forest_cover': features.get('forest_cover', 0),
                        'risk_score': risk_score,
                        'analysis_type': analysis_type
                    }
                    
                    # Initialize history list if not exists
                    if 'analysis_history' not in st.session_state:
                        st.session_state.analysis_history = []
                    
                    st.session_state.analysis_history.append(history_entry)
                    
                    st.success("✅ Analysis complete! Results displayed below.")
                    
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
                if st.session_state.debug_mode:
                    st.code(traceback.format_exc())
    
    # Display debug info
    if st.session_state.debug_mode:
        st.markdown("---")
        st.markdown("### Debug Info")
        st.write(f"Has analysis results: {st.session_state.analysis_results is not None}")
        st.write(f"Last analysis time: {st.session_state.last_analysis_time}")
    
    # Display results if they exist in session state
    if st.session_state.analysis_results is not None:
        display_analysis_results(st.session_state.analysis_results)
        
        # Clear results button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 Clear Results", key="clear_results_button", use_container_width=True):
                st.session_state.analysis_results = None
                st.rerun()

def display_analysis_results(results):
    """Display analysis results from session state"""
    st.markdown("---")
    st.markdown(f"## 📊 Analysis Results - {results['filename']}")
    st.markdown(f"*Analyzed at: {results['timestamp']}*")
    
    features = results['features']
    ndvi = results['ndvi']
    classification = results['classification']
    risk_score = results['risk_score']
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ndvi_mean = features.get('ndvi_mean', 0)
        delta = "Healthy" if ndvi_mean > 0.5 else "Moderate" if ndvi_mean > 0.3 else "Poor"
        st.metric("Mean NDVI", f"{ndvi_mean:.3f}", delta)
    
    with col2:
        forest_cover = features.get('forest_cover', 0)
        st.metric("Forest Cover", f"{forest_cover:.1f}%")
    
    with col3:
        if classification:
            forest_pct = classification['class_percentages'].get('forest', 0)
            st.metric("Forest Class", f"{forest_pct:.1f}%")
        else:
            st.metric("Forest Class", "N/A")
    
    with col4:
        risk_label = "Low" if risk_score < 30 else "Moderate" if risk_score < 60 else "High"
        st.metric("Risk Score", f"{risk_score:.0f}", risk_label)
    
    # Detailed analysis tabs
    res_tab1, res_tab2, res_tab3, res_tab4 = st.tabs([
        "🌿 Vegetation Indices", 
        "🗺️ Land Cover", 
        "📈 Feature Analysis",
        "⚠️ Risk Assessment"
    ])
    
    with res_tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            if ndvi is not None:
                fig = go.Figure(data=go.Heatmap(
                    z=ndvi,
                    colorscale='Viridis',
                    showscale=True,
                    colorbar_title="NDVI"
                ))
                fig.update_layout(title="NDVI Heatmap", height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if results['evi'] is not None:
                fig = go.Figure(data=go.Heatmap(
                    z=results['evi'],
                    colorscale='Plasma',
                    showscale=True,
                    colorbar_title="EVI"
                ))
                fig.update_layout(title="EVI (Enhanced Vegetation Index)", height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        if ndvi is not None:
            st.markdown("### NDVI Statistics")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Mean", f"{np.mean(ndvi):.3f}")
            col2.metric("Std Dev", f"{np.std(ndvi):.3f}")
            col3.metric("Max", f"{np.max(ndvi):.3f}")
            col4.metric("Min", f"{np.min(ndvi):.3f}")
            
            fig = px.histogram(
                x=ndvi.flatten(), 
                nbins=50,
                title="NDVI Distribution",
                labels={'x': 'NDVI Value', 'y': 'Frequency'}
            )
            fig.add_vline(x=0.3, line_dash="dash", line_color="red")
            st.plotly_chart(fig, use_container_width=True)
    
    with res_tab2:
        if classification:
            col1, col2 = st.columns(2)
            
            with col1:
                class_df = pd.DataFrame(
                    list(classification['class_percentages'].items()),
                    columns=['Class', 'Percentage']
                )
                fig = px.pie(
                    class_df,
                    values='Percentage',
                    names='Class',
                    title='Land Cover Distribution',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(
                    class_df,
                    x='Class',
                    y='Percentage',
                    title='Land Cover Percentages',
                    color='Class'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            if 'classification_map' in classification:
                fig = go.Figure(data=go.Heatmap(
                    z=classification['classification_map'],
                    colorscale='Viridis',
                    showscale=False
                ))
                fig.update_layout(title="Classification Map", height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    with res_tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            veg_features = {k: v for k, v in features.items() if 'ndvi' in k or 'evi' in k or 'forest' in k}
            if veg_features:
                st.markdown("#### 🌿 Vegetation Features")
                for k, v in veg_features.items():
                    if isinstance(v, (int, float)):
                        st.metric(k.replace('_', ' ').title(), f"{v:.3f}")
        
        with col2:
            texture_features = {k: v for k, v in features.items() if 'texture' in k or 'edge' in k}
            if texture_features:
                st.markdown("#### 🔲 Texture Features")
                for k, v in texture_features.items():
                    if isinstance(v, (int, float)):
                        st.metric(k.replace('_', ' ').title(), f"{v:.4f}")
    
    with res_tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Risk Assessment")
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=risk_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Deforestation Risk Score"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 30], 'color': "lightgreen"},
                        {'range': [30, 60], 'color': "yellow"},
                        {'range': [60, 100], 'color': "red"}
                    ]
                }
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Risk Factors")
            if features.get('forest_cover', 100) < 30:
                st.error("🔴 Very low forest cover")
            elif features.get('forest_cover', 100) < 50:
                st.warning("🟡 Low forest cover")
            
            if features.get('ndvi_mean', 0.5) < 0.3:
                st.error("🔴 Poor vegetation health")
            elif features.get('ndvi_mean', 0.5) < 0.4:
                st.warning("🟡 Declining vegetation")
        
        st.markdown("### Recommendations")
        if risk_score >= 60:
            st.error("🔴 URGENT: Immediate action required!")
        elif risk_score >= 30:
            st.warning("🟡 WARNING: Increase monitoring")
        else:
            st.success("✅ LOW RISK: Continue monitoring")

def show_change_detection(processor):
    """Change detection between two images"""
    st.subheader("🔄 Change Detection")
    
    # Use a form to prevent reruns
    with st.form(key="change_detection_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Before Image")
            before = st.file_uploader("Upload earlier image", type=['png', 'jpg', 'jpeg'], key="before_detection_form")
        
        with col2:
            st.markdown("### After Image")
            after = st.file_uploader("Upload later image", type=['png', 'jpg', 'jpeg'], key="after_detection_form")
        
        detect_clicked = st.form_submit_button("🔍 Detect Changes", type="primary", use_container_width=True)
    
    # Show previews outside form
    if before:
        st.image(before, caption="Before Image", use_column_width=True, width=300)
    if after:
        st.image(after, caption="After Image", use_column_width=True, width=300)
    
    if detect_clicked and before and after:
        with st.spinner("Analyzing changes..."):
            try:
                img1 = Image.open(before)
                img2 = Image.open(after)
                
                proc1 = processor.preprocess_image(img1)
                proc2 = processor.preprocess_image(img2)
                
                changes = processor.detect_changes(proc1, proc2)
                
                if changes:
                    st.session_state.change_results = {
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'before': before.name,
                        'after': after.name,
                        'changes': changes
                    }
                    st.success("✅ Change detection complete!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error during change detection: {str(e)}")
    
    # Display change results if they exist
    if st.session_state.get('change_results'):
        changes = st.session_state.change_results['changes']
        st.markdown("---")
        st.markdown(f"### Change Detection Results - {st.session_state.change_results['before']} vs {st.session_state.change_results['after']}")
        st.markdown(f"*Analyzed at: {st.session_state.change_results['timestamp']}*")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Change", f"{changes['total_change_percent']:.1f}%")
        col2.metric("Deforestation", f"{changes['deforestation_percent']:.1f}%")
        col3.metric("Reforestation", f"{changes['reforestation_percent']:.1f}%")
        
        if 'change_map' in changes:
            fig = go.Figure(data=go.Heatmap(
                z=changes['change_map'],
                colorscale='RdBu',
                showscale=False
            ))
            fig.update_layout(title="Change Map", height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        if changes['deforestation_percent'] > 15:
            st.error("🚨 CRITICAL: Significant deforestation detected!")
        elif changes['deforestation_percent'] > 5:
            st.warning("⚠️ WARNING: Moderate deforestation detected")
        else:
            st.success("✅ No significant deforestation")
        
        if st.button("Clear Change Results", key="clear_change_results"):
            st.session_state.change_results = None
            st.rerun()

def show_batch_processing(processor):
    """Batch process multiple images"""
    st.subheader("📦 Batch Processing")
    
    with st.form(key="batch_form"):
        files = st.file_uploader(
            "Choose multiple images",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            key="batch_uploader_form"
        )
        
        process_clicked = st.form_submit_button("🚀 Process Batch", type="primary", use_container_width=True)
    
    if process_clicked and files:
        progress_bar = st.progress(0)
        status = st.empty()
        
        results = []
        for i, file in enumerate(files):
            status.text(f"Processing {file.name}... ({i+1}/{len(files)})")
            
            try:
                image = Image.open(file)
                processed = processor.preprocess_image(image)
                features = processor.extract_features(processed)
                
                result = {'filename': file.name}
                if features:
                    for k, v in features.items():
                        if isinstance(v, (int, float)):
                            result[k] = round(v, 4)
                
                results.append(result)
            except Exception as e:
                st.error(f"Error processing {file.name}: {str(e)}")
            
            progress_bar.progress((i + 1) / len(files))
        
        status.text("Complete!")
        progress_bar.empty()
        
        st.session_state.batch_results = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'results': results,
            'count': len(results)
        }
        st.rerun()
    
    # Display batch results if they exist
    if st.session_state.get('batch_results'):
        st.markdown("---")
        st.markdown(f"### Batch Processing Results")
        st.markdown(f"*Processed at: {st.session_state.batch_results['timestamp']}*")
        st.success(f"✅ Successfully processed {st.session_state.batch_results['count']} images")
        
        df = pd.DataFrame(st.session_state.batch_results['results'])
        st.dataframe(df)
        
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            csv,
            file_name=f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if st.button("Clear Batch Results", key="clear_batch_results"):
            st.session_state.batch_results = None
            st.rerun()

def show_analysis_history():
    """Show analysis history"""
    st.subheader("📋 Analysis History")
    
    if st.session_state.analysis_history:
        df = pd.DataFrame(st.session_state.analysis_history)
        
        # Format the dataframe for better display
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        st.dataframe(df, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear History", key="clear_history_button", use_container_width=True):
                st.session_state.analysis_history = []
                st.session_state.analysis_results = None
                st.rerun()
        
        with col2:
            if st.button("Export History CSV", key="export_history", use_container_width=True):
                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 Download CSV",
                    csv,
                    file_name=f"analysis_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                )
    else:
        st.info("No analysis history yet. Run some analyses to see them here.")

def calculate_risk_score(features):
    """Calculate risk score from features"""
    score = 0
    
    if features.get('forest_cover', 100) < 30:
        score += 40
    elif features.get('forest_cover', 100) < 50:
        score += 20
    
    if features.get('ndvi_mean', 0.5) < 0.3:
        score += 30
    elif features.get('ndvi_mean', 0.5) < 0.4:
        score += 15
    
    return min(score, 100)

__all__ = ['show_monitoring_page']
