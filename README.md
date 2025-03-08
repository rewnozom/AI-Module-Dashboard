
# Developer Documentation for the Utvecklar-Dashboard Framework

> **Overview:**  
> The Utvecklar-Dashboard framework is a modular developer dashboard application built using PySide6. It features a frameless main window with a custom title bar, multiple functional tabs (including a search dashboard, code module manager, and AI prompt vault), and robust support for managing, editing, and analyzing code modules. The framework also integrates code analysis and generation utilities for Python and JavaScript, along with an LLM integration system for automated code updates.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [File Structure](#file-structure)
3. [Main Components](#main-components)
   - [Dashboard (dashboard.py)](#dashboard-dashboardpy)
   - [Code Module Widget (code_module_widget.py)](#code-module-widget-code_module_widgetpy)
   - [Code Module Tab (code_module_tab.py)](#code-module-tab-code_module_tabpy)
   - [Code Utilities (utils/code_utils.py)](#code-utilities-utilscode_utilspy)
4. [UI and Theming](#ui-and-theming)
5. [LLM System Prompt Integration](#llm-system-prompt-integration)
6. [Extending and Maintaining the Framework](#extending-and-maintaining-the-framework)
7. [Usage and Workflow](#usage-and-workflow)
8. [Developer Notes and Best Practices](#developer-notes-and-best-practices)
9. [API Reference Highlights](#api-reference-highlights)
10. [Additional Utilities](#additional-utilities)

---

## Architecture Overview

The framework is organized as a multi-tab desktop application using [PySide6](https://doc.qt.io/qtforpython/) for its GUI. Key architectural highlights include:

- **Modular Design:** Each functional unit (such as code module editing, code analysis, and file management) is encapsulated in its own module or class.
- **Custom UI Components:** A frameless window with a custom title bar (in `dashboard.py`) provides an enhanced look and feel.
- **Code Management:** The framework supports advanced code editing with features like syntax highlighting, line numbering, auto-save, and undo/redo.
- **Analysis & Generation:** Utility modules provide methods to parse and analyze code (both Python and JavaScript) and generate code templates.
- **Data Persistence:** Module data is stored as JSON files and files are organized by language and category. The framework also supports import/export and auto-scanning for modules on disk.
- **LLM Integration:** An integrated AI system uses a system prompt (written in Swedish) to guide code updates, additions, and analysis within the dashboard.

---

## File Structure

Below is an outline of the major files and directories in the framework:

```
/ (project root)
│
├── dashboard.py
│   - Main entry point; creates the application window and adds various tabs.
│
├── ui/
│   ├── code_module_widget.py
│   │   - Contains the CodeModuleWidget class, an advanced widget for handling a code module.
│   │
│   └── code_module_tab.py
│       - Implements the tab view that lists, filters, imports/exports, and manages code modules.
│
└── utils/
    ├── code_utils.py
    │   - Provides code analysis (using AST and regex), code formatting, and code generation tools.
    │   - Contains classes such as CodeAnalyzer, CodeGenerator, and CodeModuleManager.
    │
    └── theme_utils.py
        - Implements theming (e.g., applying dark theme) for consistent UI styling.
```

Additional utility files (e.g., `card_utils.py`) are used for creating UI cards, and JSON files are located under a `/modules/json/` folder for persisting module data.

---

## Main Components

### Dashboard (`dashboard.py`)

- **Purpose:**  
  Acts as the main application window. It creates a frameless window with a custom title bar and manages multiple tabs (such as the search dashboard, code module manager, and AI prompt vault).

- **Key Features:**
  - **Custom Title Bar:** Implements window controls (minimize, maximize/restore, close) and draggable functionality.
  - **Tab Management:** Adds and configures tabs for different functionalities.
  - **Dark Theme:** Applies a dark theme globally for a consistent look and feel.

- **Important Methods:**
  - `__init__`: Sets up window flags, creates the main widget and layout, and applies the theme.
  - Mouse event overrides (e.g., `mousePressEvent`, `mouseMoveEvent`) to support dragging of the frameless window.

---

### Code Module Widget (`code_module_widget.py`)

- **Purpose:**  
  Provides an advanced widget for editing a single code module. This includes a code editor with syntax highlighting, line numbering, auto-save functionality, and integration for code analysis and AI updates.

- **Key Features:**
  - **Syntax Highlighting:** Uses language-specific highlighters (e.g., Python and JavaScript) to format code.
  - **Line Number Area:** Custom widget to display line numbers next to the editor.
  - **Auto-Save:** Periodic saving of code changes, with signals (e.g., `contentChanged`).
  - **Module Metadata:** Editable fields for module name, extension, description, category, and tags.
  - **LLM Integration:** Provides an AI integration tab for applying code suggestions or updates via LLM commands.
  - **Code Navigation:** Features to search code structure and navigate to functions, classes, or variables.

- **Important Methods & Signals:**
  - `initUI`: Configures the widget layout, including toolbars, tab widgets, and status areas.
  - `save_module`: Handles saving code to a file.
  - Signals such as `moduleAdded`, `moduleRemoved`, and `moduleUpdated` help communicate changes to parent components.

---

### Code Module Tab (`code_module_tab.py`)

- **Purpose:**  
  Acts as the container and management interface for multiple code module widgets. This tab allows the user to view, filter, import/export, and manage a collection of code modules.

- **Key Features:**
  - **Module Grid Layout:** Displays code modules in a 2x2 grid layout.
  - **Filtering & Searching:** Provides filtering options by category, language, and tags, along with a global search function.
  - **History Management:** Supports undo/redo of module changes.
  - **Import/Export:** Functions to import modules from a directory and export all modules to a designated folder.
  - **Pagination:** Manages multiple JSON pages to persist module data.

- **Important Methods:**
  - `initUI`: Builds the UI including control panels, scroll area, and status bar.
  - `add_code_module`: Creates a new CodeModuleWidget and integrates it into the grid.
  - `refresh_ui`: Rebuilds the module view after changes (addition, removal, filtering).
  - `save_data` and `load_data`: Persist and retrieve module data from JSON files.
  - Filtering methods (`apply_filters`, `clear_filters`) to adjust the visible module list.

---

### Code Utilities (`utils/code_utils.py`)

- **Purpose:**  
  Contains utility classes and functions for analyzing, generating, and formatting code. This module is central to providing insights into the code modules and offering improvements or code generation capabilities.

- **Key Components:**
  - **CodeAnalyzer:**  
    - Extracts functions, classes, variables, and imports from code using AST (for Python) or regular expressions (for JavaScript).
    - Supports basic metrics like lines of code (LOC), source lines (SLOC), and comment lines.
  - **CodeGenerator:**  
    - Provides templates to generate Python classes, functions, and JavaScript equivalents.
    - Useful for automatically inserting new functions or classes with pre-defined documentation.
  - **CodeModuleManager:**  
    - Manages file I/O for code modules, including saving, loading, renaming, moving, and listing modules.
    - Organizes modules based on file extension (language) and category directories.

- **Additional Utility Functions:**
  - Functions for detecting duplicate code, extracting package requirements from imports, and formatting code in both Python and JavaScript.

---

## UI and Theming

- **Theming:**  
  The framework uses a dark theme applied via `utils/theme_utils`. This ensures a consistent look for widgets such as the main window, buttons, input fields, and toolbars.

- **Custom Widgets:**  
  Components like the draggable title bar in `dashboard.py` and the line number area in `code_module_widget.py` enhance the user experience beyond standard widgets.

- **Responsiveness:**  
  Layouts are managed using QVBoxLayout, QHBoxLayout, and QGridLayout to ensure the application scales well with window resizing.

---

## LLM System Prompt Integration

The dashboard integrates an LLM (Large Language Model) system to assist with automated code modifications, analysis, and improvements directly within the module dashboard. Here’s how it works:

- **System Prompt Overview:**  
  The LLM system prompt is written in Swedish and provides detailed instructions for the AI on how to interpret and execute code management commands. Despite the prompt being in Swedish, the rest of the documentation and user interface remain in English. The system prompt guides the LLM on tasks such as adding new functions or classes, updating existing code, and suggesting improvements.

- **Command Structure:**  
  The prompt defines a set of commands that the LLM can process, including:
  - **Adding Code:**  
    - `/add_function <function_name>`  
      _Example:_ Generates a complete Python function template with proper docstrings and formatting.
    - `/add_class <class_name>`  
      _Example:_ Generates a class template with an initializer and space for methods.
  - **Updating Code:**  
    - `/update_function <function_name>`  
    - `/update_class <class_name>`  
    - `/update_method <class_name> <method_name>`  
      _Example:_ Updates an existing function or class method with new implementation.
  - **Variable Management:**  
    - `/update_variable <variable_name> <new_value>`  
    - `/add_variable <variable_name> <value>`
  - **Analytical Commands:**  
    - `/analyze_module`  
    - `/suggest_improvements`  
    - `/find_function <search_term>`  
    - `/find_class <search_term>`

- **Key Principles in the LLM Prompt:**  
  The prompt also emphasizes:
  - **Indentation:** Ensuring proper indentation (4 spaces for Python and 2 spaces for JavaScript).
  - **Documentation:** Including detailed docstrings or JSDoc comments.
  - **Code Formatting:** Adhering to language-specific style guidelines (e.g., PEP 8 for Python).
  - **Precision in Variable and Method Operations:** Clear syntax for variable updates and method modifications.

- **Usage within the Dashboard:**  
  Inside the CodeModuleWidget, the AI integration tab allows developers to paste or generate code changes using these commands. When a command is issued, the system prompt guides the LLM to generate code that conforms to the existing code style and integrates seamlessly into the module. This ensures that updates are consistent with the rest of the application.

- **Benefits:**  
  - **Consistent Code Quality:** The prompt enforces coding standards and documentation practices.
  - **Streamlined Updates:** Developers can quickly update or add code using structured commands.
  - **Enhanced Analysis:** The LLM can analyze code and suggest improvements based on the guidelines provided.

---

## Extending and Maintaining the Framework

- **Adding New Functionality:**  
  When adding new modules or tabs, follow the structure used in `dashboard.py` and `code_module_tab.py`. Create new UI classes if needed, and ensure they integrate with the theming and signal/slot mechanisms.

- **Code Standards:**  
  - Use consistent naming conventions and follow PEP 8 for Python code.
  - When writing new code analysis or generation functions, leverage the existing structure in `CodeAnalyzer` and `CodeGenerator`.
  - Ensure any new code is well-documented, preferably with docstrings or JSDoc-style comments for JavaScript parts.

- **Signals and Communication:**  
  The framework uses Qt signals (e.g., `moduleUpdated`, `moduleRemoved`) to notify parent components of changes. When extending functionality, emit these signals to maintain synchronization between UI components.

- **Testing and Debugging:**  
  Each component (especially the code editor and module management features) should be tested in isolation. Use the provided logging (e.g., status messages in the status bar) and Python’s exception handling to catch errors.

---

## Usage and Workflow

1. **Launching the Dashboard:**  
   Run `dashboard.py` to start the application. The dashboard opens with a frameless window, custom title bar, and multiple tabs.

2. **Managing Code Modules:**  
   - In the **Code Module Manager** tab, add new modules using the "Lägg till Ny Modul" button.
   - Edit code in the embedded code editor with syntax highlighting and auto-save.
   - Use the toolbar for saving, importing, exporting, and tag management.
   - The left panel in the Code Module Tab provides filtering options, history management (undo/redo), and JSON file operations.

3. **Code Analysis and AI Integration:**  
   - Within each module’s widget, use the integrated AI/LLM tab to paste or generate code suggestions.
   - Validate and apply code changes using the provided tools.
   - Utilize the structure tree to navigate to functions, classes, or variables.

4. **Persistence:**  
   - Module data is automatically saved to JSON files in `/modules/json/`.
   - The CodeModuleManager handles file I/O, ensuring modules are stored in language- and category-specific directories.

---

## Developer Notes and Best Practices

- **Maintainability:**  
  Ensure that any updates to one component do not break the integration with other parts of the system. Always test signal connections (module addition, update, and removal) thoroughly.

- **Scalability:**  
  The use of grid layouts and JSON pagination allows the system to handle a growing number of modules. When adding new modules, update the UI accordingly.

- **Code Consistency:**  
  When writing or modifying code, maintain the use of dark theme styling and follow the existing layout guidelines for consistency.

- **Performance:**  
  Auto-save timers, auto-scanning, and history management are designed to run in the background. Optimize these functions if the number of modules grows significantly.

---

## API Reference Highlights

### `Dashboard` Class (in `dashboard.py`)
- **Methods:**
  - `__init__()`: Sets up the main window.
  - `mousePressEvent()`, `mouseMoveEvent()`: Enable dragging the frameless window.
- **Tabs:**
  - **Sökfält Dashboard**, **Kodmodul Manager**, **AI Prompt Vault**

### `CodeModuleWidget` Class (in `code_module_widget.py`)
- **Signals:**
  - `moduleAdded(str, dict)`
  - `moduleRemoved(str)`
  - `moduleUpdated(str, str, dict)`
- **Key Methods:**
  - `initUI()`: Configures the module widget.
  - `save_module()`: Saves module content to file.
  - `update_structure_tree()`: Refreshes the code structure tree.
  - `apply_llm_changes()`: Applies changes from AI integration.

### `CodeModuleTab` Class (in `code_module_tab.py`)
- **Key Methods:**
  - `add_code_module()`: Adds a new code module widget.
  - `refresh_ui()`: Rebuilds the module grid.
  - `apply_filters()`, `clear_filters()`: Filter modules based on criteria.
  - `save_data()`, `load_data()`: Manage JSON persistence.

### `CodeAnalyzer`, `CodeGenerator`, and `CodeModuleManager` (in `utils/code_utils.py`)
- **CodeAnalyzer:**  
  - Methods to extract functions, classes, variables, and imports.
- **CodeGenerator:**  
  - Methods to generate Python/JavaScript functions and classes.
- **CodeModuleManager:**  
  - Methods to save, load, list, delete, rename, and move module files.

---

## Additional Utilities

- **Theme Utilities (`utils/theme_utils.py`):**  
  Centralized functions to apply the dark theme across the application.
  
- **Card Utilities (`utils/card_utils.py`):**  
  Used to create styled UI cards for displaying module information (if applicable).

- **JSON Management:**  
  Modules are stored in JSON files under `/modules/json/`, and the framework supports multi-page JSON handling with history and pagination.
