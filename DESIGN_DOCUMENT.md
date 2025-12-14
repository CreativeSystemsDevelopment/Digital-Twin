# Neomorphic Document Upload Interface - Design Document

## Design Philosophy

The new interface will embody **neomorphism** (soft UI) principles combined with modern glassmorphism and subtle animations to create an elegant, professional, and awe-inspiring experience.

## Core Design Principles

### 1. Neomorphic Elements
- **Soft shadows**: Elements appear to extrude from or indent into the background
- **Subtle depth**: Multi-layered shadow system (light + dark) for 3D effect
- **Monochromatic palette**: Variations of a base color for cohesion
- **Smooth surfaces**: Rounded corners and gentle gradients

### 2. Color Palette
- **Base**: `#e0e5ec` (light neomorphic) or `#1a1d29` (dark neomorphic)
- **Shadow Light**: `rgba(255, 255, 255, 0.7)`
- **Shadow Dark**: `rgba(0, 0, 0, 0.15)`
- **Accent**: `#6366f1` (indigo) for interactive elements
- **Success**: `#10b981` (emerald)
- **Warning**: `#f59e0b` (amber)
- **Error**: `#ef4444` (red)

### 3. Component Architecture

#### A. Upload Zone
- Large drag-and-drop area with neomorphic inset effect
- Animated border on drag-over
- File preview cards with soft shadows
- Progress indicators with gradient fills

#### B. Machine Selector
- Elegant dropdown with neomorphic styling
- Smooth expand/collapse animations
- Search functionality with live filtering
- Create new machine option with inline form

#### C. File Cards
- Individual file representation with neomorphic raised effect
- File type icons with subtle glow
- Size and status indicators
- Remove button with hover effects
- Category selector for each file

#### D. Processing Status
- Real-time progress visualization
- Animated status orbs with pulsing effects
- Success/error states with smooth transitions
- Detailed logs in expandable sections

#### E. Action Buttons
- Primary: Neomorphic raised with gradient on hover
- Secondary: Neomorphic flat with subtle highlight
- Disabled: Reduced opacity with inset effect

## Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│  Header: Digital Twin - Document Processing             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  Machine Selector (Neomorphic Dropdown)        │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │                                                 │    │
│  │     Drag & Drop Upload Zone                    │    │
│  │     (Neomorphic Inset)                         │    │
│  │                                                 │    │
│  │     Click to browse or drag files here         │    │
│  │                                                 │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  File Preview Grid:                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ File 1   │  │ File 2   │  │ File 3   │             │
│  │ [Icon]   │  │ [Icon]   │  │ [Icon]   │             │
│  │ Name     │  │ Name     │  │ Name     │             │
│  │ Size     │  │ Size     │  │ Size     │             │
│  │ Category │  │ Category │  │ Category │             │
│  │ [Remove] │  │ [Remove] │  │ [Remove] │             │
│  └──────────┘  └──────────┘  └──────────┘             │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  [Upload & Process] (Primary Action Button)    │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  Processing Status (when active):                       │
│  ┌────────────────────────────────────────────────┐    │
│  │  ● Processing file 2 of 5...                   │    │
│  │  [████████████░░░░░░░░] 60%                    │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Animation & Interaction Details

### Micro-interactions
1. **File drop**: Smooth scale-in animation with bounce
2. **Button press**: Inset effect (shadow inversion)
3. **Hover states**: Subtle lift with shadow expansion
4. **Progress**: Smooth gradient animation left-to-right
5. **Status changes**: Color transition with fade effect

### Transitions
- Duration: 200-300ms for interactions, 500ms for state changes
- Easing: `cubic-bezier(0.4, 0.0, 0.2, 1)` for smooth, natural feel
- Stagger: 50ms delay between multiple elements

## Accessibility
- ARIA labels for all interactive elements
- Keyboard navigation support
- Focus indicators with neomorphic styling
- High contrast mode compatibility
- Screen reader announcements for status changes

## Technical Implementation Notes
- Use CSS custom properties for consistent theming
- Framer Motion for complex animations
- React Hook Form for form management
- TanStack Query for API state management
- Tailwind CSS for utility-first styling with custom neomorphic utilities
