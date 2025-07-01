#!/usr/bin/env python3
"""
Setup verification script for South Park Animator
Checks all dependencies and creates required directories
"""

import sys
import os
import subprocess
import importlib

def check_python_packages():
    """Check required Python packages"""
    required_packages = [
        'cv2',          # opencv-python
        'PIL',          # Pillow
        'numpy',        # numpy
        'pydub',        # pydub
        'flask',        # Flask
        'flask_cors'    # flask-cors
    ]
    
    print("🔍 Checking Python packages...")
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing_packages.append(package)
    
    return missing_packages

def check_system_tools():
    """Check required system tools"""
    tools = ['ffmpeg']
    
    print("\n🔍 Checking system tools...")
    missing_tools = []
    
    for tool in tools:
        try:
            result = subprocess.run([tool, '-version'], 
                                  capture_output=True, text=True, check=True)
            print(f"  ✅ {tool}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"  ❌ {tool} - MISSING")
            missing_tools.append(tool)
    
    return missing_tools

def check_project_structure():
    """Check and create required directories"""
    print("\n🔍 Checking project structure...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    required_dirs = [
        'backend/core',
        'backend/assets/mouth_sprites',
        'backend/tests',
        'backend/temp',
        'backend/output'
    ]
    
    for dir_path in required_dirs:
        full_path = os.path.join(base_dir, dir_path)
        if os.path.exists(full_path):
            print(f"  ✅ {dir_path}")
        else:
            print(f"  📁 Creating {dir_path}")
            os.makedirs(full_path, exist_ok=True)

def check_mouth_sprites():
    """Check if mouth sprites exist"""
    print("\n🔍 Checking mouth sprites...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sprites_dir = os.path.join(base_dir, 'backend', 'assets', 'mouth_sprites')
    
    expected_sprites = [
        'southparkClosed(M_B_P).png',
        'southparkSmall(E_I).png',
        'southparkMedium(E_EH).png',
        'southparkWide(A_AH).png',
        'southparkRound(O_OO).png',
        'southparkTeeth(F_V).png',
        'southparkSpecial(L_TH_R).png'
    ]
    
    missing_sprites = []
    for sprite in expected_sprites:
        sprite_path = os.path.join(sprites_dir, sprite)
        if os.path.exists(sprite_path):
            print(f"  ✅ {sprite}")
        else:
            print(f"  ❌ {sprite} - MISSING")
            missing_sprites.append(sprite)
    
    if missing_sprites:
        print(f"\n  💡 Run: python backend/core/generate_mouth_sprites.py")
    
    return missing_sprites

def run_basic_test():
    """Run basic functionality test"""
    print("\n🔍 Running basic tests...")
    
    try:
        # Add backend to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        
        # Test sprite manager
        from core.mouth_sprite_manager import MouthSpriteManager
        sprite_manager = MouthSpriteManager()
        print("  ✅ MouthSpriteManager initialization")
        
        # Test phoneme detector
        from core.phoneme_detector import PhonemeDetector
        phoneme_detector = PhonemeDetector()
        mapping = phoneme_detector.get_rhubarb_viseme_mapping()
        assert len(mapping) == 9, "Should have 9 viseme codes"
        print("  ✅ PhonemeDetector viseme mapping")
        
        # Test animator
        from core.animator import TalkingHeadAnimator
        animator = TalkingHeadAnimator()
        print("  ✅ TalkingHeadAnimator initialization")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False

def main():
    print("🎬 South Park Animator Setup Check\n")
    
    # Check all components
    missing_packages = check_python_packages()
    missing_tools = check_system_tools()
    check_project_structure()
    missing_sprites = check_mouth_sprites()
    test_passed = run_basic_test()
    
    # Summary
    print("\n" + "="*50)
    print("📋 SETUP SUMMARY")
    print("="*50)
    
    if missing_packages:
        print(f"❌ Missing Python packages: {', '.join(missing_packages)}")
        print("   💡 Run: pip install -r requirements.txt")
    else:
        print("✅ All Python packages installed")
    
    if missing_tools:
        print(f"❌ Missing system tools: {', '.join(missing_tools)}")
        print("   💡 Install FFmpeg: brew install ffmpeg (macOS) or apt install ffmpeg (Ubuntu)")
    else:
        print("✅ All system tools available")
    
    if missing_sprites:
        print(f"❌ Missing {len(missing_sprites)} mouth sprites")
        print("   💡 Run: python backend/core/generate_mouth_sprites.py")
    else:
        print("✅ All mouth sprites present")
    
    if test_passed:
        print("✅ Basic functionality tests passed")
    else:
        print("❌ Basic functionality tests failed")
    
    # Final verdict
    all_good = not missing_packages and not missing_tools and not missing_sprites and test_passed
    
    if all_good:
        print("\n🎉 READY TO GO! You can now run:")
        print("   python backend/cli_test.py --style standard --image your_image.png --audio your_audio.wav")
    else:
        print("\n⚠️  Setup incomplete. Please address the issues above.")
    
    return 0 if all_good else 1

if __name__ == '__main__':
    sys.exit(main())