#!/usr/bin/env python3
"""
REGON MCP Server - Executable Builder
=====================================

Professional-grade script for building standalone executables from the REGON MCP Server.
Creates production-ready .exe files using PyInstaller for both stdio and HTTP server variants.

Author: REGON MCP Server Project
Date: August 2025
Version: 2.0.0

Usage:
    python make_exe.py [OPTIONS]
    
Options:
    -y, --yes           Auto-confirm cleanup operations
    -v, --verbose       Enable verbose output
    --no-test          Skip executable testing
    --help             Show this help message
"""

import argparse
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple
import time


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


class ProgressBar:
    """Simple progress bar for visual feedback."""
    
    def __init__(self, total: int, description: str = "", width: int = 50):
        self.total = total
        self.current = 0
        self.description = description
        self.width = width
        self.start_time = time.time()
    
    def update(self, step: int = 1, description: str = None):
        """Update progress bar."""
        self.current += step
        if description:
            self.description = description
        
        percentage = (self.current / self.total) * 100
        filled = int(self.width * self.current // self.total)
        bar = '█' * filled + '░' * (self.width - filled)
        
        elapsed = time.time() - self.start_time
        eta = (elapsed / self.current * (self.total - self.current)) if self.current > 0 else 0
        
        print(f'\r{Colors.CYAN}{self.description:<30}{Colors.RESET} |{Colors.GREEN}{bar}{Colors.RESET}| '
              f'{percentage:6.1f}% ({self.current}/{self.total}) ETA: {eta:4.0f}s', end='', flush=True)
        
        if self.current >= self.total:
            print()  # New line when complete


class ExecutableBuilder:
    """
    Professional-grade executable builder for REGON MCP Server.
    
    This class handles the complete build process including:
    - Environment validation
    - File copying and organization
    - PyInstaller execution
    - Executable testing
    - Build verification
    """
    
    # Build configuration constants
    REQUIRED_FILES = ["server.py", "server_http.py"]
    EXECUTABLE_NAMES = {
        "server.py": "regon_mcp_server_stdio.exe",
        "server_http.py": "regon_mcp_server_http.exe"
    }
    
    def __init__(self, auto_confirm: bool = False, verbose: bool = False, skip_test: bool = False):
        """
        Initialize the executable builder.
        
        Args:
            auto_confirm: Automatically confirm cleanup operations
            verbose: Enable verbose logging
            skip_test: Skip executable testing phase
        """
        self.auto_confirm = auto_confirm
        self.verbose = verbose
        self.skip_test = skip_test
        
        # Setup logging
        self._setup_logging()
        
        # Initialize paths
        self._initialize_paths()
        
        # Setup environment
        self._setup_environment()
    
    def _setup_logging(self) -> None:
        """Configure logging based on verbosity level."""
        log_level = logging.DEBUG if self.verbose else logging.INFO
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s' if self.verbose else '%(levelname)s: %(message)s'
        
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('build.log', encoding='utf-8')
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        
        # Suppress PyInstaller verbose output if not in verbose mode
        if not self.verbose:
            logging.getLogger('PyInstaller').setLevel(logging.WARNING)
    
    def _initialize_paths(self) -> None:
        """Initialize and validate all required paths."""
        self.python_path = Path(sys.executable)
        
        # Detect project root from Python executable path
        if '.venv' in str(self.python_path):
            self.project_root = Path(str(self.python_path).split('.venv')[0])
        else:
            self.project_root = Path.cwd()
        
        self.logger.info(f"{Colors.CYAN}Python executable: {Colors.WHITE}{self.python_path}{Colors.RESET}")
        self.logger.info(f"{Colors.CYAN}Project root: {Colors.WHITE}{self.project_root}{Colors.RESET}")
        
        # Define all build paths
        self.source_dir = self.project_root / "regon_mcp_server"
        self.config_dir = self.project_root / "config"
        self.deployment_dir = self.project_root / "production_deployment"
        self.build_src_dir = self.deployment_dir / "src"
        self.dist_dir = self.deployment_dir / "regon_mcp"
        self.build_dir = self.deployment_dir / "build"
        self.spec_dir = self.deployment_dir / "spec"
    
    def _setup_environment(self) -> None:
        """Setup build environment variables."""
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # Ensure UTF-8 encoding for Windows
        if sys.platform == 'win32':
            os.environ['PYTHONLEGACYWINDOWSSTDIO'] = '0'
    
    def validate_environment(self) -> bool:
        """
        Validate build environment and dependencies.
        
        Returns:
            bool: True if environment is valid, False otherwise
        """
        self.logger.info(f"{Colors.BOLD}{Colors.BLUE}🔍 Validating Build Environment{Colors.RESET}")
        
        validation_steps = [
            ("PyInstaller availability", self._check_pyinstaller),
            ("Source files existence", self._check_source_files),
            ("Config directory", self._check_config_directory),
            ("Write permissions", self._check_permissions)
        ]
        
        progress = ProgressBar(len(validation_steps), "Validating environment")
        
        for step_name, check_func in validation_steps:
            try:
                check_func()
                progress.update(1, f"✓ {step_name}")
                self.logger.debug(f"✓ {step_name} - OK")
            except Exception as e:
                progress.update(1, f"✗ {step_name}")
                self.logger.error(f"{Colors.RED}✗ {step_name}: {e}{Colors.RESET}")
                return False
        
        self.logger.info(f"{Colors.GREEN}✓ Environment validation completed successfully{Colors.RESET}")
        return True
    
    def _check_pyinstaller(self) -> None:
        """Check if PyInstaller is available."""
        try:
            import PyInstaller
            self.logger.debug(f"PyInstaller version: {PyInstaller.__version__}")
        except ImportError:
            raise ImportError("PyInstaller not installed. Run: pip install pyinstaller")
    
    def _check_source_files(self) -> None:
        """Validate that all required source files exist."""
        for file_name in self.REQUIRED_FILES:
            file_path = self.source_dir / file_name
            if not file_path.exists():
                raise FileNotFoundError(f"Required source file not found: {file_path}")
    
    def _check_config_directory(self) -> None:
        """Validate config directory exists and contains files."""
        if not self.config_dir.exists():
            raise FileNotFoundError(f"Config directory not found: {self.config_dir}")
        
        config_files = list(self.config_dir.glob("*.json"))
        if not config_files:
            raise FileNotFoundError("No configuration files found in config directory")
    
    def _check_permissions(self) -> None:
        """Check write permissions for deployment directory."""
        if not os.access(self.project_root, os.W_OK):
            raise PermissionError(f"No write permission for project root: {self.project_root}")
    
    def prepare_build_environment(self) -> None:
        """
        Prepare and clean the build environment.
        
        Creates necessary directories and handles cleanup of existing builds.
        """
        self.logger.info(f"{Colors.BOLD}{Colors.BLUE}🏗️  Preparing Build Environment{Colors.RESET}")
        
        # Handle existing deployment directory
        if self.deployment_dir.exists() and any(self.deployment_dir.iterdir()):
            self._handle_existing_deployment()
        
        # Create directory structure
        directories = [
            self.deployment_dir,
            self.build_src_dir,
            self.dist_dir,
            self.dist_dir / "config",
            self.build_dir,
            self.spec_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Created directory: {directory}")
        
        self.logger.info(f"{Colors.GREEN}✓ Build environment prepared{Colors.RESET}")
    
    def _handle_existing_deployment(self) -> None:
        """Handle cleanup of existing deployment directory."""
        if self.auto_confirm:
            self.logger.info(f"{Colors.YELLOW}Auto-confirming cleanup of {self.deployment_dir}{Colors.RESET}")
            confirmation = True
        else:
            print(f"{Colors.YELLOW}Warning: {self.deployment_dir} is not empty.{Colors.RESET}")
            response = input(f"{Colors.CYAN}Clean all existing files? (Y/n): {Colors.RESET}").lower()
            confirmation = response != 'n'
        
        if confirmation:
            self.logger.info(f"{Colors.YELLOW}🧹 Cleaning {self.deployment_dir}...{Colors.RESET}")
            
            items = list(self.deployment_dir.iterdir())
            progress = ProgressBar(len(items), "Cleaning deployment")
            
            for item in items:
                try:
                    if item.is_dir():
                        shutil.rmtree(item)
                        progress.update(1, f"Removed directory: {item.name}")
                    else:
                        item.unlink()
                        progress.update(1, f"Removed file: {item.name}")
                    
                    self.logger.debug(f"Removed: {item}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove {item}: {e}")
                    progress.update(1, f"Failed: {item.name}")
        else:
            self.logger.info(f"{Colors.CYAN}Continuing without cleanup...{Colors.RESET}")
    
    def copy_source_files(self) -> None:
        """
        Copy source files to build directory with error handling.
        """
        self.logger.info(f"{Colors.BOLD}{Colors.BLUE}📁 Copying Source Files{Colors.RESET}")
        
        # Copy Python source files
        python_files = list(self.source_dir.glob("*.py"))
        
        # Also copy .env.example and mcp.json from project root
        additional_files = [
            (self.project_root / ".env.example", self.dist_dir / ".env.example"),
            (self.project_root / "mcp.json", self.dist_dir / "mcp.json")
        ]
        
        total_files = len(python_files) + len(additional_files) + 1  # +1 for config files
        progress = ProgressBar(total_files, "Copying files")
        
        for src_file in python_files:
            try:
                dest_file = self.build_src_dir / src_file.name
                self._copy_file_with_encoding(src_file, dest_file)
                progress.update(1, f"Copied: {src_file.name}")
                self.logger.debug(f"Copied {src_file} → {dest_file}")
            except Exception as e:
                self.logger.error(f"{Colors.RED}Failed to copy {src_file}: {e}{Colors.RESET}")
                raise
        
        # Copy additional configuration files
        for src_file, dest_file in additional_files:
            try:
                if src_file.exists():
                    self._copy_file_with_encoding(src_file, dest_file)
                    progress.update(1, f"Copied: {src_file.name}")
                    self.logger.debug(f"Copied {src_file} → {dest_file}")
                else:
                    self.logger.warning(f"{Colors.YELLOW}File not found, skipping: {src_file}{Colors.RESET}")
                    progress.update(1, f"Skipped: {src_file.name}")
            except Exception as e:
                self.logger.error(f"{Colors.RED}Failed to copy {src_file}: {e}{Colors.RESET}")
                raise
        
        # Copy config files
        config_files = list(self.config_dir.glob("*.json"))
        for config_file in config_files:
            try:
                dest_file = self.dist_dir / "config" / config_file.name
                self._copy_file_with_encoding(config_file, dest_file)
                self.logger.debug(f"Copied config {config_file} → {dest_file}")
            except Exception as e:
                self.logger.error(f"{Colors.RED}Failed to copy config {config_file}: {e}{Colors.RESET}")
                raise
        
        progress.update(1, "Config files copied")
        self.logger.info(f"{Colors.GREEN}✓ Source files copied successfully{Colors.RESET}")
    
    def _copy_file_with_encoding(self, src: Path, dest: Path) -> None:
        """
        Copy file with proper encoding handling.
        
        Args:
            src: Source file path
            dest: Destination file path
        """
        try:
            # Try reading as text first (for Python files)
            if src.suffix == '.py':
                with open(src, 'r', encoding='utf-8') as f_src:
                    content = f_src.read()
                with open(dest, 'w', encoding='utf-8') as f_dest:
                    f_dest.write(content)
            else:
                # Binary copy for other files
                with open(src, 'rb') as f_src:
                    content = f_src.read()
                with open(dest, 'wb') as f_dest:
                    f_dest.write(content)
        except UnicodeDecodeError:
            # Fallback to binary copy
            with open(src, 'rb') as f_src:
                content = f_src.read()
            with open(dest, 'wb') as f_dest:
                f_dest.write(content)
    
    def build_executables(self) -> None:
        """
        Build executables using PyInstaller.
        """
        self.logger.info(f"{Colors.BOLD}{Colors.BLUE}🔨 Building Executables{Colors.RESET}")
        
        # Change to source directory for building
        original_cwd = Path.cwd()
        os.chdir(self.build_src_dir)
        self.logger.debug(f"Changed working directory to: {self.build_src_dir}")
        
        try:
            progress = ProgressBar(len(self.REQUIRED_FILES), "Building executables")
            
            for source_file in self.REQUIRED_FILES:
                exe_name = self.EXECUTABLE_NAMES[source_file]
                progress.update(1, f"Building: {exe_name}")
                
                self.logger.info(f"{Colors.CYAN}Building {exe_name}...{Colors.RESET}")
                self._build_single_executable(source_file, exe_name)
                self.logger.info(f"{Colors.GREEN}✓ {exe_name} built successfully{Colors.RESET}")
            
        finally:
            os.chdir(original_cwd)
            self.logger.debug(f"Restored working directory to: {original_cwd}")
        
        self.logger.info(f"{Colors.GREEN}✓ All executables built successfully{Colors.RESET}")
    
    def _build_single_executable(self, source_file: str, exe_name: str) -> None:
        """
        Build a single executable using PyInstaller.
        
        Args:
            source_file: Source Python file name
            exe_name: Output executable name
        """
        cmd_args = [
            str(self.python_path), "-m", "PyInstaller",
            "--onefile",
            "--name", exe_name.replace('.exe', ''),
            "--distpath", str(self.dist_dir),
            "--workpath", str(self.build_dir),
            "--specpath", str(self.spec_dir),
            "--clean",  # Clean before building
        ]
        
        # Add hidden import for HTTP server variant
        if "http" in source_file.lower() or "http" in exe_name.lower():
            cmd_args.extend(["--hiddenimport", "error_handling"])
        
        cmd_args.append(source_file)
        
        if not self.verbose:
            cmd_args.extend(["--log-level", "WARN"])
        
        self.logger.debug(f"PyInstaller command: {' '.join(cmd_args)}")
        
        try:
            result = subprocess.run(
                cmd_args,
                check=True,
                capture_output=not self.verbose,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, cmd_args)
                
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"PyInstaller timed out building {exe_name}")
        except subprocess.CalledProcessError as e:
            error_msg = f"PyInstaller failed for {exe_name}"
            if hasattr(e, 'stderr') and e.stderr:
                error_msg += f": {e.stderr}"
            raise RuntimeError(error_msg)
    
    def test_executables(self) -> None:
        """
        Test built executables for basic functionality.
        """
        if self.skip_test:
            self.logger.info(f"{Colors.YELLOW}⏭️  Skipping executable testing{Colors.RESET}")
            return
        
        self.logger.info(f"{Colors.BOLD}{Colors.BLUE}🧪 Testing Executables{Colors.RESET}")
        
        executables = list(self.dist_dir.glob("*.exe"))
        progress = ProgressBar(len(executables), "Testing executables")
        
        for exe_path in executables:
            progress.update(1, f"Testing: {exe_path.name}")
            
            try:
                self._test_single_executable(exe_path)
                self.logger.info(f"{Colors.GREEN}✓ {exe_path.name} test passed{Colors.RESET}")
            except Exception as e:
                self.logger.warning(f"{Colors.YELLOW}⚠️  {exe_path.name} test failed: {e}{Colors.RESET}")
        
        self.logger.info(f"{Colors.GREEN}✓ Executable testing completed{Colors.RESET}")
    
    def _test_single_executable(self, exe_path: Path) -> None:
        """
        Test a single executable.
        
        Args:
            exe_path: Path to executable file
        """
        cmd_args = [str(exe_path), "--help"]
        
        try:
            result = subprocess.run(
                cmd_args,
                check=False,  # Don't raise on non-zero exit
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Consider it successful if help text contains expected patterns
            help_patterns = ["usage", "options", "arguments", "help"]
            output = (result.stdout + result.stderr).lower()
            
            if any(pattern in output for pattern in help_patterns):
                self.logger.debug(f"✓ {exe_path.name} help test passed")
            else:
                raise RuntimeError(f"Help output doesn't contain expected patterns")
                
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Executable test timed out")
    
    def generate_build_report(self) -> None:
        """
        Generate a comprehensive build report.
        """
        self.logger.info(f"{Colors.BOLD}{Colors.BLUE}📊 Generating Build Report{Colors.RESET}")
        
        executables = list(self.dist_dir.glob("*.exe"))
        config_files = list((self.dist_dir / "config").glob("*.json"))
        
        # Calculate sizes
        total_size = sum(exe.stat().st_size for exe in executables)
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 Build Complete!{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}Build Summary:{Colors.RESET}")
        print(f"  📁 Output Directory: {Colors.WHITE}{self.dist_dir}{Colors.RESET}")
        print(f"  🗂️  Total Size: {Colors.WHITE}{total_size / (1024*1024):.2f} MB{Colors.RESET}")
        print(f"  📦 Executables Built: {Colors.WHITE}{len(executables)}{Colors.RESET}")
        print(f"  ⚙️  Config Files: {Colors.WHITE}{len(config_files)}{Colors.RESET}")
        
        print(f"\n{Colors.BOLD}Executables:{Colors.RESET}")
        for exe in executables:
            size_mb = exe.stat().st_size / (1024*1024)
            print(f"  {Colors.GREEN}✓{Colors.RESET} {exe.name} ({size_mb:.2f} MB)")
        
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}🔧 Configuration Instructions{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
        
        print(f"\n{Colors.BOLD}1. API Key Configuration:{Colors.RESET}")
        print(f"   Copy {Colors.YELLOW}.env.example{Colors.RESET} to {Colors.YELLOW}.env{Colors.RESET} and configure your API keys:")
        print(f"   {Colors.CYAN}cd {self.dist_dir}{Colors.RESET}")
        print(f"   {Colors.CYAN}copy .env.example .env{Colors.RESET}")
        print(f"   {Colors.CYAN}notepad .env{Colors.RESET}")
        print(f"")
        print(f"   Set your API keys in .env:")
        print(f"   {Colors.YELLOW}# For testing (free test key){Colors.RESET}")
        print(f"   {Colors.WHITE}TEST_API_KEY=abcde12345abcde12345{Colors.RESET}")
        print(f"   {Colors.YELLOW}# For production (your real API key from GUS){Colors.RESET}")
        print(f"   {Colors.WHITE}API_KEY=your_production_api_key_here{Colors.RESET}")
        
        print(f"\n{Colors.BOLD}2. MCP Configuration (Claude Desktop):{Colors.RESET}")
        print(f"   Update your Claude Desktop {Colors.YELLOW}mcp.json{Colors.RESET} configuration:")
        print(f"   Location: {Colors.CYAN}%APPDATA%\\Claude\\mcp.json{Colors.RESET}")
        print(f"")
        print(f"   {Colors.BOLD}For Stdio Server (recommended):{Colors.RESET}")
        print(f"   {Colors.WHITE}{{")
        print(f"     \"mcpServers\": {{")
        print(f"       \"regon-api\": {{")
        print(f"         \"command\": \"{self.dist_dir.as_posix()}/regon_mcp_server_stdio.exe\",")
        print(f"         \"args\": [\"--tools-config\", \"polish\"],")
        print(f"         \"env\": {{")
        print(f"           \"LOG_LEVEL\": \"INFO\"")
        print(f"         }}")
        print(f"       }}")
        print(f"     }}")
        print(f"   }}{Colors.RESET}")
        
        print(f"\n   {Colors.BOLD}For HTTP Server:{Colors.RESET}")
        print(f"   {Colors.WHITE}{{")
        print(f"     \"mcpServers\": {{")
        print(f"       \"regon-api-http\": {{")
        print(f"         \"command\": \"{self.dist_dir.as_posix()}/regon_mcp_server_http.exe\",")
        print(f"         \"args\": [\"--port\", \"8080\", \"--tools-config\", \"polish\"],")
        print(f"         \"env\": {{")
        print(f"           \"LOG_LEVEL\": \"INFO\"")
        print(f"         }}")
        print(f"       }}")
        print(f"     }}")
        print(f"   }}{Colors.RESET}")
        
        print(f"\n{Colors.BOLD}3. Available Tool Configurations:{Colors.RESET}")
        tool_configs = [
            ("minimal", "Basic company search tools only"),
            ("default", "Standard set of tools (recommended)"),
            ("detailed", "Extended tools with detailed information"),
            ("polish", "Polish language interface with full features")
        ]
        
        for config_name, description in tool_configs:
            print(f"   {Colors.CYAN}--tools-config {config_name:<10}{Colors.RESET} {description}")
        
        print(f"\n{Colors.BOLD}4. API Key Sources:{Colors.RESET}")
        print(f"   {Colors.YELLOW}Test API Key:{Colors.RESET} Use default 'abcde12345abcde12345' for testing")
        print(f"   {Colors.YELLOW}Production Key:{Colors.RESET} Register at: https://api.stat.gov.pl/")
        print(f"   {Colors.YELLOW}Documentation:{Colors.RESET} https://api.stat.gov.pl/Home/RegonApi")
        
        print(f"\n{Colors.BOLD}Usage Examples:{Colors.RESET}")
        print(f"  {Colors.CYAN}Test Mode:{Colors.RESET}")
        print(f"    .\\regon_mcp_server_stdio.exe --tools-config polish")
        print(f"  {Colors.CYAN}Production Mode:{Colors.RESET}")
        print(f"    .\\regon_mcp_server_stdio.exe --production --tools-config polish")
        print(f"  {Colors.CYAN}HTTP Server:{Colors.RESET}")
        print(f"    .\\regon_mcp_server_http.exe --port 8080 --tools-config polish")
        print(f"  {Colors.CYAN}Debug Mode:{Colors.RESET}")
        print(f"    .\\regon_mcp_server_stdio.exe --log-level DEBUG --tools-config detailed")
        
        print(f"\n{Colors.BOLD}Troubleshooting:{Colors.RESET}")
        print(f"  • Check .env file exists and contains valid API keys")
        print(f"  • Verify mcp.json syntax with JSON validator")
        print(f"  • Test executable with --help flag first")
        print(f"  • Check logs for authentication errors")
        print(f"  • Ensure Claude Desktop is restarted after mcp.json changes")
        
        print(f"\n{Colors.BOLD}Next Steps:{Colors.RESET}")
        print(f"  1. {Colors.WHITE}Configure .env file with your API keys{Colors.RESET}")
        print(f"  2. {Colors.WHITE}Update Claude Desktop mcp.json configuration{Colors.RESET}")
        print(f"  3. {Colors.WHITE}Restart Claude Desktop application{Colors.RESET}")
        print(f"  4. {Colors.WHITE}Test connection with a simple company search{Colors.RESET}")
        print(f"  5. {Colors.WHITE}Deploy to target environments as needed{Colors.RESET}")
        
        print(f"\n{Colors.GREEN}🚀 Production deployment ready!{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
    
    def build(self) -> bool:
        """
        Execute complete build process.
        
        Returns:
            bool: True if build successful, False otherwise
        """
        try:
            print(f"{Colors.BOLD}{Colors.MAGENTA}REGON MCP Server - Professional Executable Builder{Colors.RESET}")
            print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
            
            # Execute build pipeline
            if not self.validate_environment():
                return False
            
            self.prepare_build_environment()
            self.copy_source_files()
            self.build_executables()
            self.test_executables()
            self.generate_build_report()
            
            return True
            
        except KeyboardInterrupt:
            self.logger.error(f"{Colors.RED}❌ Build interrupted by user{Colors.RESET}")
            return False
        except Exception as e:
            self.logger.error(f"{Colors.RED}❌ Build failed: {e}{Colors.RESET}")
            if self.verbose:
                import traceback
                self.logger.debug(traceback.format_exc())
            return False


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Professional-grade REGON MCP Server executable builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python make_exe.py                    # Interactive build
  python make_exe.py -y                # Auto-confirm cleanup
  python make_exe.py -v                # Verbose output
  python make_exe.py -y --no-test      # Skip testing phase
        """
    )
    
    parser.add_argument(
        '-y', '--yes',
        action='store_true',
        help='Auto-confirm cleanup operations'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output and detailed logging'
    )
    
    parser.add_argument(
        '--no-test',
        action='store_true',
        help='Skip executable testing phase'
    )
    
    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the executable builder.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    args = parse_arguments()
    
    builder = ExecutableBuilder(
        auto_confirm=args.yes,
        verbose=args.verbose,
        skip_test=args.no_test
    )
    
    success = builder.build()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
