# Feature Plan: Formatic UI Implementation

## Epic Overview

**User Value**
Formatic UI is a new, modular component system designed to modernize the website's interface. It provides reusable, consistent, and accessible UI components (atoms and molecules) that replace ad-hoc HTML/CSS. This improves maintainability, ensures design consistency, and speeds up future development.

**Success Metrics**
- **Reusability**: Core components (Button, Input, Card) implemented as Hugo partials.
- **Consistency**: Centralized styling via SCSS.
- **Adoption**: At least one major page (e.g., Contact or Blog list) migrated to use Formatic components.
- **Documentation**: Usage guide for each component.

**Scope**
- **Included**:
    - SCSS architecture for Formatic.
    - Core Atoms: Button, Input, Label, Icon wrapper.
    - Core Molecules: Card, Modal, Alert.
    - Migration of "Contact" page to use Formatic.
- **Excluded**:
    - Complete rewrite of Semantic UI (Formatic will sit alongside or extend it initially).
    - Complex data grids or charts.

## Story Breakdown

### Story 1: Foundation & Scaffolding [1 day]
**User Value**: Establishes the technical groundwork for the component library.
**Acceptance Criteria**:
- `themes/espouse/layouts/partials/formatic/` directory exists.
- `themes/espouse/sass/formatic.scss` created and imported.
- Basic build pipeline verifies SCSS compilation.

### Story 2: Core Atoms (Inputs & Buttons) [1-2 days]
**User Value**: Provides the basic building blocks for forms and actions.
**Acceptance Criteria**:
- Button component supports variants (primary, secondary, ghost) and sizes.
- Input component supports types, labels, and error states.
- Components are accessible (aria attributes).

### Story 3: Molecules & Layouts [2-3 days]
**User Value**: Provides higher-level UI patterns.
**Acceptance Criteria**:
- Card component for blog posts/projects.
- Container/Grid wrappers (if not using Semantic's grid).

## Atomic Task Decomposition

### Task 1.1: Formatic UI Scaffolding (1h)
- **Objective**: Set up the directory structure and SCSS foundation.
- **Status**: ⏳ Pending
- **Files**:
    - `themes/espouse/layouts/partials/formatic/README.md` (create)
    - `themes/espouse/sass/formatic.scss` (create)
    - `themes/espouse/sass/espouse.scss` (modify to import)
- **Implementation**:
    - Create directories.
    - Add basic variables (colors, spacing) to `formatic.scss`.
    - Import `formatic.scss` in `espouse.scss`.

### Task 1.2: Button Component (2h)
- **Objective**: Create a reusable Button partial.
- **Status**: ⏳ Pending
- **Files**:
    - `themes/espouse/layouts/partials/formatic/button.html` (create)
    - `themes/espouse/sass/formatic.scss` (modify)
- **Implementation**:
    - Define partial with params: `text`, `href`, `type`, `class`, `variant`.
    - Implement SCSS for `.fmt-btn`, `.fmt-btn--primary`, etc.
    - Ensure hover/focus states.

### Task 1.3: Input Component (2h)
- **Objective**: Create a reusable Input partial with label support.
- **Status**: ⏳ Pending
- **Files**:
    - `themes/espouse/layouts/partials/formatic/input.html` (create)
    - `themes/espouse/sass/formatic.scss` (modify)
- **Implementation**:
    - Define partial with params: `name`, `label`, `type`, `placeholder`, `required`.
    - Implement SCSS for `.fmt-input-group`, `.fmt-label`, `.fmt-input`.

### Task 2.1: Card Component (3h)
- **Objective**: Create a flexible Card component for content listing.
- **Status**: ⏳ Pending
- **Files**:
    - `themes/espouse/layouts/partials/formatic/card.html` (create)
    - `themes/espouse/sass/formatic.scss` (modify)
- **Implementation**:
    - Support slots/params for: `image`, `title`, `meta`, `description`, `link`.
    - Style for responsiveness.

## Dependency Visualization

```
[Start]
   |
   +---> [Task 1.1: Scaffolding]
           |
           +---> [Task 1.2: Button Component]
           |       |
           +---> [Task 1.3: Input Component]
                   |
                   +---> [Task 2.1: Card Component]
```

## Context Preparation Guide
- **Task 1.1**:
    - Open `themes/espouse/sass/espouse.scss` to understand current imports.
    - Review Hugo Partial syntax.

## Links
- **Main TODO**: [../../TODO.md](../../TODO.md)
