# AnkiVN â€“ Better Web Browser

A lightweight, fully integrated web browser add-on for Anki's **Add Card** and **Browser** dialogs, designed to help developers understand, modify, and extend the web browsing functionality within Anki.

---

## Table of Contents

1. [Project Overview](#project-overview)  
2. [Architecture](#architecture)  
3. [Project Structure](#project-structure)  
4. [Key Components](#key-components)  
5. [Development Setup](#development-setup)  
6. [Configuration System](#configuration-system)  
7. [Testing](#testing)  
8. [Contributing](#contributing)  
9. [Build & Deployment](#build--deployment)  
10. [Technical Requirements](#technical-requirements)  
11. [License](#license)

---

## Project Overview

**AnkiVN Better Web Browser** is an Anki add-on that embeds a fully functional web browser directly into Anki's interface. This allows users to research vocabulary, look up definitions, find images, and access various online resources without leaving the Anki environment.

### Key Features

- **Embedded Browser Integration**: Seamlessly integrates with Anki's Add Card dialog and Browser window
- **Multi-Tab Support**: Multiple tabs within the browser pane for efficient browsing
- **Configurable Search Sites**: Predefined search engines and dictionaries categorized by language and content type
- **Field-Based Auto-Search**: Automatically searches based on selected note fields
- **Keyboard Shortcuts**: Customizable shortcuts for common browser operations
- **Session Persistence**: Maintains browser state across Anki sessions

---

## Architecture

The add-on follows a modular architecture with clear separation of concerns:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚   UI Layer      â”‚    â”‚  Config Layer   â”‚    â”‚  Browser Layer  â”‚
â”‚                 â”‚    â”‚                 â”‚    â”‚                 â”‚
â”‚ â€¢ Settings UI   â”‚â—„â”€â”€â–ºâ”‚ â€¢ Config Mgmt   â”‚â—„â”€â”€â–ºâ”‚ â€¢ Browser Widgetâ”‚
â”‚ â€¢ Browser UI    â”‚    â”‚ â€¢ Meta Storage  â”‚    â”‚ â€¢ Tab Managementâ”‚
â”‚ â€¢ Event Filters â”‚    â”‚ â€¢ Site Defs     â”‚    â”‚ â€¢ Web Engine    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
         â”‚                       â”‚                       â”‚
         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                 â”‚
                    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                    â”‚  Anki Hooks     â”‚
                    â”‚                 â”‚
                    â”‚ â€¢ Browser Hook  â”‚
                    â”‚ â€¢ Dialog Hook   â”‚
                    â”‚ â€¢ Menu Hook     â”‚
                    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Core Design Principles

1. **Minimal Anki API Surface**: Uses only stable Anki APIs to ensure compatibility
2. **Modular Components**: Each component has a single responsibility
3. **Configuration-Driven**: Behavior is controlled through configuration files
4. **Event-Driven**: Responds to Anki events and user interactions
5. **Testable**: Core logic is isolated and unit-testable

---

## Project Structure

```
AnkiVN---Better-Web-Browser-main/
â”œâ”€â”€ __init__.py                 # Entry point, hooks registration
â”œâ”€â”€ browser.py                  # Core browser widget implementation
â”œâ”€â”€ config.py                   # Configuration management & search sites
â”œâ”€â”€ settings.py                 # Settings dialog UI
â”œâ”€â”€ manifest.json               # Anki add-on manifest
â”œâ”€â”€ meta.json                   # User configuration storage
â”œâ”€â”€ config.json                 # Global settings (start URL, etc.)
â”œâ”€â”€ pytest.ini                  # pytest configuration
â”œâ”€â”€ conftest.py                 # pytest fixtures
â”œâ”€â”€ tests/                      # Test suite
â”‚   â”œâ”€â”€ conftest.py            # Test fixtures
â”‚   â”œâ”€â”€ test_config.py         # Configuration tests
â”‚   â””â”€â”€ __pycache__/           # Python cache
â”œâ”€â”€ __pycache__/               # Python cache
â”œâ”€â”€ .git/                      # Git repository
â”œâ”€â”€ .gitignore                 # Git ignore rules
â”œâ”€â”€ demo.gif                   # Demo animation
â”œâ”€â”€ CHANGELOG.md               # Version history
â”œâ”€â”€ LICENSE                    # GPL v3 license
â””â”€â”€ README.md                  # This file
```

---

## Key Components

### 1. `__init__.py` - Entry Point & Hooks
- **Purpose**: Main entry point for the add-on
- **Responsibilities**:
  - Registers Anki hooks (`browser_will_show`, `editor_did_init_buttons`, `editor_did_init`)
  - Initializes browser integration for both Add Card and Browser dialogs
  - Sets up keyboard shortcuts and event filters
  - Manages add-on lifecycle and menu integration
  - Handles auto-refresh functionality based on note selection

**Key Classes**:
- `BrowserEventFilter`: Handles keyboard events for tab closure (Ctrl+W)
- `BrowserCloseEventFilter`: Handles window close events with tab management
- `BrowserActionFilter`: Filters and intercepts browser actions

**Key Functions**:
- `show_browser_sidebar()`: Main function to toggle browser sidebar
- `add_browser_button()`: Adds browser button to editor toolbar
- `setup_editor_shortcuts()`: Sets up keyboard shortcuts for refresh
- `refresh_browser_search()`: Refreshes browser with current note content
- `on_browser_row_changed()`: Auto-refreshes when note selection changes
- `setup_browser_hooks()`: Connects browser table selection events

**Menu Integration**:
- Creates "AnkiVN" main menu in Anki's menu bar
- Adds "Better Web Browser" settings option to the menu

### 2. `browser.py` - Browser Widget
- **Purpose**: Core browser functionality with multi-tab support
- **Responsibilities**:
  - Multi-tab browser implementation with tab management
  - Navigation controls (back, forward, reload) with keyboard shortcuts
  - URL bar with intelligent search detection and Google fallback
  - QWebEngineView configuration with mobile user agent
  - Session persistence with cookies and JavaScript support
  - Responsive design with viewport injection
  - Tab title management and URL change handling

**Key Classes**:
- `TabWidget`: Individual tab implementation with navigation controls
- `BrowserWidget`: Main browser container with tab management
- Manages `QWebEngineView` instances with custom profiles

**Browser Features**:
- **Mobile User Agent**: Simulates Android device for optimized layouts
- **Persistent Cookies**: Maintains session across Anki restarts
- **JavaScript Support**: Full JavaScript and clipboard access enabled
- **Responsive Viewport**: Auto-injection of mobile viewport meta tag
- **Smart URL Detection**: Distinguishes between URLs and search terms
- **Tab Management**: Closable, movable tabs with document mode

**Navigation System**:
- **Back/Forward**: Browser history navigation with shortcuts
- **Reload**: Page refresh functionality
- **URL Bar**: Smart navigation with search fallback
- **New Tab**: Creates blank tabs or loads specific URLs

**Tab Management**:
- **Multi-tab Support**: Unlimited tabs with tab bar
- **Tab Titles**: Auto-updating titles from page content (20 char limit)
- **Tab Closure**: Individual tab closing or hide widget if last tab
- **Tab Shortcuts**: Ctrl+T (new), Ctrl+W (close), Ctrl+L (focus URL)

**Search Integration**:
- **Auto-search**: `open_search_tabs()` method for field-based searches
- **URL Template Processing**: Handles placeholders and encoding
- **Bulk Tab Creation**: Clears existing tabs and opens all search results
- **Field-Site Mapping**: Links configured fields to search sites

### Browser Widget Implementation Details

#### TabWidget Class Architecture

Each tab is a complete browser instance with:
- **Navigation Bar**: Back, Forward, Reload, URL input, New Tab buttons
- **Web Engine**: QWebEngineView with custom profile and mobile user agent
- **Viewport Injection**: JavaScript injection for responsive layouts
- **Smart URL Detection**: Distinguishes between URLs and search terms

#### BrowserWidget Class Architecture

Container for multiple tabs with centralized management:
- **Tab Container**: QTabWidget with document mode and text eliding
- **Focus Management**: Auto-focus on web content when showing
- **Event Handling**: Custom key press events for tab operations
- **Tab Lifecycle**: Creation, updating, and removal management

#### Web Engine Configuration

```python
# Mobile user agent for responsive layouts
profile.setHttpUserAgent("Mozilla/5.0 (Linux; Android 11; Pixel 5)...")

# Persistent cookies across sessions
profile.setPersistentCookiesPolicy(ForcePersistentCookies)

# JavaScript and clipboard access enabled
settings.setAttribute(JavascriptEnabled, True)
settings.setAttribute(JavascriptCanAccessClipboard, True)
```

#### Multi-Search Tab Creation

The `open_search_tabs()` method handles bulk tab creation:
1. **Content Validation**: Check if search content exists
2. **Configuration Loading**: Get note type and field configurations
3. **URL Collection**: Iterate through configured fields and enabled sites
4. **URL Generation**: Format templates with encoded search content
5. **Tab Management**: Clear existing tabs and create new ones
6. **Title Setting**: Set descriptive titles (site - field format)

#### Keyboard Shortcuts System

```python
# Tab-level shortcuts
Ctrl+[ / Ctrl+]  # Back/Forward navigation
Ctrl+T          # New tab
Ctrl+L          # Focus URL bar
Ctrl+R          # Reload current tab
Ctrl+W          # Close current tab (custom event handling)
```

### 3. `config.py` - Configuration Management
- **Purpose**: Handles all configuration-related operations
- **Responsibilities**:
  - Loads and saves configuration files with fallback mechanisms
  - Manages predefined search sites with categorized URL templates
  - Handles `config.json` file I/O with error handling
  - Provides default configurations and validation
  - Cross-platform path resolution for Anki add-on directories

**Key Features**:
- `PREDEFINED_SEARCH_SITES`: Dictionary of categorized search engines with URL templates
- `get_config_path()`: Robust path resolution with multiple fallback methods
- `get_default_config()`: Provides safe default configuration structure
- `get_config()`: Loads configuration with automatic key validation
- `save_config()`: Saves configuration with directory creation and error handling

**Configuration Structure**:
```python
{
    "note_type": "",              # Selected note type name
    "main_field": "",             # Main field for auto-search
    "refresh_shortcut": "Ctrl+R", # Keyboard shortcut for refresh
    "configurable_fields": {},    # Fields that can show web content
    "field_search_configs": {}    # Search site configurations per field
}
```

**Search Site Categories**:
- **English**: 10 dictionaries (Cambridge, Oxford, Merriam-Webster, etc.)
- **Tiáº¿ng Viá»‡t**: 4 Vietnamese resources (Cambridge Viá»‡t, Dunno, Laban, VDict)
- **Example**: 5 sentence/example sites (Dunno Examples, TraCau, Ludwig, etc.)
- **Thesaurus**: 3 thesaurus resources (Thesaurus.com, Power Thesaurus, etc.)
- **Image**: 4 image search engines (Google Images, Bing Images, Giphy, Tenor)

### 4. `settings.py` - Settings UI
- **Purpose**: Provides comprehensive user interface for configuration
- **Responsibilities**:
  - Settings dialog implementation with two-column responsive layout
  - Field configuration UI with hierarchical tree widget display
  - Search site selection interface with category grouping and toggles
  - Custom shortcut configuration with real-time key capture
  - Real-time filtering and search functionality across all sites
  - Configuration validation and error handling during save operations

**Key Classes**:
- `SettingsDialog`: Main settings window with maximize button support and responsive design
- `ShortcutEdit`: Custom shortcut input widget with advanced key capture and validation
- Field and site configuration widgets with persistent checkbox states

**UI Architecture**:
- **Two-Column Layout**: Basic configuration (left 1/3) and search sites (right 2/3)
- **Hierarchical Tree Widget**: Three-level display: Fields â†’ Categories â†’ Sites
- **Real-Time Search Filtering**: Instant filtering of sites by name with hierarchical visibility
- **Category Toggle System**: "Select All/Deselect All" buttons for efficient bulk operations
- **Responsive Design**: Minimum 800x600 with proper stretch factors and auto-resizing
- **State Persistence**: Maintains expanded/collapsed states and checkbox selections

**Advanced Features**:
- **Dynamic Field Loading**: Automatically updates fields when note type changes
- **Site Configuration Matrix**: Complex mapping of fields to categories to individual sites
- **URL Template Display**: Shows actual URL templates for each search site
- **Bulk Operations**: Category-level site selection with visual feedback
- **Configuration Validation**: Validates all settings before saving with error messages

**UI Components**:
- **Note Type Dropdown**: Dynamically loaded from Anki collection
- **Main Field Selection**: Auto-populated based on selected note type fields
- **Configurable Fields List**: Multi-selection list with checkboxes for field enablement
- **Search Sites Tree**: Three-column tree (Site, Enabled, URL Template) with filtering
- **Shortcut Capture**: Real-time keyboard shortcut capture with modifier support

### Settings UI Implementation Details

#### SettingsDialog Class Architecture

The settings dialog uses a sophisticated two-column layout system:

```python
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        # Window with maximize button support
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        
        # Complex data structures for state management
        self.field_site_checkboxes = {}  # [note_type][field_name][category_name][site_name] -> QCheckBox
        self.configurable_field_details = {}  # Field metadata storage
        
        # Minimum responsive dimensions
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
```

**Layout Structure**:
- **Left Column (1/3 width)**: Basic configuration controls
- **Right Column (2/3 width)**: Search sites tree with filtering
- **Column Stretch Factors**: Automatically adjusts to window resizing
- **Responsive Design**: Maintains usability across different screen sizes

#### ShortcutEdit Custom Widget

Advanced keyboard shortcut capture with comprehensive validation:

```python
class ShortcutEdit(QLineEdit):
    def keyPressEvent(self, event):
        # Real-time key combination capture
        # Modifier detection: Ctrl, Shift, Alt
        # Key validation and filtering
        # Automatic string formatting (e.g., "Ctrl+Shift+R")
        # Error handling with graceful fallback
```

**Features**:
- **Real-Time Capture**: Captures key combinations as they're pressed
- **Modifier Support**: Handles Ctrl, Shift, Alt combinations
- **Key Validation**: Filters out invalid keys and modifiers
- **Visual Feedback**: Shows formatted shortcut strings immediately
- **Error Handling**: Graceful handling of invalid key combinations

#### Hierarchical Tree Widget System

Three-level hierarchical display with advanced state management:

```python
def _add_field_to_tree(self, tree, field_name, field_config):
    # Level 1: Field names (e.g., "Back", "Extra")
    field_item = QTreeWidgetItem([field_name, "", ""])
    
    # Level 2: Categories (e.g., "English", "Tiáº¿ng Viá»‡t")
    for category, sites in PREDEFINED_SEARCH_SITES.items():
        cat_item = QTreeWidgetItem([category, "", ""])
        
        # Category toggle button with state tracking
        toggle_btn = QPushButton("Select All")
        toggle_btn.setCheckable(True)
        
        # Level 3: Individual sites with checkboxes
        for site_name, url_template in sites.items():
            site_item = QTreeWidgetItem([site_name, "", url_template])
            site_item.setCheckState(1, Qt.CheckState.Checked/Unchecked)
```

**Tree Structure**:
```
Field Name
â”œâ”€â”€ Category 1 [Select All Button]
â”‚   â”œâ”€â”€ â˜‘ Site 1 - URL Template 1
â”‚   â”œâ”€â”€ â˜ Site 2 - URL Template 2
â”‚   â””â”€â”€ â˜‘ Site 3 - URL Template 3
â””â”€â”€ Category 2 [Select All Button]
    â”œâ”€â”€ â˜ Site 4 - URL Template 4
    â””â”€â”€ â˜‘ Site 5 - URL Template 5
```

#### Real-Time Search Filtering

Advanced filtering system with hierarchical visibility control:

```python
def filter_sites(self, text):
    """Filter sites based on search text with hierarchical visibility."""
    for field_item in self.sites_tree.topLevelItems():
        field_visible = False
        
        for cat_item in field_item.children():
            cat_visible = False
            
            for site_item in cat_item.children():
                site_visible = text.lower() in site_item.text(0).lower()
                site_item.setHidden(not site_visible)
                cat_visible = cat_visible or site_visible
            
            cat_item.setHidden(not cat_visible)
            field_visible = field_visible or cat_visible
        
        field_item.setHidden(not field_visible)
```

**Filtering Logic**:
- **Bottom-Up Visibility**: Site visibility determines category visibility
- **Hierarchical Propagation**: Category visibility determines field visibility
- **Real-Time Updates**: Instant filtering as user types
- **Case-Insensitive Matching**: Flexible search across all site names

#### Category Toggle System

Efficient bulk operations with visual feedback:

```python
def _toggle_category_sites(self, category_item, checked, button):
    """Toggle all sites in a category with visual feedback."""
    for i in range(category_item.childCount()):
        site_item = category_item.child(i)
        site_item.setCheckState(1, Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
    
    # Dynamic button text updates
    button.setText("Deselect All" if checked else "Select All")
```

**Toggle Features**:
- **Bulk Selection**: Select/deselect all sites in a category
- **Visual Feedback**: Button text changes based on current state
- **State Synchronization**: Maintains consistency across UI elements
- **Smart Detection**: Automatically detects current category state

#### Configuration Validation and Saving

Comprehensive validation system with error handling:

```python
def accept(self):
    cfg = config.get_config()
    
    # Multi-step validation and saving process
    # 1. Basic configuration validation
    # 2. Field configuration compilation
    # 3. Site configuration matrix building
    # 4. Configuration file saving with error handling
    # 5. User feedback on success/failure
    
    if config.save_config(cfg):
        super().accept()
    else:
        showInfo("Failed to save configuration.")
```

**Validation Steps**:
1. **Note Type Validation**: Ensures selected note type exists
2. **Field Validation**: Validates field selections against note type
3. **Site Configuration**: Builds complex field-to-site mapping
4. **File System Validation**: Checks write permissions and disk space
5. **User Feedback**: Provides clear success/failure messages

#### Dynamic UI Updates

Reactive UI system that responds to user selections:

```python
def on_note_type_changed(self, note_type):
    """Cascade updates when note type changes."""
    self.update_main_field_combo()     # Refresh available fields
    self.update_fields_list()          # Update field checkboxes
    self.update_sites_tree()           # Rebuild sites tree
    
def on_field_selection_changed(self, item):
    """Update sites tree when field selection changes."""
    self.update_sites_tree()
```

**Update Chain**:
- **Note Type â†’ Main Field Options**: Updates available fields
- **Note Type â†’ Configurable Fields**: Updates field list
- **Field Selection â†’ Sites Tree**: Rebuilds site configuration
- **Real-Time Synchronization**: All UI elements stay synchronized

#### State Management System

Complex state tracking across multiple UI components:

```python
# Multi-dimensional state tracking
self.field_site_checkboxes = {
    "note_type": {
        "field_name": {
            "category_name": {
                "site_name": QCheckBox_reference
            }
        }
    }
}

# Field metadata storage
self.configurable_field_details = {
    "field_name": {
        "group_box": QGroupBox_reference,
        "content_widget": QWidget_reference,
        "toggle_button": QPushButton_reference,
        "categories": {}
    }
}
```

**State Features**:
- **Hierarchical State**: Maintains state across all UI levels
- **Reference Management**: Tracks all UI component references
- **Persistence**: Remembers user selections across dialog sessions
- **Validation**: Ensures state consistency before saving

### Search Filtering System

Advanced real-time search functionality:

```python
def filter_sites(self, text):
    """Filter sites based on search text."""
    for i in range(self.sites_tree.topLevelItemCount()):
        field_item = self.sites_tree.topLevelItem(i)
        field_visible = False
        
        for j in range(field_item.childCount()):
            cat_item = field_item.child(j)
            cat_visible = False
            
            for k in range(cat_item.childCount()):
                site_item = cat_item.child(k)
                site_name = site_item.text(0).lower()
                site_visible = text.lower() in site_name
                site_item.setHidden(not site_visible)
                cat_visible = cat_visible or site_visible
            
            cat_item.setHidden(not cat_visible)
            field_visible = field_visible or cat_visible
        
        field_item.setHidden(not field_visible)
```

**Filter Features**:
- **Real-time Search**: Instant filtering as user types
- **Hierarchical Filtering**: Maintains tree structure during filtering
- **Case-insensitive**: Searches regardless of case
- **Partial Matching**: Supports substring searches
- **Visual Feedback**: Immediate hide/show of non-matching items

### Category Toggle System

Bulk operation system for managing site selections:

```python
def _toggle_category_sites(self, category_item, checked, button):
    """Toggle all sites in a category."""
    for i in range(category_item.childCount()):
        site_item = category_item.child(i)
        site_item.setCheckState(1, Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
    
    # Update button text
    button.setText("Deselect All" if checked else "Select All")
```

**Toggle Features**:
- **Bulk Operations**: Select/deselect all sites in a category
- **Dynamic Labels**: Button text updates based on state
- **Consistent State**: All child items match parent state
- **Visual Feedback**: Immediate checkbox updates

### Configuration Persistence

Comprehensive save/load system:

```python
def accept(self):
    """Save all configuration settings."""
    cfg = config.get_config()
    
    # Basic settings
    cfg["note_type"] = self.note_type_combo.currentText()
    cfg["main_field"] = self.main_field_combo.currentText()
    cfg["refresh_shortcut"] = self.shortcut_edit.text()
    
    # Field configurations
    note_type = self.note_type_combo.currentText()
    if note_type:
        # Save configurable fields
        configurable_fields = []
        for i in range(self.fields_list.count()):
            item = self.fields_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                configurable_fields.append(item.text())
        
        if "configurable_fields" not in cfg:
            cfg["configurable_fields"] = {}
        cfg["configurable_fields"][note_type] = configurable_fields
        
        # Save detailed site configurations
        field_configs = {}
        for i in range(self.sites_tree.topLevelItemCount()):
            field_item = self.sites_tree.topLevelItem(i)
            field_name = field_item.text(0)
            field_config = {}
            
            for j in range(field_item.childCount()):
                cat_item = field_item.child(j)
                category = cat_item.text(0)
                sites = {}
                
                for k in range(cat_item.childCount()):
                    site_item = cat_item.child(k)
                    site_name = site_item.text(0)
                    enabled = site_item.checkState(1) == Qt.CheckState.Checked
                    sites[site_name] = enabled
                    
                field_config[category] = sites
                
            field_configs[field_name] = field_config
            
        if "field_search_configs" not in cfg:
            cfg["field_search_configs"] = {}
        cfg["field_search_configs"][note_type] = field_configs
    
    # Save with validation
    if config.save_config(cfg):
        super().accept()
    else:
        showInfo("Failed to save configuration.")
```

**Persistence Features**:
- **Multi-level Storage**: Saves configurations at note type, field, and site levels
- **Validation**: Ensures data integrity before saving
- **Error Handling**: Graceful handling of save failures
- **User Feedback**: Clear success/failure messages

### UI Layout Architecture

Professional two-column layout system:

```python
def setup_ui(self):
    main_layout = QVBoxLayout(self)
    
    # Create two columns
    columns_layout = QHBoxLayout()
    left_column = QVBoxLayout()
    right_column = QVBoxLayout()
    
    # Left Column - Basic Configuration
    # Note Type Selection
    note_type_group = QGroupBox("Note Type")
    # Main Field Selection
    main_field_group = QGroupBox("Main Field")
    # Configurable Fields
    fields_group = QGroupBox("Configurable Fields")
    # Refresh Shortcut
    shortcut_group = QGroupBox("Refresh Shortcut")
    
    # Right Column - Search Sites
    sites_group = QGroupBox("Search Sites")
    # Search filter
    search_layout = QHBoxLayout()
    # Sites tree
    self.sites_tree = QTreeWidget()
    
    # Layout proportions
    columns_layout.addLayout(left_column, 1)  # 1/3 width
    columns_layout.addLayout(right_column, 2)  # 2/3 width
    
    # Window sizing
    self.setMinimumWidth(800)
    self.setMinimumHeight(600)
    self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
```

**Layout Features**:
- **Proportional Design**: 1:2 ratio for left:right columns
- **Responsive Layout**: Adjusts to window resizing
- **Minimum Sizing**: Ensures usable interface dimensions
- **Maximize Support**: Full-screen viewing capability
- **Organized Grouping**: Logical separation of functionality

### Error Handling and Validation

Comprehensive error management system:

```python
# Keyboard input validation
def keyPressEvent(self, event):
    try:
        if event.type() == QEvent.Type.KeyPress:
            # Skip invalid keys
            if key in (Qt.Key.Key_unknown, Qt.Key.Key_Control, 
                      Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta):
                return
            # Process valid key combinations
    except Exception as e:
        print(f"Error in ShortcutEdit.keyPressEvent: {str(e)}")
        return

# Configuration validation
def load_config(self):
    try:
        cfg = config.get_config()
        # Validate note type exists
        note_types = mw.col.models.all()
        if cfg.get("note_type") not in [nt['name'] for nt in note_types]:
            # Reset to default
            cfg["note_type"] = note_types[0]['name'] if note_types else None
    except Exception as e:
        print(f"Error loading configuration: {str(e)}")
        # Use default configuration
```

**Error Handling Features**:
- **Input Validation**: Prevents invalid keyboard shortcuts
- **Configuration Validation**: Ensures all settings are valid
- **Graceful Degradation**: Continues operation despite errors
- **Error Logging**: Comprehensive logging for debugging
- **User Feedback**: Clear error messages when appropriate

### Performance Optimizations

Efficient UI and data management:

```python
# Lazy loading
def update_sites_tree(self):
    """Only update tree when necessary."""
    if not self.note_type_combo.currentText():
        return
    
    selected_fields = self._get_selected_fields()
    if not selected_fields:
        return
    
    # Efficient tree building
    self.sites_tree.clear()
    for field_name in selected_fields:
        self._add_field_to_tree(field_name)

# Efficient filtering
def filter_sites(self, text):
    """Filter without rebuilding tree."""
    for item in self._iterate_tree_items():
        item.setHidden(not self._matches_filter(item, text))

# Memory management
def closeEvent(self, event):
    """Clean up resources."""
    self.field_site_checkboxes.clear()
    self.configurable_field_details.clear()
    super().closeEvent(event)
```

**Performance Features**:
- **Lazy Loading**: Creates UI elements only when needed
- **Efficient Updates**: Minimizes unnecessary UI rebuilds
- **Memory Management**: Proper cleanup of resources
- **Optimized Filtering**: Fast search without tree rebuilding

---

## Development Setup

### Prerequisites
- **Anki â‰¥ 2.1.50** (minimum supported version by new launcher)
- **Current Anki versions**:
  - **Latest stable**: 25.07.2 (July 2025)
  - **Latest beta**: 25.08b1 (includes Qt 6.9 update)
  - **New launcher system**: Supports version downgrade/upgrade
- **Qt version**: Qt 6.9 (as of 25.08b1), Qt 6.8+ recommended
- **Python version**: 
  - **Bundled**: Python 3.13 (shipped with Anki 25.07+)
  - **Minimum supported**: Python 3.9 (maintained for backward compatibility)
- **System requirements**:
  - **Linux**: glibc 2.36+ required (as of 25.07+)
  - **Windows**: AMD64 (ARM64 runs in emulation mode)
  - **macOS**: AMD64 (Intel) and ARM64 (Apple Silicon) support
- **Development tools**:
  - **pytest** for testing (optional)
  - **Git** for version control
  - **Text editor** or IDE with Python support

### Installation for Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/AnkiVN---Better-Web-Browser.git
   cd AnkiVN---Better-Web-Browser
   ```

2. **Install in Anki add-ons directory**:
   ```bash
   # Windows
   copy /E . "%APPDATA%\Anki2\addons21\AnkiVN---Better-Web-Browser-main"
   
   # macOS/Linux
   cp -r . ~/Library/Application\ Support/Anki2/addons21/AnkiVN---Better-Web-Browser-main
   ```

3. **Restart Anki** to load the add-on

### Development Workflow

1. **Make changes** to the source code
2. **Restart Anki** to reload the add-on (or use debug mode)
3. **Test functionality** in both Add Card and Browser dialogs
4. **Run tests** (if applicable): `pytest`
5. **Check configuration** files for proper saving/loading
6. **Test edge cases**: Empty fields, special characters, network issues
7. **Commit changes** and create pull requests

### Hot Reload for Development (Advanced)

For faster development, you can use Anki's debug mode:

```python
# Add this to your development version of __init__.py
import importlib
import sys

def reload_addon():
    """Reload the add-on without restarting Anki."""
    modules_to_reload = [
        'browser', 'config', 'settings'
    ]
    
    for module_name in modules_to_reload:
        full_module_name = f"addons21.AnkiVN---Better-Web-Browser-main.{module_name}"
        if full_module_name in sys.modules:
            importlib.reload(sys.modules[full_module_name])
```

### Debugging

- **Print statements**: Use `print()` for simple debugging
- **Anki utils**: Use `aqt.utils.showInfo()` for user-visible debugging
- **Debug console**: Access via `Tools â†’ Debug Console` in Anki
- **Log files**: Check Anki's profile directory for crash logs
- **Exception handling**: Wrap risky operations in try-catch blocks

**Common debugging locations**:
- `%APPDATA%\Anki2\[profile]\` (Windows)
- `~/Library/Application Support/Anki2/[profile]/` (macOS)
- `~/.local/share/Anki2/[profile]/` (Linux)

---

## Configuration System

### Configuration Files

#### 1. `config.json` - Global Settings
Located in the add-on directory, stores basic configuration:
```json
{
    "note_type": "Basic",
    "main_field": "Front",
    "refresh_shortcut": "Ctrl+R",
    "configurable_fields": {
        "Basic": ["Back", "Extra"]
    },
    "field_search_configs": {
        "Basic": {
            "Back": {
                "English": {
                    "Cambridge Dictionary": true,
                    "Oxford Dictionary": false
                },
                "Image": {
                    "Google Images": true
                }
            }
        }
    }
}
```

#### 2. `meta.json` - User Configuration (Legacy)
Stores user-specific settings including:
- Selected note type
- Main field configuration
- Field search site mappings
- UI state (expanded/collapsed fields)

#### 3. `manifest.json` - Add-on Manifest
```json
{
    "name": "AnkiVN - Better Web Browser",
    "package": "add_dialog_web_browser",
    "human_version": "1.0.0"
}
```

### Configuration Path Resolution

The add-on uses a robust path resolution system with multiple fallback methods:

1. **Primary**: `addonManager.addonFolder(__name__)`
2. **Secondary**: `addonManager.addon_meta(__name__).path`
3. **Tertiary**: `addonManager.addon_path(__name__)`
4. **Fallback**: `os.path.dirname(__file__)`

This ensures compatibility across different Anki versions and platforms.

### Error Handling in Configuration

```python
# Automatic fallback to defaults
if not os.path.exists(config_path):
    return get_default_config()

# Key validation and completion
default_config = get_default_config()
for key in default_config:
    if key not in config:
        config[key] = default_config[key]

# Graceful error handling
except PermissionError as e:
    print(f"Permission denied: {e}")
    return False
```

### Configuration API Reference

#### Core Functions

```python
def get_config_path():
    """
    Returns the path to config.json with robust fallback mechanisms.
    Handles different Anki versions and platform differences.
    """

def get_default_config():
    """
    Returns the default configuration structure.
    Used as fallback when config.json doesn't exist or is corrupted.
    """

def get_config():
    """
    Loads current configuration from config.json.
    - Automatically falls back to defaults if file missing
    - Validates and completes missing keys
    - Handles JSON parsing errors gracefully
    """

def save_config(config):
    """
    Saves configuration to config.json.
    - Creates directory if it doesn't exist
    - Handles permission errors
    - Uses UTF-8 encoding with proper JSON formatting
    - Returns True/False for success/failure
    """
```

#### Configuration Structure Details

```python
{
    "note_type": "Basic",                    # Current note type name
    "main_field": "Front",                   # Field for auto-search
    "refresh_shortcut": "Ctrl+R",            # Keyboard shortcut
    "configurable_fields": {                 # Fields per note type
        "Basic": ["Back", "Extra"],
        "Cloze": ["Text", "Extra"]
    },
    "field_search_configs": {                # Detailed site configs
        "Basic": {
            "Back": {
                "English": {
                    "Cambridge Dictionary": true,
                    "Oxford Dictionary": false
                },
                "Image": {
                    "Google Images": true
                }
            }
        }
    }
}
```

#### Error Handling Patterns

The configuration system implements comprehensive error handling:

```python
# Path resolution with fallbacks
try:
    if hasattr(mgr, "addonFolder"):
        addon_dir = mgr.addonFolder(__name__)
    elif hasattr(mgr, "addon_meta"):
        # Multiple fallback methods...
except Exception as e:
    print(f"Error getting addon path: {e}")
    addon_dir = os.path.dirname(__file__)  # Ultimate fallback

# JSON loading with validation
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Ensure all required keys exist
    default_config = get_default_config()
    for key in default_config:
        if key not in config:
            config[key] = default_config[key]
            
except Exception as e:
    print(f"Failed to load configuration: {e}")
    return get_default_config()
```

### Search Site Categories

The add-on supports multiple categories of search sites with specific URL templates:

#### English Dictionaries (10 sites)
- **Cambridge Dictionary**: `https://dictionary.cambridge.org/dictionary/english/{}`
- **Oxford Dictionary**: `https://www.oxfordlearnersdictionaries.com/definition/english/{}_1?q={}`
- **Merriam-Webster**: `https://www.merriam-webster.com/dictionary/{}`
- **Longman Dictionary**: `https://www.ldoceonline.com/dictionary/{}`
- **Collins Dictionary**: `https://www.collinsdictionary.com/dictionary/english/{}`
- **Macmillan Dictionary**: `https://www.macmillandictionary.com/search/?q={}`
- **Urban Dictionary**: `https://www.urbandictionary.com/define.php?term={}`
- **Vocabulary.com**: `https://www.vocabulary.com/dictionary/{}`
- **The Free Dictionary**: `https://www.thefreedictionary.com/{}`
- **Dictionary.com**: `https://www.dictionary.com/browse/{}`

#### Tiáº¿ng Viá»‡t Resources (4 sites)
- **Cambridge Viá»‡t**: `https://dictionary.cambridge.org/dictionary/english-vietnamese/{}`
- **Dunno**: `https://dunno.ai/search/word/{}?hl=vi`
- **Laban**: `https://dict.laban.vn/find?type=1&query={}`
- **VDict**: `https://vdict.com/{},1,0,0.html`

#### Example & Sentence Sources (5 sites)
- **Dunno Examples**: `https://dunno.ai/search/example/{}?hl=vi`
- **TraCau**: `https://tracau.vn/?s={}`
- **Ludwig**: `https://ludwig.guru/s/{}`
- **Sentence Stack**: `https://sentencestack.com/q/{}`
- **Fraze.it**: `https://fraze.it/n_search.jsp?q={}&l=0`

#### Thesaurus Resources (3 sites)
- **Thesaurus.com**: `https://www.thesaurus.com/browse/{}`
- **Power Thesaurus**: `https://www.powerthesaurus.org/{}`
- **Merriam-Webster Thesaurus**: `https://www.merriam-webster.com/thesaurus/{}`

#### Image Search Engines (4 sites)
- **Google Images**: `https://www.google.com/search?q={}&tbm=isch`
- **Bing Images**: `https://www.bing.com/images/search?q={}`
- **Giphy**: `https://giphy.com/search/{}`
- **Tenor**: `https://tenor.com/search/{}`

### Adding New Search Sites

To add new search sites, follow these steps:

1. **Edit `PREDEFINED_SEARCH_SITES` in `config.py`**:
```python
PREDEFINED_SEARCH_SITES = {
    "English": {
        "New Dictionary": "https://newdictionary.com/search?q={}",
        # ... existing sites
    },
    "New Category": {
        "Site Name": "https://example.com/search/{}"
    }
}
```

2. **URL Template Guidelines**:
   - Use `{}` as placeholder for the search term
   - Multiple placeholders supported: `"https://site.com/{}?lang={}"` 
   - Search terms are automatically URL-encoded
   - Special characters and spaces handled automatically

3. **Test URL Format**:
```python
# Test your URL template
search_term = "hello world"
url_template = "https://example.com/search?q={}"
final_url = url_template.format(search_term.replace(' ', '+'))
# Result: https://example.com/search?q=hello+world
```

4. **Category Organization**:
   - Group similar sites by language or content type
   - Use descriptive category names
   - Keep site names concise (truncated at 15 characters in tabs)

5. **URL Encoding Considerations**:
   - Spaces â†’ `+` (automatic)
   - Special characters â†’ URL encoded
   - Multiple placeholders get the same search term

Example addition:
```python
"Programming": {
    "Stack Overflow": "https://stackoverflow.com/search?q={}",
    "GitHub": "https://github.com/search?q={}",
    "MDN Web Docs": "https://developer.mozilla.org/en-US/search?q={}"
}
```

---

## Testing

### Test Structure
```
tests/
â”œâ”€â”€ conftest.py         # pytest fixtures and setup
â”œâ”€â”€ test_config.py      # Configuration system tests
â””â”€â”€ __pycache__/       # Python cache
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_config.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=.
```

### Test Coverage
- Configuration loading and saving
- Default configuration generation
- Search site URL formatting
- Error handling

### Adding New Tests

1. Create test functions in appropriate test files
2. Use `load_module` fixture for testing modules
3. Mock Anki dependencies when necessary
4. Test both success and error cases

---

## Contributing

### Development Guidelines

1. **Code Style**:
   - Follow PEP 8 guidelines
   - Use meaningful variable and function names
   - Add docstrings for public functions

2. **Git Workflow**:
   - Create feature branches: `git checkout -b feature/new-feature`
   - Make atomic commits with clear messages
   - Test before committing

3. **Pull Request Process**:
   - Fork the repository
   - Create a feature branch
   - Implement changes with tests
   - Submit pull request with clear description

### Areas for Contribution

- **New Search Sites**: Add support for additional dictionaries/resources
- **UI Improvements**: Enhance the settings dialog and browser interface
- **Performance**: Optimize browser rendering and memory usage
- **Internationalization**: Add support for more languages
- **Testing**: Increase test coverage

### Code Review Checklist

- [ ] Code follows project style guidelines
- [ ] New features include appropriate tests
- [ ] Documentation is updated
- [ ] No breaking changes to existing functionality
- [ ] Performance impact is considered

---

## Build & Deployment

### Creating a Release

1. **Update version numbers**:
   - `manifest.json`: Update `human_version`
   - `CHANGELOG.md`: Add release notes

2. **Test thoroughly**:
   - Run all tests: `pytest`
   - Test in multiple Anki versions
   - Test all major features

3. **Create release package**:
   ```bash
   # Create clean directory without development files
   mkdir release
   cp -r *.py *.json *.md LICENSE release/
   cd release
   zip -r AnkiVN-Better-Web-Browser-v1.0.0.zip .
   ```

### Distribution

- **AnkiWeb**: Submit to Anki's official add-on repository
- **GitHub Releases**: Create tagged releases with ZIP files
- **Documentation**: Update README and documentation

---

## Technical Requirements

### Current Anki Version Support (2025)

**Officially Supported Versions:**
- **Anki 25.07.2** (Latest stable - July 2025)
- **Anki 25.08b1** (Latest beta - includes Qt 6.9)
- **Anki 25.07.1** (Previous stable)
- **Anki 25.07** (Major release with new launcher)

**New Launcher System (25.07+):**
- **Minimum version**: 2.1.50 (oldest supported for installation)
- **Upgrade/Downgrade**: Built-in Tools > Upgrade/Downgrade menu
- **Distribution**: Online launcher replaces traditional installers
- **Platform support**: AMD64 (Intel) and ARM64 (Apple Silicon) on Mac/Linux

### System Requirements

**Qt Framework:**
- **Current**: Qt 6.9 (as of Anki 25.08b1)
- **Minimum**: Qt 6.8+ recommended
- **Compatibility**: Qt 5 support removed in 25.07+

**Python Environment:**
- **Bundled with Anki**: Python 3.13 (25.07+)
- **Minimum supported**: Python 3.9 (maintained for backward compatibility)
- **Add-on compatibility**: Uses Anki's bundled Python environment

**Operating System Support:**
- **Linux**: glibc 2.36+ required (as of 25.07+)
- **Windows**: AMD64 architecture (ARM64 runs in emulation)
- **macOS**: Native support for Intel and Apple Silicon

**Development Requirements:**
- **pytest**: For test suite execution (optional)
- **Git**: Version control for development
- **IDE/Editor**: Python development environment

### Anki Version Compatibility Timeline

**2025 Releases (New Versioning):**
| Version | Release Date | Status | Key Features |
|---------|-------------|--------|--------------|
| 25.08b1 | July 2025 | Beta | Qt 6.9, crash fixes |
| 25.07.2 | July 2025 | âœ… Stable | Bug fixes, improvements |
| 25.07.1 | July 2025 | âœ… Stable | Regression fixes |
| 25.07 | July 2025 | âœ… Stable | New launcher, Python 3.13 |
| 25.06b7 | June 2025 | Beta | Launcher updates |
| 25.06b6 | June 2025 | Beta | Tools > Upgrade/Downgrade |

**Legacy 2.1.x Versions (Pre-2025):**
| Version Range | Status | Notes |
|--------------|--------|-------|
| 2.1.50 - 2.1.720 | âœ… Compatible | Minimum supported version |
| 2.1.49 and below | âŒ Unsupported | Not supported by new launcher |

### Compatibility Matrix

**Add-on Compatibility:**
- **Anki 25.07.2+**: âœ… Fully compatible, recommended
- **Anki 25.07+**: âœ… Compatible with new launcher
- **Anki 2.1.50-2.1.720**: âœ… Compatible via launcher
- **Anki 2.1.49 and below**: âŒ Not supported

**Feature Support:**
- **QWebEngineView**: Full support in Qt 6.8+
- **Browser Integration**: Compatible with all supported versions
- **Configuration System**: Backward compatible with 2.1.50+
- **Keyboard Shortcuts**: Full support in Qt 6.8+

### Platform-Specific Notes

**Linux:**
- **glibc**: Version 2.36+ required (25.07+)
- **Package managers**: Use new launcher instead of distro packages
- **ARM64**: Native support available

**Windows:**
- **Architecture**: AMD64 primary, ARM64 emulation
- **Launcher**: Replaces traditional MSI installer
- **Compatibility**: Windows 10+ recommended

**macOS:**
- **Intel Macs**: Native AMD64 support
- **Apple Silicon**: Native ARM64 support
- **Launcher**: Universal binary support

### Testing Strategy

**Version Testing:**
- **Primary**: Latest stable (25.07.2)
- **Secondary**: Latest beta (25.08b1)
- **Legacy**: Selected 2.1.x versions

**Compatibility Testing:**
- **Qt versions**: 6.8, 6.9
- **Python versions**: 3.9, 3.10, 3.11, 3.12, 3.13
- **Operating systems**: Windows 10+, macOS 10.15+, Linux (glibc 2.36+)

### Migration Guide

**From 2.1.x to 25.x:**
1. Install new launcher from GitHub releases
2. Use Tools > Upgrade/Downgrade to update
3. Verify add-on compatibility
4. Check configuration file integrity

**Compatibility Warnings:**
- Qt 5 support removed in 25.07+
- Python 3.8 and below not supported
- Legacy configuration formats may need migration

---

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! Please see the [Contributing](#contributing) section for development guidelines and the [Development Setup](#development-setup) section for getting started.

---

## Support

For support, please create an issue on the GitHub repository with:
- Anki version information
- Operating system details
- Steps to reproduce the issue
- Expected vs actual behavior
- Screenshots if applicable

---

*This documentation is comprehensive and designed for developers. For user-facing documentation, please refer to the add-on's AnkiWeb page.*
