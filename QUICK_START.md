# Quick Start Guide - Neomorphic Document Upload UI

## Getting Started

### 1. Install Dependencies
```bash
cd frontend
pnpm install
```

### 2. Run Development Server
```bash
pnpm run dev
```

The application will be available at `http://localhost:5173`

### 3. Navigate to Document Processing
- Open the application in your browser
- Click "Import" from the home page
- Or navigate directly to `/documents`

## Using the Interface

### Step 1: Select a Machine
1. Click the machine selector dropdown
2. Search for an existing machine or create a new one
3. Your selection will be saved

### Step 2: Upload Documents
1. Drag files into the upload zone, or click to browse
2. Supported formats: PDF, DOC, DOCX
3. Multiple files can be uploaded at once

### Step 3: Review and Categorize
1. Each file appears as a card with preview
2. Categories are auto-detected from filenames
3. Adjust categories manually if needed

### Step 4: Upload
1. Click "Upload & Process" button
2. Watch real-time progress for each file
3. Success/error status displayed inline

## Key Features

- **Neomorphic Design**: Soft, elegant 3D-style interface
- **Drag & Drop**: Intuitive file upload
- **Smart Categories**: Auto-detection with manual override
- **Real-time Progress**: Visual feedback during upload
- **Responsive**: Works on desktop, tablet, and mobile
- **Accessible**: Keyboard navigation and screen reader support

## Component API

### MachineSelector
```tsx
<MachineSelector 
  value={selectedMachine} 
  onChange={(id) => setSelectedMachine(id)} 
/>
```

### DocumentUpload
```tsx
<DocumentUpload 
  machineId={selectedMachine}
  onUploadComplete={() => console.log('Done!')}
/>
```

## Customization

### Colors
Edit CSS variables in `src/index.css`:
```css
:root {
  --neo-bg: #e0e5ec;
  --accent-primary: #6366f1;
  /* ... */
}
```

### Categories
Edit the `CATEGORIES` array in `src/components/DocumentUpload.tsx`

### Animations
Adjust timing in `src/index.css` keyframes and transitions

## Troubleshooting

**Issue**: Build fails
**Solution**: Run `pnpm install` again, ensure Node.js 22+ is installed

**Issue**: Styles not loading
**Solution**: Clear browser cache, restart dev server

**Issue**: Upload not working
**Solution**: Ensure backend API is running and accessible

## Next Steps

1. Connect to backend API endpoints
2. Test with real document uploads
3. Customize colors and branding
4. Add additional features as needed

For detailed documentation, see:
- `UI_REFACTOR_README.md` - Complete feature guide
- `COMPONENT_SHOWCASE.md` - Design system details
- `REFACTOR_SUMMARY.md` - Technical overview
