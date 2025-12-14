# Component Showcase - Neomorphic UI Elements

## Visual Design Language

### Neomorphic Shadow System

The interface uses a sophisticated shadow system to create depth and dimension:

**Raised Elements** (buttons, cards):
```css
box-shadow: 
  8px 8px 16px rgba(163, 177, 198, 0.6),    /* Dark shadow (bottom-right) */
  -8px -8px 16px rgba(255, 255, 255, 0.8);  /* Light shadow (top-left) */
```

**Inset Elements** (input fields, upload zone):
```css
box-shadow: 
  inset 6px 6px 12px rgba(163, 177, 198, 0.6),
  inset -6px -6px 12px rgba(255, 255, 255, 0.8);
```

**Flat Elements** (subtle containers):
```css
box-shadow: 
  4px 4px 8px rgba(163, 177, 198, 0.6),
  -4px -4px 8px rgba(255, 255, 255, 0.8);
```

---

## Component Breakdown

### 1. Machine Selector

**Visual Characteristics:**
- Neomorphic flat container with smooth rounded corners
- Circular avatar with gradient text (first 2 letters of machine name)
- Dropdown with search functionality
- Smooth rotation animation on chevron icon (0° → 180°)

**Interaction States:**
- **Closed**: Flat neomorphic style
- **Open**: Dropdown appears with raised neomorphic card
- **Hover**: Subtle lift effect
- **Focus**: Accent color outline

**Features:**
- Real-time search filtering
- Create new machine inline
- Document count display
- Selected state with checkmark

---

### 2. Document Upload Zone

**Visual Characteristics:**
- Large inset neomorphic area (appears sunken into background)
- Upload icon with accent color
- Clear instructional text hierarchy
- Supported formats hint

**Interaction States:**
- **Default**: Inset appearance with subtle shadows
- **Hover**: Cursor changes to pointer
- **Drag Over**: Border highlight with accent color + background tint
- **Active**: Scale animation on upload icon

**Features:**
- Drag and drop support
- Click to browse files
- Multiple file selection
- File type validation

---

### 3. File Preview Cards

**Visual Characteristics:**
- Raised neomorphic cards in grid layout
- File icon in nested flat container
- Truncated filename with tooltip
- File size display
- Category dropdown
- Remove button

**Interaction States:**
- **Default**: Raised with soft shadows
- **Hover**: Increased elevation (translateY -4px)
- **Uploading**: Progress bar appears
- **Success**: Green checkmark icon
- **Error**: Red alert icon

**Layout:**
- Responsive grid: 1 column (mobile) → 2 columns (tablet+)
- Stagger animation on appearance (50ms delay per card)
- Smooth exit animation on removal

---

### 4. Category Selector

**Visual Characteristics:**
- Neomorphic inset select element
- Custom styling matching design system
- Clear label with secondary text color

**Categories:**
1. Manual Contents
2. Schematic Diagram
3. Electrical Construction
4. Electrical Parts List
5. Cable List
6. Error List
7. Terminal Box Wiring
8. General Arrangement
9. Panel Outline
10. Unknown / Other

**Auto-Detection Logic:**
- Filename parsing for keywords
- Intelligent categorization
- User can override selection

---

### 5. Progress Indicators

**Visual Characteristics:**
- Neomorphic inset track
- Gradient-filled progress bar
- Shimmer animation overlay
- Percentage display

**Status Orbs:**
- **Pending**: Gray orb (static)
- **Processing**: Blue orb (pulsing animation)
- **Success**: Green orb (pulse + checkmark)
- **Error**: Red orb (alert icon)

**Animation:**
- Smooth width transition (300ms cubic-bezier)
- Shimmer effect moving left to right
- Pulsing scale animation (1.0 → 1.15)

---

### 6. Primary Action Button

**Visual Characteristics:**
- Gradient background (indigo → purple)
- Raised neomorphic shadows
- White text with icon
- Shimmer effect on hover

**Interaction States:**
- **Default**: Raised with gradient
- **Hover**: Increased elevation + glow + shimmer sweep
- **Active**: Returns to base position
- **Disabled**: Reduced opacity + inset shadow

**Loading State:**
- Spinning loader icon
- "Uploading..." text
- Disabled interaction

---

## Animation Specifications

### Timing Functions

```javascript
// Standard easing
cubic-bezier(0.4, 0.0, 0.2, 1)

// Bounce effect (for file drop)
cubic-bezier(0.68, -0.55, 0.265, 1.55)
```

### Duration Guidelines

| Interaction Type | Duration |
|-----------------|----------|
| Button press | 200ms |
| Hover effect | 300ms |
| State change | 500ms |
| Page transition | 600ms |
| Stagger delay | 50ms |

### Key Animations

**Fade In:**
```css
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

**Pulse (Status Orbs):**
```css
@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.15);
  }
}
```

**Shimmer (Progress Bar):**
```css
@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
```

**Gradient Shift (Background):**
```css
@keyframes gradient-shift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
```

---

## Responsive Breakpoints

```css
/* Mobile First */
Default: 1 column grid, full width

/* Tablet (768px+) */
@media (min-width: 768px) {
  - 2 column grid for file cards
  - Increased padding
}

/* Desktop (1024px+) */
@media (min-width: 1024px) {
  - Max width container (6xl)
  - Larger text sizes
  - Enhanced hover effects
}

/* Large Desktop (1440px+) */
@media (min-width: 1440px) {
  - Spacious layout
  - Larger component sizes
}
```

---

## Color Palette

### Base Colors
```
Background:     #e0e5ec
Light Shadow:   rgba(255, 255, 255, 0.8)
Dark Shadow:    rgba(163, 177, 198, 0.6)
```

### Text Colors
```
Primary:   #2d3748
Secondary: #718096
Muted:     #a0aec0
```

### Accent Colors
```
Primary:   #6366f1 (Indigo)
Success:   #10b981 (Emerald)
Warning:   #f59e0b (Amber)
Error:     #ef4444 (Red)
```

### Gradients
```css
Primary:  linear-gradient(135deg, #667eea 0%, #764ba2 100%)
Success:  linear-gradient(135deg, #10b981 0%, #059669 100%)
Accent:   linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)
```

---

## Typography

### Font Family
```css
font-family: 'Inter', system-ui, -apple-system, sans-serif;
```

### Font Weights
- **Light**: 300 (subtle text)
- **Regular**: 400 (body text)
- **Medium**: 500 (labels)
- **Semibold**: 600 (headings)
- **Bold**: 700 (emphasis)

### Font Sizes
```
xs:   12px  (hints, metadata)
sm:   14px  (body, inputs)
base: 16px  (default)
lg:   18px  (section headings)
xl:   20px  (page titles)
2xl:  24px  (hero text)
4xl:  36px  (main heading)
```

---

## Accessibility Features

### Keyboard Navigation
- Tab through all interactive elements
- Enter to activate buttons/dropdowns
- Escape to close modals/dropdowns
- Arrow keys for dropdown navigation

### Screen Reader Support
- ARIA labels on all interactive elements
- Role attributes for semantic meaning
- Live regions for status updates
- Alt text for icons

### Visual Accessibility
- Focus indicators with accent color
- High contrast text ratios (WCAG AA)
- Large touch targets (min 48px)
- Clear visual hierarchy

---

## Performance Optimizations

### CSS
- Hardware-accelerated transforms
- Will-change hints for animations
- Efficient selectors
- Minimal repaints

### React
- Memoized components where appropriate
- Lazy loading for code splitting
- Optimized re-renders
- Virtual scrolling for large lists (future)

### Assets
- Optimized SVG icons
- Minimal external dependencies
- Tree-shaking enabled
- Gzip compression

---

## Design Principles

1. **Consistency**: All components follow the same design language
2. **Clarity**: Clear visual hierarchy and intuitive interactions
3. **Feedback**: Immediate visual response to all user actions
4. **Efficiency**: Minimal clicks to complete tasks
5. **Delight**: Smooth animations and polished details
6. **Accessibility**: Usable by everyone, regardless of ability
7. **Performance**: Fast, responsive, and lightweight

---

This neomorphic design system creates a cohesive, professional, and delightful user experience that elevates the Digital Twin platform to a new level of visual sophistication.
