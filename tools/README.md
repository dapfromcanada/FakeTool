# AIStudio Tools

This folder contains independently-developed AI tools that work with the AIStudio launcher.

## Installing Tools

Each tool is maintained in its own separate GitHub repository. To install a tool:

### Option 1: Clone Individual Tools

```powershell
cd G:\AIStudio\tools

# Clone the tools you want
git clone https://github.com/dapfromcanada/VisionTester.git
git clone https://github.com/dapfromcanada/Convert2mdFile.git
git clone https://github.com/dapfromcanada/FakeTool.git
git clone https://github.com/dapfromcanada/ToolTester.git
```

### Option 2: Use AIStudio's Add Tool Feature

1. Launch AIStudio: `python ai_studio.py`
2. Click **"➕ Add Tool"**
3. Browse to your cloned tool folder
4. AIStudio auto-reads the tool's `config.json` and registers it

## Available Tools

- **VisionTester** - YOLO object detection testing tool
  - Repo: https://github.com/dapfromcanada/VisionTester
  
- **Convert2mdFile** - Document to Markdown converter
  - Repo: https://github.com/dapfromcanada/Convert2mdFile

- **FakeTool** - Example/test tool for template validation
  - Repo: https://github.com/dapfromcanada/FakeTool

- **ToolTester** - Automated testing for AIStudio tools
  - Repo: https://github.com/dapfromcanada/ToolTester

## Creating Your Own Tool

See `tools_template/TEMPLATE_INSTRUCTIONS.md` for complete documentation on creating custom tools.

### Quick Start:
1. Use the template as a starting point
2. Each tool must have:
   - `config.json` - Tool metadata
   - `main_gui.py` - GUI interface
   - `engine.py` - Headless CLI engine
   - `requirements.txt` - Dependencies
   - `.venv/` - Virtual environment
3. Register with AIStudio using "Add Tool"

## Tool Architecture

Each tool is **completely standalone**:
- ✅ Independent Git repository
- ✅ Own virtual environment
- ✅ Own dependencies
- ✅ Can be developed/tested separately
- ✅ AIStudio launches as subprocess

This allows:
- Individual version control
- Independent releases
- Easier collaboration
- Modular development
