"""
Facial Landmarks Detector for Realistic Face Mouth Detection
Uses dlib and MediaPipe for accurate mouth positioning on photorealistic faces
"""

import cv2
import numpy as np
import os

# Try to import facial landmark libraries
try:
    import dlib
    DLIB_AVAILABLE = True
except ImportError:
    print("⚠️ dlib not installed. Run: pip install dlib")
    DLIB_AVAILABLE = False

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    print("⚠️ MediaPipe not installed. Run: pip install mediapipe")
    MEDIAPIPE_AVAILABLE = False


class FacialLandmarksDetector:
    def __init__(self):
        self.dlib_detector = None
        self.dlib_predictor = None
        self.mp_face_mesh = None
        self.mp_face_detection = None
        
        # Initialize dlib if available
        if DLIB_AVAILABLE:
            try:
                self.dlib_detector = dlib.get_frontal_face_detector()
                # Look for the predictor file in common locations
                predictor_paths = [
                    "shape_predictor_68_face_landmarks.dat",
                    os.path.join(os.path.dirname(__file__), "shape_predictor_68_face_landmarks.dat"),
                    os.path.join(os.path.dirname(__file__), "..", "models", "shape_predictor_68_face_landmarks.dat"),
                    "/usr/local/share/dlib/shape_predictor_68_face_landmarks.dat",
                ]
                
                predictor_found = False
                for path in predictor_paths:
                    if os.path.exists(path):
                        self.dlib_predictor = dlib.shape_predictor(path)
                        predictor_found = True
                        print(f"✅ Loaded dlib predictor from: {path}")
                        break
                
                if not predictor_found:
                    print("⚠️ dlib shape predictor file not found. Download from:")
                    print("   http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")
                    self.dlib_predictor = None
                    
            except Exception as e:
                print(f"⚠️ Error initializing dlib: {e}")
                self.dlib_detector = None
                self.dlib_predictor = None
        
        # Initialize MediaPipe if available
        if MEDIAPIPE_AVAILABLE:
            try:
                mp_face = mp.solutions.face_mesh
                self.mp_face_mesh = mp_face.FaceMesh(
                    static_image_mode=True,
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5
                )
                
                mp_detection = mp.solutions.face_detection
                self.mp_face_detection = mp_detection.FaceDetection(
                    model_selection=1,  # Use full-range model
                    min_detection_confidence=0.5
                )
                print("✅ MediaPipe initialized successfully")
            except Exception as e:
                print(f"⚠️ Error initializing MediaPipe: {e}")
                self.mp_face_mesh = None
                self.mp_face_detection = None
    
    def detect_mouth_dlib(self, image_array):
        """
        Use dlib to detect mouth position using 68 facial landmarks
        Points 48-68 specifically correspond to the mouth region
        """
        if not DLIB_AVAILABLE or self.dlib_detector is None or self.dlib_predictor is None:
            return None
        
        try:
            # Convert to RGB if needed
            if image_array.shape[2] == 4:
                rgb_image = image_array[:, :, :3]
            else:
                rgb_image = image_array
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
            
            # Detect faces
            faces = self.dlib_detector(gray)
            
            if len(faces) > 0:
                # Get the first face
                face = faces[0]
                
                # Get facial landmarks
                landmarks = self.dlib_predictor(gray, face)
                
                # Extract mouth points (landmarks 48-67, 0-indexed so 48-68 in 1-indexed)
                mouth_points = []
                for i in range(48, 68):
                    x = landmarks.part(i).x
                    y = landmarks.part(i).y
                    mouth_points.append((x, y))
                
                # Calculate mouth center
                mouth_center = np.mean(mouth_points, axis=0)
                
                # Also get mouth bounds for size estimation
                mouth_xs = [p[0] for p in mouth_points]
                mouth_ys = [p[1] for p in mouth_points]
                mouth_bounds = {
                    'left': min(mouth_xs),
                    'right': max(mouth_xs),
                    'top': min(mouth_ys),
                    'bottom': max(mouth_ys),
                    'width': max(mouth_xs) - min(mouth_xs),
                    'height': max(mouth_ys) - min(mouth_ys)
                }
                
                print(f"🎯 dlib mouth detection: center=({int(mouth_center[0])}, {int(mouth_center[1])})")
                
                return {
                    'center': (int(mouth_center[0]), int(mouth_center[1])),
                    'bounds': mouth_bounds,
                    'points': mouth_points,
                    'method': 'dlib_68_landmarks'
                }
            else:
                print("⚠️ dlib: No faces detected")
                return None
                
        except Exception as e:
            print(f"⚠️ dlib detection error: {e}")
            return None
    
    def detect_mouth_mediapipe(self, image_array):
        """
        Use MediaPipe Face Mesh to detect mouth position
        MediaPipe provides 468 3D face landmarks
        """
        if not MEDIAPIPE_AVAILABLE or self.mp_face_mesh is None:
            return None
        
        try:
            # Convert to RGB if needed
            if image_array.shape[2] == 4:
                rgb_image = image_array[:, :, :3]
            else:
                rgb_image = image_array
            
            # Process with MediaPipe
            results = self.mp_face_mesh.process(rgb_image)
            
            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                
                # MediaPipe mouth landmarks indices
                # Upper lip: 61, 84, 17, 314, 405, 306, 311, 308, 415, 310, 311, 312, 13, 82, 81, 80, 78
                # Lower lip: 61, 84, 17, 314, 405, 306, 375, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95
                # We'll use a subset for simplicity
                mouth_indices = [
                    13, 14, 17, 18, 61, 78, 80, 81, 82, 84, 87, 88, 95,
                    178, 191, 269, 270, 271, 272, 308, 310, 311, 312,
                    314, 317, 318, 324, 375, 402, 405, 415
                ]
                
                h, w = image_array.shape[:2]
                mouth_points = []
                
                for idx in mouth_indices:
                    if idx < len(face_landmarks.landmark):
                        landmark = face_landmarks.landmark[idx]
                        x = int(landmark.x * w)
                        y = int(landmark.y * h)
                        mouth_points.append((x, y))
                
                if mouth_points:
                    # Calculate mouth center
                    mouth_center = np.mean(mouth_points, axis=0)
                    
                    # Get mouth bounds
                    mouth_xs = [p[0] for p in mouth_points]
                    mouth_ys = [p[1] for p in mouth_points]
                    mouth_bounds = {
                        'left': min(mouth_xs),
                        'right': max(mouth_xs),
                        'top': min(mouth_ys),
                        'bottom': max(mouth_ys),
                        'width': max(mouth_xs) - min(mouth_xs),
                        'height': max(mouth_ys) - min(mouth_ys)
                    }
                    
                    print(f"🎯 MediaPipe mouth detection: center=({int(mouth_center[0])}, {int(mouth_center[1])})")
                    
                    return {
                        'center': (int(mouth_center[0]), int(mouth_center[1])),
                        'bounds': mouth_bounds,
                        'points': mouth_points,
                        'method': 'mediapipe_face_mesh'
                    }
            
            print("⚠️ MediaPipe: No faces detected")
            return None
            
        except Exception as e:
            print(f"⚠️ MediaPipe detection error: {e}")
            return None
    
    def detect_mouth_simple(self, image_array):
        """
        Simple mouth detection using MediaPipe Face Detection (6 landmarks)
        This is faster but less accurate than Face Mesh
        """
        if not MEDIAPIPE_AVAILABLE or self.mp_face_detection is None:
            return None
        
        try:
            # Convert to RGB if needed
            if image_array.shape[2] == 4:
                rgb_image = image_array[:, :, :3]
            else:
                rgb_image = image_array
            
            # Process with MediaPipe Face Detection
            results = self.mp_face_detection.process(rgb_image)
            
            if results.detections:
                detection = results.detections[0]
                h, w = image_array.shape[:2]
                
                # Get the mouth center landmark (landmark 3)
                mouth_landmark = detection.location_data.relative_keypoints[3]
                mouth_x = int(mouth_landmark.x * w)
                mouth_y = int(mouth_landmark.y * h)
                
                print(f"🎯 MediaPipe simple detection: mouth at ({mouth_x}, {mouth_y})")
                
                return {
                    'center': (mouth_x, mouth_y),
                    'bounds': None,  # Simple detection doesn't provide bounds
                    'points': [(mouth_x, mouth_y)],
                    'method': 'mediapipe_simple'
                }
            
            print("⚠️ MediaPipe simple: No faces detected")
            return None
            
        except Exception as e:
            print(f"⚠️ MediaPipe simple detection error: {e}")
            return None
    
    def detect_mouth(self, image_array, prefer_method='auto'):
        """
        Main detection method that tries multiple approaches
        
        Args:
            image_array: Input image as numpy array
            prefer_method: 'dlib', 'mediapipe', 'simple', or 'auto'
        
        Returns:
            Dictionary with mouth detection results or None
        """
        print(f"🔍 Attempting facial landmark mouth detection (prefer: {prefer_method})")
        
        # Try methods based on preference
        if prefer_method == 'dlib':
            result = self.detect_mouth_dlib(image_array)
            if result:
                return result
        elif prefer_method == 'mediapipe':
            result = self.detect_mouth_mediapipe(image_array)
            if result:
                return result
        elif prefer_method == 'simple':
            result = self.detect_mouth_simple(image_array)
            if result:
                return result
        
        # Auto mode: try all methods in order of accuracy
        if prefer_method == 'auto' or result is None:
            # Try dlib first (most accurate for realistic faces)
            result = self.detect_mouth_dlib(image_array)
            if result:
                return result
            
            # Try MediaPipe Face Mesh (very detailed)
            result = self.detect_mouth_mediapipe(image_array)
            if result:
                return result
            
            # Try simple MediaPipe detection (fastest)
            result = self.detect_mouth_simple(image_array)
            if result:
                return result
        
        print("⚠️ All facial landmark detection methods failed")
        return None
    
    def is_available(self):
        """Check if any facial landmark detection is available"""
        return (
            (DLIB_AVAILABLE and self.dlib_detector is not None and self.dlib_predictor is not None) or
            (MEDIAPIPE_AVAILABLE and (self.mp_face_mesh is not None or self.mp_face_detection is not None))
        )