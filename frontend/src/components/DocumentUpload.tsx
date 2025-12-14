import { useState, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, X, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

interface FileWithMetadata {
  file: File;
  id: string;
  category: string;
  status: 'pending' | 'uploading' | 'success' | 'error';
  progress: number;
  error?: string;
}

interface DocumentUploadProps {
  machineId: string;
  onUploadComplete?: () => void;
}

const CATEGORIES = [
  { value: 'manual_contents', label: 'Manual Contents' },
  { value: 'schematic', label: 'Schematic Diagram' },
  { value: 'electrical_construction_drawings', label: 'Electrical Construction' },
  { value: 'electrical_parts_list', label: 'Electrical Parts List' },
  { value: 'cable_list', label: 'Cable List' },
  { value: 'error_list', label: 'Error List' },
  { value: 'terminal_box_wiring_diagram', label: 'Terminal Box Wiring' },
  { value: 'general_arrangement', label: 'General Arrangement' },
  { value: 'panel_outline', label: 'Panel Outline' },
  { value: 'unknown', label: 'Unknown / Other' },
];

export default function DocumentUpload({ machineId, onUploadComplete }: DocumentUploadProps) {
  const [files, setFiles] = useState<FileWithMetadata[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    addFiles(droppedFiles);
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      addFiles(selectedFiles);
    }
  }, []);

  const addFiles = (newFiles: File[]) => {
    const filesWithMetadata: FileWithMetadata[] = newFiles.map(file => ({
      file,
      id: `${file.name}-${Date.now()}-${Math.random()}`,
      category: detectCategory(file.name),
      status: 'pending',
      progress: 0,
    }));
    
    setFiles(prev => [...prev, ...filesWithMetadata]);
  };

  const detectCategory = (filename: string): string => {
    const name = filename.toUpperCase();
    
    if (name.includes('CONTENTS') || name.includes('目次')) return 'manual_contents';
    if (name.includes('SCHEMATIC')) return 'schematic';
    if (name.includes('ELECTRICAL CONSTRUCTION')) return 'electrical_construction_drawings';
    if (name.includes('PARTS LIST')) return 'electrical_parts_list';
    if (name.includes('CABLE LIST')) return 'cable_list';
    if (name.includes('ERROR')) return 'error_list';
    if (name.includes('TERMINAL BOX')) return 'terminal_box_wiring_diagram';
    if (name.includes('GENERAL ARRANGEMENT')) return 'general_arrangement';
    if (name.includes('PANEL OUTLINE')) return 'panel_outline';
    
    return 'unknown';
  };

  const removeFile = (id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id));
  };

  const updateFileCategory = (id: string, category: string) => {
    setFiles(prev => prev.map(f => 
      f.id === id ? { ...f, category } : f
    ));
  };

  const uploadFiles = async () => {
    if (files.length === 0 || !machineId) return;
    
    setIsUploading(true);
    
    for (const fileItem of files) {
      try {
        // Update status to uploading
        setFiles(prev => prev.map(f => 
          f.id === fileItem.id ? { ...f, status: 'uploading', progress: 0 } : f
        ));

        const formData = new FormData();
        formData.append('file', fileItem.file);
        formData.append('machine_label', machineId);
        formData.append('category', fileItem.category);

        // Simulate progress (in real implementation, use XMLHttpRequest or fetch with progress)
        const progressInterval = setInterval(() => {
          setFiles(prev => prev.map(f => 
            f.id === fileItem.id && f.progress < 90 
              ? { ...f, progress: f.progress + 10 } 
              : f
          ));
        }, 200);

        const response = await fetch('/api/upload', {
          method: 'POST',
          body: formData,
        });

        clearInterval(progressInterval);

        if (response.ok) {
          setFiles(prev => prev.map(f => 
            f.id === fileItem.id 
              ? { ...f, status: 'success', progress: 100 } 
              : f
          ));
        } else {
          const error = await response.text();
          setFiles(prev => prev.map(f => 
            f.id === fileItem.id 
              ? { ...f, status: 'error', progress: 0, error } 
              : f
          ));
        }
      } catch (error) {
        setFiles(prev => prev.map(f => 
          f.id === fileItem.id 
            ? { ...f, status: 'error', progress: 0, error: String(error) } 
            : f
        ));
      }
    }
    
    setIsUploading(false);
    onUploadComplete?.();
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6">
      {/* Upload Zone */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className={`neo-inset p-12 text-center cursor-pointer transition-all ${
          isDragging ? 'drag-over' : ''
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.doc,.docx"
          onChange={handleFileSelect}
          className="hidden"
        />
        
        <motion.div
          animate={isDragging ? { scale: 1.1 } : { scale: 1 }}
          transition={{ duration: 0.2 }}
        >
          <Upload 
            className="mx-auto mb-4" 
            size={48} 
            strokeWidth={1.5}
            style={{ color: 'var(--accent-primary)' }}
          />
        </motion.div>
        
        <h3 className="text-xl font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
          {isDragging ? 'Drop files here' : 'Upload Documents'}
        </h3>
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
          Drag and drop files here, or click to browse
        </p>
        <p className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>
          Supported formats: PDF, DOC, DOCX
        </p>
      </motion.div>

      {/* File List */}
      <AnimatePresence mode="popLayout">
        {files.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-4"
          >
            <h4 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
              Files ({files.length})
            </h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 stagger-children">
              {files.map((fileItem, index) => (
                <motion.div
                  key={fileItem.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ delay: index * 0.05 }}
                  className="neo-file-card"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <div className="neo-flat p-3 shrink-0">
                        <FileText size={24} style={{ color: 'var(--accent-primary)' }} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p 
                          className="font-medium truncate" 
                          style={{ color: 'var(--text-primary)' }}
                          title={fileItem.file.name}
                        >
                          {fileItem.file.name}
                        </p>
                        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                          {formatFileSize(fileItem.file.size)}
                        </p>
                      </div>
                    </div>
                    
                    <button
                      onClick={() => removeFile(fileItem.id)}
                      className="neo-button p-2 ml-2 shrink-0"
                      disabled={fileItem.status === 'uploading'}
                    >
                      <X size={16} style={{ color: 'var(--text-secondary)' }} />
                    </button>
                  </div>

                  {/* Category Selector */}
                  <div className="mb-3">
                    <label className="block text-xs font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
                      Category
                    </label>
                    <select
                      value={fileItem.category}
                      onChange={(e) => updateFileCategory(fileItem.id, e.target.value)}
                      className="neo-input w-full text-sm"
                      disabled={fileItem.status === 'uploading'}
                    >
                      {CATEGORIES.map(cat => (
                        <option key={cat.value} value={cat.value}>
                          {cat.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Status */}
                  <div className="flex items-center gap-2">
                    {fileItem.status === 'pending' && (
                      <span className="text-xs flex items-center gap-1" style={{ color: 'var(--text-muted)' }}>
                        <div className="pulse-orb" style={{ background: 'var(--text-muted)' }} />
                        Ready to upload
                      </span>
                    )}
                    {fileItem.status === 'uploading' && (
                      <>
                        <Loader2 size={14} className="animate-spin" style={{ color: 'var(--accent-primary)' }} />
                        <span className="text-xs" style={{ color: 'var(--accent-primary)' }}>
                          Uploading... {fileItem.progress}%
                        </span>
                      </>
                    )}
                    {fileItem.status === 'success' && (
                      <>
                        <CheckCircle2 size={14} style={{ color: 'var(--accent-success)' }} />
                        <span className="text-xs" style={{ color: 'var(--accent-success)' }}>
                          Uploaded successfully
                        </span>
                      </>
                    )}
                    {fileItem.status === 'error' && (
                      <>
                        <AlertCircle size={14} style={{ color: 'var(--accent-error)' }} />
                        <span className="text-xs" style={{ color: 'var(--accent-error)' }}>
                          Upload failed
                        </span>
                      </>
                    )}
                  </div>

                  {/* Progress Bar */}
                  {fileItem.status === 'uploading' && (
                    <div className="neo-progress mt-3">
                      <motion.div
                        className="neo-progress-fill"
                        initial={{ width: 0 }}
                        animate={{ width: `${fileItem.progress}%` }}
                        transition={{ duration: 0.3 }}
                      />
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Upload Button */}
      {files.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex justify-center"
        >
          <button
            onClick={uploadFiles}
            disabled={isUploading || files.every(f => f.status === 'success')}
            className="neo-button-primary px-8 py-4 text-lg font-semibold"
          >
            {isUploading ? (
              <span className="flex items-center gap-2">
                <Loader2 size={20} className="animate-spin" />
                Uploading...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <Upload size={20} />
                Upload & Process {files.length} {files.length === 1 ? 'File' : 'Files'}
              </span>
            )}
          </button>
        </motion.div>
      )}
    </div>
  );
}
