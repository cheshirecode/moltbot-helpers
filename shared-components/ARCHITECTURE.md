# OpenClaw Shared Components Architecture

## Overview
This document outlines the architecture for shared components between the main OpenClaw dashboard and the demo system, ensuring consistency while maintaining security through separation.

## Core Principles
1. **Security First**: Complete data isolation between main and demo systems
2. **Consistency**: Shared UI/UX patterns across systems
3. **Flexibility**: Adapters for different data sources and environments
4. **Maintainability**: Single source of truth for common components

## Component Architecture

### 1. Universal Data Layer
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Application   │◄──►│ Universal Data  │◄──►│ PostgreSQL API  │
│   Components    │    │   Adapter       │    │ (Main System)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                           │
                           ▼
                    ┌─────────────────┐
                    │   IndexedDB     │
                    │ (Demo System)   │
                    └─────────────────┘
```

#### Key Features:
- Abstract data access through common interface
- Automatic fallback between data sources
- Offline-first architecture
- Sync capabilities between sources

### 2. Shared UI Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Main App      │    │   Demo App      │    │  Component Lib  │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │  Dashboard  │ │    │ │  Dashboard  │ │    │ │  Chart Comp │ │
│ │             │ │    │ │             │ │    │ │             │ │
│ │  ┌───────┐  │ │    │ │  ┌───────┐  │ │    │ │             │ │
│ │  │Chart  │  │ │◄───┼─┼──┤Chart  │  │ │◄───┼─┤             │ │
│ │  └───────┘  │ │    │ │  └───────┘  │ │    │ │             │ │
│ │             │ │    │ │             │ │    │ │             │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### Components Include:
- Chart components (bar, doughnut, line)
- Table components with sorting/filtering
- Modal dialogs
- Form components with validation
- Dashboard cards and layouts

### 3. State Management System
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UI Layer      │    │  State Manager  │    │   Persistence   │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │   React     │ │◄───┼─┤   Central   │ │◄───┼─┤   Local     │ │
│ │   Views     │ │    │ │   Store     │ │    │ │   Storage   │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │   Widgets   │ │◄───┼─┤   Events    │ │    │ │   IndexedDB │ │
│ │             │ │    │ │   System    │ │    │ │             │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Implementation Strategy

### Phase 1: Foundation (Current)
- [X] Universal Data Adapter (Python/JS)
- [X] Basic UI Components (Python)
- [X] PostgreSQL-to-IndexedDB Mirror
- [X] Demo deployment to Vercel

### Phase 2: Enhancement (Next)
- [ ] Advanced UI Components
- [ ] State Management System
- [ ] Theme Management System
- [ ] PWA Capabilities

### Phase 3: Integration
- [ ] Main dashboard integration
- [ ] Cross-component communication
- [ ] Performance optimization

### Phase 4: Advanced Features
- [ ] Advanced analytics components
- [ ] Collaboration features
- [ ] Customization engine

## Security Considerations

### Data Isolation
- Separate databases for main and demo systems
- No shared credentials or access tokens
- Network isolation between environments
- Sanitized data transfer protocols

### Access Control
- Role-based access in main system
- Anonymous access in demo system
- API rate limiting
- Input validation and sanitization

## Technology Stack

### Frontend
- JavaScript/ES6 for browser components
- Chart.js for data visualization
- IndexedDB for local storage
- Service Workers for offline capability

### Backend (Python)
- Flask for API endpoints
- PostgreSQL for main data
- JSON for data interchange
- Environment-based configuration

### Deployment
- Vercel for demo deployment
- Containerized environments
- CI/CD pipelines
- Automated testing

## Development Guidelines

### Component Design
1. Follow single responsibility principle
2. Maintain loose coupling between components
3. Use dependency injection for flexibility
4. Implement proper error handling

### Testing Strategy
1. Unit tests for individual components
2. Integration tests for component interactions
3. End-to-end tests for complete workflows
4. Security testing for data isolation

### Documentation
1. API documentation for all components
2. Architecture diagrams for system understanding
3. Usage examples for developers
4. Security guidelines for deployment