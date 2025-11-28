#!/usr/bin/env python3
"""
Quick Start - Voice Development Wrapper
Get up and running in minutes
"""

import os
import sys
from pathlib import Path

def print_banner():
    banner = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║        🎤 Voice Development Wrapper 🎤                  ║
║                                                          ║
║     Personal Voice Interface for Development            ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""
    print(banner)

def check_requirements():
    """Check if basic requirements are met"""
    print("\n📋 Checking requirements...\n")
    
    # Check Python version
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    
    # Check for required packages
    packages = [
        ('yaml', 'pyyaml'),
        ('numpy', 'numpy'),
    ]
    
    missing = []
    for import_name, package_name in packages:
        try:
            __import__(import_name)
            print(f"✓ {package_name}")
        except ImportError:
            print(f"✗ {package_name} not installed")
            missing.append(package_name)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("\nInstall with:")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    return True

def setup_api_keys():
    """Guide user through API key setup"""
    print("\n🔑 API Key Configuration\n")
    
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not anthropic_key:
        print("⚠️  ANTHROPIC_API_KEY not found")
        print("   Get your key from: https://console.anthropic.com/")
        
    if not openai_key:
        print("⚠️  OPENAI_API_KEY not found")
        print("   Get your key from: https://platform.openai.com/api-keys")
    
    if not (anthropic_key and openai_key):
        print("\n📝 To set API keys:")
        print("   1. Create a .env file in the project root")
        print("   2. Add:")
        print("      ANTHROPIC_API_KEY=your_key_here")
        print("      OPENAI_API_KEY=your_key_here")
        print("\n   Or set environment variables:")
        print("      export ANTHROPIC_API_KEY=your_key")
        print("      export OPENAI_API_KEY=your_key")
        return False
    
    print("✓ API keys configured")
    return True

def show_quick_commands():
    """Display quick start commands"""
    print("\n🚀 Quick Start Commands\n")
    
    commands = [
        ("Web Interface", "python web-interface/app.py"),
        ("Voice Server", "python claude-bridge/bridge_server.py"),
        ("Examples", "python examples/example_usage.py"),
        ("Setup Script", "python deployment/setup.py"),
    ]
    
    for name, cmd in commands:
        print(f"  {name}:")
        print(f"    {cmd}\n")

def show_features():
    """Show available features"""
    print("\n✨ Available Features\n")
    
    features = [
        "🎤 Speech-to-Text (Whisper)",
        "🔊 Text-to-Speech (OpenAI TTS)",
        "🤖 Claude Conversations",
        "💻 VS Code Extension",
        "🌐 Web Interface (Gradio)",
        "🔌 WebSocket API",
        "📡 HTTP REST API",
        "☁️  Hugging Face Spaces Ready",
    ]
    
    for feature in features:
        print(f"  {feature}")

def show_next_steps():
    """Show recommended next steps"""
    print("\n📚 Next Steps\n")
    
    steps = [
        "1. Install dependencies:",
        "   pip install -r deployment/requirements.txt",
        "",
        "2. Configure API keys (see above)",
        "",
        "3. Run the web interface:",
        "   python web-interface/app.py",
        "",
        "4. Or run the full setup:",
        "   python deployment/setup.py",
        "",
        "5. Read the usage guide:",
        "   Check USAGE_GUIDE.md for detailed instructions",
    ]
    
    for step in steps:
        print(f"  {step}")

def main():
    """Main quick start function"""
    print_banner()
    
    print("Welcome to Voice Development Wrapper!")
    print("This personal tool brings voice capabilities to your development workflow.\n")
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Please install missing requirements first")
        print("   Run: pip install -r deployment/requirements.txt")
        sys.exit(1)
    
    # Check API keys
    api_keys_ok = setup_api_keys()
    
    # Show features
    show_features()
    
    # Show quick commands
    show_quick_commands()
    
    # Show next steps
    if not api_keys_ok:
        show_next_steps()
    else:
        print("\n✅ Everything looks good!")
        print("\nYou're ready to go! Try running:")
        print("  python web-interface/app.py")
    
    print("\n" + "="*60)
    print("For detailed documentation, see:")
    print("  • README.md - Project overview")
    print("  • USAGE_GUIDE.md - Comprehensive guide")
    print("  • examples/example_usage.py - Code examples")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
