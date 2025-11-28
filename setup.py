#!/usr/bin/env python3
"""
Voice Development Wrapper - Quick Setup
Automated setup and configuration script
"""

import os
import sys
import subprocess
from pathlib import Path
import yaml


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")


def run_command(cmd, description):
    """Run a shell command with description"""
    print(f"→ {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e.stderr}")
        return False


def check_python_version():
    """Check Python version"""
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    
    print("✓ Python version OK")
    return True


def create_virtual_environment():
    """Create Python virtual environment"""
    print_header("Setting Up Virtual Environment")
    
    venv_path = Path(__file__).parent.parent / "venv"
    
    if venv_path.exists():
        print("Virtual environment already exists")
        return True
    
    if not run_command("python -m venv venv", "Creating virtual environment"):
        return False
    
    print(f"\n✓ Virtual environment created at: {venv_path}")
    print("\nActivate it with:")
    print("  • Linux/Mac: source venv/bin/activate")
    print("  • Windows: venv\\Scripts\\activate")
    
    return True


def install_dependencies():
    """Install Python dependencies"""
    print_header("Installing Dependencies")
    
    req_file = Path(__file__).parent / "requirements.txt"
    
    if not req_file.exists():
        print(f"❌ Requirements file not found: {req_file}")
        return False
    
    # Determine pip command
    pip_cmd = "pip" if sys.platform == "win32" else "pip3"
    
    commands = [
        (f"{pip_cmd} install --upgrade pip", "Upgrading pip"),
        (f"{pip_cmd} install -r {req_file}", "Installing Python packages")
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    
    print("\n✓ All dependencies installed")
    return True


def configure_api_keys():
    """Configure API keys"""
    print_header("Configuring API Keys")
    
    config_file = Path(__file__).parent.parent / "config" / "settings.yaml"
    env_file = Path(__file__).parent.parent / ".env"
    
    print("You'll need API keys for:")
    print("  • Anthropic (Claude)")
    print("  • OpenAI (Whisper STT + TTS)")
    print()
    
    configure = input("Configure API keys now? (y/n): ").lower() == 'y'
    
    if not configure:
        print("\nSkipping API key configuration.")
        print("You can configure them later by:")
        print("  1. Editing config/settings.yaml")
        print("  2. Or setting environment variables")
        return True
    
    # Get API keys
    anthropic_key = input("\nEnter your Anthropic API key: ").strip()
    openai_key = input("Enter your OpenAI API key: ").strip()
    
    # Update config file
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    config['apis']['anthropic_key'] = anthropic_key
    config['apis']['openai_key'] = openai_key
    
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print(f"\n✓ API keys saved to {config_file}")
    
    # Also create .env file
    with open(env_file, 'w') as f:
        f.write(f"ANTHROPIC_API_KEY={anthropic_key}\n")
        f.write(f"OPENAI_API_KEY={openai_key}\n")
    
    print(f"✓ Environment variables saved to {env_file}")
    
    return True


def setup_vscode_extension():
    """Setup VS Code extension"""
    print_header("Setting Up VS Code Extension")
    
    ext_dir = Path(__file__).parent.parent / "vscode-extension"
    
    if not (ext_dir / "package.json").exists():
        print("❌ VS Code extension files not found")
        return False
    
    setup = input("Install VS Code extension dependencies? (y/n): ").lower() == 'y'
    
    if not setup:
        print("Skipping VS Code extension setup")
        return True
    
    os.chdir(ext_dir)
    
    commands = [
        ("npm install", "Installing Node.js dependencies"),
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            print("Note: You may need to install Node.js first")
            return False
    
    print("\n✓ VS Code extension ready")
    print("\nTo install the extension in VS Code:")
    print("  1. Open VS Code")
    print("  2. Press Ctrl+Shift+P (Cmd+Shift+P on Mac)")
    print("  3. Type 'Extensions: Install from VSIX'")
    print("  4. Navigate to vscode-extension/ and select the .vsix file")
    
    return True


def test_installation():
    """Test the installation"""
    print_header("Testing Installation")
    
    print("Testing core services...")
    
    # Test imports
    try:
        sys.path.append(str(Path(__file__).parent.parent / "core"))
        from voice_manager import VoiceManager
        print("✓ Voice Manager imports successfully")
        
        sys.path.append(str(Path(__file__).parent.parent / "claude-bridge"))
        from api_client import ClaudeAPIClient
        print("✓ Claude API Client imports successfully")
        
        print("\n✓ All core modules import successfully")
        return True
        
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False


def print_next_steps():
    """Print next steps"""
    print_header("Setup Complete! 🎉")
    
    print("Your voice development wrapper is ready to use!\n")
    
    print("📝 Next Steps:\n")
    
    print("1. Start the voice server:")
    print("   python claude-bridge/bridge_server.py\n")
    
    print("2. Launch the web interface:")
    print("   python web-interface/app.py\n")
    
    print("3. Use the VS Code extension:")
    print("   Install it from vscode-extension/ directory\n")
    
    print("4. Deploy to Hugging Face Spaces:")
    print("   python deployment/spaces_config.py\n")
    
    print("📚 Documentation:")
    print("   Check README.md for detailed usage instructions\n")
    
    print("💡 Tips:")
    print("   • Use Ctrl+Shift+V in VS Code for voice mode")
    print("   • Web interface runs on http://localhost:7860")
    print("   • WebSocket server runs on ws://localhost:8766")


def main():
    """Main setup function"""
    print_header("Voice Development Wrapper - Setup")
    
    steps = [
        ("Python Version Check", check_python_version),
        ("Virtual Environment", create_virtual_environment),
        ("Dependencies", install_dependencies),
        ("API Configuration", configure_api_keys),
        ("VS Code Extension", setup_vscode_extension),
        ("Installation Test", test_installation),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            print("Please fix the errors and run setup again")
            sys.exit(1)
    
    print_next_steps()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
