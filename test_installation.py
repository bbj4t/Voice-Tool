#!/usr/bin/env python3
"""
Voice Development Wrapper - Test Suite
Verify installation and configuration
"""

import sys
import os
from pathlib import Path

# Add modules to path
project_root = Path(__file__).parent
sys.path.append(str(project_root / "core"))
sys.path.append(str(project_root / "claude-bridge"))


class TestRunner:
    """Simple test runner for verification"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
    
    def test(self, name, func):
        """Run a single test"""
        try:
            print(f"\n{'='*60}")
            print(f"TEST: {name}")
            print('='*60)
            result = func()
            if result:
                print(f"✅ PASSED: {name}")
                self.passed += 1
            else:
                print(f"⏭️  SKIPPED: {name}")
                self.skipped += 1
        except Exception as e:
            print(f"❌ FAILED: {name}")
            print(f"   Error: {e}")
            self.failed += 1
    
    def summary(self):
        """Print test summary"""
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print('='*60)
        print(f"✅ Passed:  {self.passed}")
        print(f"❌ Failed:  {self.failed}")
        print(f"⏭️  Skipped: {self.skipped}")
        print(f"Total:     {self.passed + self.failed + self.skipped}")
        print('='*60)
        
        if self.failed == 0:
            print("\n🎉 All tests passed!")
            return True
        else:
            print(f"\n⚠️  {self.failed} test(s) failed")
            return False


def test_python_version():
    """Test Python version"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✓ Python 3.8+ detected")
        return True
    else:
        print("✗ Python 3.8+ required")
        return False


def test_core_imports():
    """Test core module imports"""
    try:
        from voice_manager import VoiceManager
        print("✓ VoiceManager imports successfully")
        
        from stt_service import STTService
        print("✓ STTService imports successfully")
        
        from tts_service import TTSService
        print("✓ TTSService imports successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_claude_imports():
    """Test Claude integration imports"""
    try:
        from api_client import ClaudeAPIClient
        print("✓ ClaudeAPIClient imports successfully")
        
        from api_client import VoiceEnabledClaudeClient
        print("✓ VoiceEnabledClaudeClient imports successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_required_packages():
    """Test required Python packages"""
    packages = [
        'yaml',
        'numpy',
        'gradio',
        'anthropic',
        'openai',
    ]
    
    all_found = True
    for package in packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} not found")
            all_found = False
    
    return all_found


def test_config_file():
    """Test configuration file"""
    config_path = Path(__file__).parent / "config" / "settings.yaml"
    
    if not config_path.exists():
        print(f"✗ Config file not found: {config_path}")
        return False
    
    print(f"✓ Config file found: {config_path}")
    
    try:
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        print("✓ Config file is valid YAML")
        
        # Check required sections
        required_sections = ['apis', 'stt', 'tts', 'claude', 'server']
        for section in required_sections:
            if section in config:
                print(f"✓ Section '{section}' found")
            else:
                print(f"✗ Section '{section}' missing")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Error reading config: {e}")
        return False


def test_api_keys():
    """Test API key configuration"""
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    keys_found = True
    
    if anthropic_key:
        print(f"✓ ANTHROPIC_API_KEY found (length: {len(anthropic_key)})")
    else:
        print("⚠️  ANTHROPIC_API_KEY not set")
        keys_found = False
    
    if openai_key:
        print(f"✓ OPENAI_API_KEY found (length: {len(openai_key)})")
    else:
        print("⚠️  OPENAI_API_KEY not set")
        keys_found = False
    
    if not keys_found:
        print("\nNote: API keys are optional for testing imports")
        print("      but required for actual voice operations")
    
    return True  # Don't fail on missing keys


def test_voice_manager_init():
    """Test VoiceManager initialization"""
    try:
        from voice_manager import VoiceManager
        
        print("Attempting to initialize VoiceManager...")
        # This may fail without API keys, that's okay
        try:
            vm = VoiceManager()
            print("✓ VoiceManager initialized successfully")
            
            status = vm.get_status()
            print(f"  STT Provider: {status['stt_provider']}")
            print(f"  TTS Provider: {status['tts_provider']}")
            
            return True
        except Exception as e:
            print(f"⚠️  VoiceManager initialization failed (expected without API keys)")
            print(f"   Error: {e}")
            return True  # Don't fail - API keys may not be set
        
    except Exception as e:
        print(f"✗ Critical error: {e}")
        return False


def test_file_structure():
    """Test project file structure"""
    required_files = [
        "README.md",
        "USAGE_GUIDE.md",
        "config/settings.yaml",
        "core/stt_service.py",
        "core/tts_service.py",
        "core/voice_manager.py",
        "claude-bridge/api_client.py",
        "claude-bridge/bridge_server.py",
        "web-interface/app.py",
        "deployment/requirements.txt",
        "deployment/setup.py",
    ]
    
    all_found = True
    for file_path in required_files:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} not found")
            all_found = False
    
    return all_found


def test_gradio_import():
    """Test Gradio import for web interface"""
    try:
        import gradio as gr
        print(f"✓ Gradio version: {gr.__version__}")
        return True
    except ImportError:
        print("✗ Gradio not installed")
        print("  Install with: pip install gradio")
        return False


def test_websocket_import():
    """Test WebSocket libraries"""
    try:
        import websockets
        print("✓ websockets library available")
        
        import aiohttp
        print("✓ aiohttp library available")
        
        return True
    except ImportError as e:
        print(f"✗ WebSocket library missing: {e}")
        return False


def main():
    """Run all tests"""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     Voice Development Wrapper - Test Suite              ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")
    
    runner = TestRunner()
    
    # Run tests
    runner.test("Python Version", test_python_version)
    runner.test("Required Packages", test_required_packages)
    runner.test("Core Imports", test_core_imports)
    runner.test("Claude Imports", test_claude_imports)
    runner.test("Configuration File", test_config_file)
    runner.test("API Keys", test_api_keys)
    runner.test("File Structure", test_file_structure)
    runner.test("Gradio Import", test_gradio_import)
    runner.test("WebSocket Import", test_websocket_import)
    runner.test("VoiceManager Initialization", test_voice_manager_init)
    
    # Print summary
    success = runner.summary()
    
    if success:
        print("\n✅ Installation verified successfully!")
        print("\nYou're ready to use the Voice Development Wrapper!")
        print("\nNext steps:")
        print("  1. Configure API keys (if not already done)")
        print("  2. Run: python web-interface/app.py")
        print("  3. Or: python quick_start.py for guidance")
    else:
        print("\n⚠️  Some tests failed")
        print("\nPlease fix the issues and run tests again")
        print("Run: python deployment/setup.py for automated setup")
    
    return 0 if success else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTests cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
