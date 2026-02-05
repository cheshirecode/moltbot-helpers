# OpenClaw Shared Components

A collection of reusable components for both the main dashboard and demo system, ensuring consistency across all OpenClaw interfaces.

## Components Overview

### 1. Universal Data Adapter
- **Purpose**: Provides consistent interface for different data sources
- **Supports**: PostgreSQL (main system) and IndexedDB (demo/offline)
- **Features**:
  - Abstract data access layer
  - Sync capabilities between sources
  - Fallback mechanisms
  - Offline-first architecture

### 2. Shared UI Components
- **Purpose**: Reusable UI elements for consistent experience
- **Components**:
  - Chart components (bar, doughnut, line)
  - Table components with sorting/filtering
  - Modal dialogs
  - Forms with validation
  - Dashboard cards
  - Stats grids

### 3. State Management System
- **Purpose**: Centralized application state management
- **Features**:
  - Reactive state updates
  - Subscription model
  - Change tracking
  - Undo/redo capabilities

### 4. Theme Management System
- **Purpose**: Consistent styling across applications
- **Features**:
  - CSS variable-based themes
  - Multiple theme options
  - Persistent user preferences
  - Accessibility support

## Usage Examples

### Universal Data Adapter
```javascript
// For main system (PostgreSQL)
const apiAdapter = new ApiAdapter('/api');
const dataAdapter = new UniversalDataAdapter(apiAdapter);

// For demo system (IndexedDB)
const indexedDBAdapter = new IndexedDBAdapter();
await indexedDBAdapter.init();
const dataAdapter = new UniversalDataAdapter(indexedDBAdapter);

// Consistent interface regardless of source
const projects = await dataAdapter.getProjects();
const projectDetails = await dataAdapter.getProjectDetails('my-project');
```

### Shared UI Components
```python
from ui_components import ChartComponent, TableComponent, ModalComponent

# Create a bar chart
bar_chart = ChartComponent.create_bar_chart(
    'statusChart', 
    'Tasks by Status', 
    {'completed': 15, 'in-progress': 8, 'todo': 12}
)

# Create a data table
table = TableComponent.create_data_table(
    'projectsTable',
    ['Project', 'Status', 'Progress'],
    [['Project A', 'Active', '75%'], ['Project B', 'Planning', '25%']]
)

# Create a modal
modal = ModalComponent.create_modal(
    'infoModal',
    'Project Information',
    '<p>Details about the selected project...</p>',
    '<button onclick="...">OK</button>'
)
```

## Implementation Strategy

### Phase 1: Foundation
- [x] Universal Data Adapter (Python)
- [x] Universal Data Adapter (JavaScript)
- [x] Shared UI Components (Python)
- [x] Data synchronization capabilities

### Phase 2: Enhancement
- [ ] Advanced UI components (PWA features)
- [ ] State management system
- [ ] Theme management system
- [ ] Form validation utilities

### Phase 3: Integration
- [ ] Integrate with main dashboard
- [ ] Integrate with demo system
- [ ] Cross-component communication
- [ ] Performance optimization

### Phase 4: Expansion
- [ ] Advanced analytics components
- [ ] Collaboration features
- [ ] API playground components
- [ ] Customization engine

## Benefits

1. **Consistency**: Same UI/UX across main and demo systems
2. **Maintainability**: Single source of truth for components
3. **Scalability**: Easy to extend and modify
4. **Efficiency**: Reduced code duplication
5. **Reliability**: Tested components across environments

## Architecture

The shared components follow a modular architecture:

```
shared-components/
├── universal_data_adapter.py    # Python backend adapter
├── universal_data_adapter.js    # JavaScript frontend adapter
├── ui_components.py            # Python UI components
├── state_manager.py            # State management
├── theme_manager.py            # Theme management
└── utils/                      # Utility functions
```

Each component is designed to be independent but work seamlessly together.