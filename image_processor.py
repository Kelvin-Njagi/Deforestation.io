import cv2
import numpy as np
from PIL import Image
import logging
from skimage import exposure, filters, segmentation, measure, color
from skimage.feature import local_binary_pattern
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
import tempfile
import os
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        self.ndvi_threshold = 0.3
        self.min_forest_area = 100  # pixels
        self.classifier = None
        
    def preprocess_image(self, image):
        """Preprocess image for analysis"""
        try:
            # Convert to numpy array if PIL Image
            if isinstance(image, Image.Image):
                image = np.array(image)
            
            # Convert to RGB if needed
            if len(image.shape) == 3 and image.shape[2] == 3:
                if image.dtype == np.uint8:
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Resize if too large (maintain aspect ratio)
            height, width = image.shape[:2]
            max_size = 1024
            if height > max_size or width > max_size:
                scale = max_size / max(height, width)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height))
            
            # Apply Gaussian blur to reduce noise
            image = cv2.GaussianBlur(image, (5, 5), 0)
            
            # Enhance contrast using CLAHE
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            lab = cv2.merge([l, a, b])
            image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            
            return image
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return None
    
    def calculate_ndvi(self, image):
        """Calculate NDVI from image"""
        try:
            # Convert to float
            image_float = image.astype(np.float32) / 255.0
            
            # Extract bands
            red = image_float[:, :, 2]  # Red band
            nir = image_float[:, :, 1]  # Use green as NIR proxy
            
            # Calculate NDVI
            numerator = nir - red
            denominator = nir + red + 1e-10
            ndvi = numerator / denominator
            
            # Normalize to [0, 1]
            ndvi = (ndvi + 1) / 2
            ndvi = np.clip(ndvi, 0, 1)
            
            return ndvi
            
        except Exception as e:
            logger.error(f"Error calculating NDVI: {e}")
            return None
    
    def calculate_evi(self, image):
        """Calculate Enhanced Vegetation Index"""
        try:
            image_float = image.astype(np.float32) / 255.0
            
            red = image_float[:, :, 2]
            nir = image_float[:, :, 1]
            blue = image_float[:, :, 0]
            
            # EVI = 2.5 * ((NIR - RED) / (NIR + 6*RED - 7.5*BLUE + 1))
            numerator = 2.5 * (nir - red)
            denominator = nir + 6*red - 7.5*blue + 1 + 1e-10
            evi = numerator / denominator
            
            evi = np.clip(evi, -1, 1)
            evi = (evi + 1) / 2  # Normalize to [0, 1]
            
            return evi
            
        except Exception as e:
            logger.error(f"Error calculating EVI: {e}")
            return None
    
    def segment_image(self, image, method='kmeans', n_clusters=3):
        """Segment image into regions"""
        try:
            if method == 'kmeans':
                # Reshape image
                pixels = image.reshape(-1, 3)
                pixels = pixels.astype(np.float32)
                
                # Apply k-means
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                labels = kmeans.fit_predict(pixels)
                
                # Reshape back
                segmented = labels.reshape(image.shape[:2])
                
                return segmented
                
            elif method == 'slic':
                # Simple Linear Iterative Clustering
                from skimage.segmentation import slic
                segments = slic(image, n_segments=100, compactness=10, sigma=1)
                return segments
            
            elif method == 'threshold':
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                thresh = filters.threshold_otsu(gray)
                binary = gray > thresh
                return binary.astype(np.uint8)
            
        except Exception as e:
            logger.error(f"Error segmenting image: {e}")
            return None
    
    def extract_features(self, image, segmented=None):
        """Extract comprehensive features from image"""
        try:
            features = {}
            
            # Color features
            for i, color in enumerate(['blue', 'green', 'red']):
                channel = image[:, :, i]
                features[f'{color}_mean'] = np.mean(channel)
                features[f'{color}_std'] = np.std(channel)
                features[f'{color}_skew'] = pd.Series(channel.flatten()).skew()
            
            # Texture features using LBP
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            lbp = local_binary_pattern(gray, 8, 1, method='uniform')
            features['texture_mean'] = np.mean(lbp)
            features['texture_std'] = np.std(lbp)
            
            # Edge features
            edges = filters.sobel(gray)
            features['edge_density'] = np.mean(edges > 0.1)
            
            # Vegetation indices
            ndvi = self.calculate_ndvi(image)
            if ndvi is not None:
                features['ndvi_mean'] = np.mean(ndvi)
                features['ndvi_std'] = np.std(ndvi)
                features['ndvi_max'] = np.max(ndvi)
                features['ndvi_min'] = np.min(ndvi)
                features['forest_cover'] = np.mean(ndvi > self.ndvi_threshold) * 100
            
            evi = self.calculate_evi(image)
            if evi is not None:
                features['evi_mean'] = np.mean(evi)
                features['evi_std'] = np.std(evi)
            
            # Segmentation-based features
            if segmented is not None:
                regions = measure.regionprops(segmented + 1)
                features['n_regions'] = len(regions)
                features['avg_region_size'] = np.mean([r.area for r in regions])
                
                if ndvi is not None:
                    forest_regions = 0
                    for region in regions:
                        region_ndvi = ndvi[segmented == region.label-1]
                        if np.mean(region_ndvi) > self.ndvi_threshold:
                            forest_regions += 1
                    features['forest_region_ratio'] = forest_regions / len(regions) * 100
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return {}
    
    def detect_changes(self, image1, image2):
        """Detect changes between two images"""
        try:
            # Calculate NDVI for both images
            ndvi1 = self.calculate_ndvi(image1)
            ndvi2 = self.calculate_ndvi(image2)
            
            if ndvi1 is None or ndvi2 is None:
                return None
            
            # Ensure same size
            if ndvi1.shape != ndvi2.shape:
                ndvi2 = cv2.resize(ndvi2, (ndvi1.shape[1], ndvi1.shape[0]))
            
            # Calculate difference
            ndvi_diff = ndvi2 - ndvi1
            
            # Identify changes
            deforested = ndvi_diff < -self.ndvi_threshold
            reforested = ndvi_diff > self.ndvi_threshold
            
            # Calculate statistics
            total_pixels = deforested.size
            deforested_pixels = np.sum(deforested)
            reforested_pixels = np.sum(reforested)
            
            # Create change map
            change_map = np.zeros_like(ndvi_diff)
            change_map[deforested] = 1  # Deforestation
            change_map[reforested] = 2   # Reforestation
            
            change_stats = {
                'total_change_percent': ((deforested_pixels + reforested_pixels) / total_pixels) * 100,
                'deforestation_percent': (deforested_pixels / total_pixels) * 100,
                'reforestation_percent': (reforested_pixels / total_pixels) * 100,
                'mean_ndvi_change': np.mean(ndvi_diff),
                'max_ndvi_decrease': np.min(ndvi_diff),
                'max_ndvi_increase': np.max(ndvi_diff),
                'deforested_areas': deforested,
                'change_map': change_map
            }
            
            return change_stats
            
        except Exception as e:
            logger.error(f"Error detecting changes: {e}")
            return None
    
    def classify_land_cover(self, image, method='rf'):
        """Classify land cover types using machine learning"""
        try:
            # Extract features
            features = self.extract_features(image)
            
            # Simple threshold-based classification
            ndvi = self.calculate_ndvi(image)
            if ndvi is None:
                return None
            
            # Initialize classification map
            classification = np.zeros(image.shape[:2], dtype=np.uint8)
            
            # Classify based on NDVI and color
            # 0: Non-forest, 1: Forest, 2: Water, 3: Urban, 4: Agriculture
            
            # Forest: High NDVI
            forest_mask = ndvi > self.ndvi_threshold
            classification[forest_mask] = 1
            
            # Water: Low NDVI, low variance
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray_std = filters.sobel(gray)
            water_mask = (ndvi < 0.15) & (gray_std < 10)
            classification[water_mask] = 2
            
            # Urban: Medium NDVI, high texture
            urban_mask = (ndvi >= 0.15) & (ndvi < 0.3) & (gray_std > 20)
            classification[urban_mask] = 3
            
            # Agriculture: Medium NDVI, regular patterns
            agri_mask = (ndvi >= 0.3) & (ndvi < 0.5) & ~forest_mask & ~urban_mask
            classification[agri_mask] = 4
            
            # Calculate percentages
            total_pixels = classification.size
            class_percentages = {
                'forest': np.sum(classification == 1) / total_pixels * 100,
                'water': np.sum(classification == 2) / total_pixels * 100,
                'urban': np.sum(classification == 3) / total_pixels * 100,
                'agriculture': np.sum(classification == 4) / total_pixels * 100,
                'other': np.sum(classification == 0) / total_pixels * 100
            }
            
            return {
                'classification_map': classification,
                'class_percentages': class_percentages,
                'features': features
            }
            
        except Exception as e:
            logger.error(f"Error classifying land cover: {e}")
            return None
    
    def generate_report(self, image, filename=None):
        """Generate comprehensive analysis report"""
        try:
            # Preprocess
            processed = self.preprocess_image(image)
            if processed is None:
                return None
            
            # Extract features
            segmented = self.segment_image(processed)
            features = self.extract_features(processed, segmented)
            
            # Classify
            classification = self.classify_land_cover(processed)
            
            # Detect changes (if comparing with baseline)
            changes = None
            
            # Generate report content
            report = []
            report.append("=" * 80)
            report.append("DEFORESTATION MONITORING SYSTEM - ANALYSIS REPORT")
            report.append("=" * 80)
            report.append(f"\nReport Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append(f"Analysis ID: DEF-{datetime.now().strftime('%Y%m%d%H%M%S')}")
            
            report.append("\n" + "=" * 80)
            report.append("1. VEGETATION INDICES")
            report.append("=" * 80)
            
            if 'ndvi_mean' in features:
                report.append(f"Mean NDVI: {features['ndvi_mean']:.3f}")
                report.append(f"NDVI Std Dev: {features['ndvi_std']:.3f}")
                report.append(f"Max NDVI: {features['ndvi_max']:.3f}")
                report.append(f"Min NDVI: {features['ndvi_min']:.3f}")
                
                # NDVI interpretation
                if features['ndvi_mean'] > 0.6:
                    report.append("→ NDVI Status: DENSE VEGETATION (Healthy Forest)")
                elif features['ndvi_mean'] > 0.4:
                    report.append("→ NDVI Status: MODERATE VEGETATION")
                elif features['ndvi_mean'] > 0.2:
                    report.append("→ NDVI Status: SPARSE VEGETATION")
                else:
                    report.append("→ NDVI Status: BARE AREA / WATER")
            
            if 'evi_mean' in features:
                report.append(f"Mean EVI: {features['evi_mean']:.3f}")
            
            report.append("\n" + "=" * 80)
            report.append("2. FOREST COVER ANALYSIS")
            report.append("=" * 80)
            
            if 'forest_cover' in features:
                forest_cover = features['forest_cover']
                report.append(f"Estimated Forest Cover: {forest_cover:.2f}%")
                
                # Forest status
                if forest_cover > 70:
                    status = "HEALTHY"
                    color = "GREEN"
                elif forest_cover > 40:
                    status = "MODERATE"
                    color = "YELLOW"
                elif forest_cover > 20:
                    status = "THREATENED"
                    color = "ORANGE"
                else:
                    status = "CRITICAL"
                    color = "RED"
                
                report.append(f"Forest Status: {status} ({color})")
                report.append(f"Forest Region Ratio: {features.get('forest_region_ratio', 0):.1f}%")
            
            report.append("\n" + "=" * 80)
            report.append("3. LAND COVER CLASSIFICATION")
            report.append("=" * 80)
            
            if classification:
                for land_class, percentage in classification['class_percentages'].items():
                    bar = '█' * int(percentage / 5)
                    report.append(f"{land_class.capitalize():12}: {percentage:5.1f}% {bar}")
            
            report.append("\n" + "=" * 80)
            report.append("4. TEXTURE AND STRUCTURE ANALYSIS")
            report.append("=" * 80)
            
            if 'texture_mean' in features:
                report.append(f"Texture Mean: {features['texture_mean']:.4f}")
                report.append(f"Texture Std: {features['texture_std']:.4f}")
            
            if 'edge_density' in features:
                report.append(f"Edge Density: {features['edge_density']:.2%}")
            
            if 'n_regions' in features:
                report.append(f"Number of Segments: {features['n_regions']}")
                report.append(f"Avg Segment Size: {features['avg_region_size']:.0f} pixels")
            
            report.append("\n" + "=" * 80)
            report.append("5. RISK ASSESSMENT")
            report.append("=" * 80)
            
            # Calculate risk score
            risk_score = 0
            risk_factors = []
            
            if 'forest_cover' in features:
                if features['forest_cover'] < 30:
                    risk_score += 40
                    risk_factors.append("Very low forest cover")
                elif features['forest_cover'] < 50:
                    risk_score += 20
                    risk_factors.append("Moderate forest cover")
            
            if 'ndvi_mean' in features:
                if features['ndvi_mean'] < 0.3:
                    risk_score += 30
                    risk_factors.append("Poor vegetation health")
                elif features['ndvi_mean'] < 0.5:
                    risk_score += 15
                    risk_factors.append("Declining vegetation health")
            
            if 'edge_density' in features:
                if features['edge_density'] > 0.3:
                    risk_score += 20
                    risk_factors.append("High fragmentation")
            
            report.append(f"Overall Risk Score: {min(risk_score, 100)}/100")
            
            if risk_score < 30:
                report.append("Risk Level: LOW ✅")
            elif risk_score < 60:
                report.append("Risk Level: MODERATE ⚠️")
            else:
                report.append("Risk Level: HIGH 🔴")
            
            if risk_factors:
                report.append("\nRisk Factors:")
                for factor in risk_factors:
                    report.append(f"  • {factor}")
            
            report.append("\n" + "=" * 80)
            report.append("6. RECOMMENDATIONS")
            report.append("=" * 80)
            
            if risk_score >= 60:
                report.append("🔴 URGENT INTERVENTION REQUIRED:")
                report.append("  • Deploy immediate ground patrol teams")
                report.append("  • Investigate illegal logging activities")
                report.append("  • Notify Kenya Forest Service")
                report.append("  • Increase monitoring frequency to daily")
            elif risk_score >= 30:
                report.append("🟡 PROACTIVE MEASURES RECOMMENDED:")
                report.append("  • Increase surveillance in high-risk areas")
                report.append("  • Review conservation measures")
                report.append("  • Community awareness programs")
                report.append("  • Schedule drone overflights weekly")
            else:
                report.append("✅ MAINTAIN CURRENT PRACTICES:")
                report.append("  • Continue regular monitoring")
                report.append("  • Document as baseline data")
                report.append("  • Share best practices with other regions")
            
            report.append("\n" + "=" * 80)
            report.append("END OF REPORT")
            report.append("=" * 80)
            
            # Save report
            if filename is None:
                filename = f"deforestation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            report_path = os.path.join(tempfile.gettempdir(), filename)
            with open(report_path, 'w') as f:
                f.write('\n'.join(report))
            
            return report_path
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return None
    
    def batch_process(self, image_paths):
        """Process multiple images in batch"""
        results = []
        
        for path in image_paths:
            try:
                image = cv2.imread(path)
                if image is not None:
                    features = self.extract_features(image)
                    results.append({
                        'path': path,
                        'features': features,
                        'timestamp': datetime.now()
                    })
            except Exception as e:
                logger.error(f"Error processing {path}: {e}")
        
        return results
