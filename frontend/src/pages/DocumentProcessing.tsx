import { useState } from 'react';
import { motion } from 'framer-motion';
import MachineSelector from '../components/MachineSelector';
import DocumentUpload from '../components/DocumentUpload';
import { FileStack, Sparkles } from 'lucide-react';

export default function DocumentProcessing() {
  const [selectedMachine, setSelectedMachine] = useState('');

  return (
    <div className="min-h-screen bg-gradient-animated p-6 md:p-12">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="neo-raised p-4">
              <FileStack size={32} style={{ color: 'var(--accent-primary)' }} />
            </div>
            <h1 className="text-4xl md:text-5xl font-bold gradient-text">
              Digital Twin
            </h1>
          </div>
          <p className="text-lg" style={{ color: 'var(--text-secondary)' }}>
            Document Processing & Management System
          </p>
          <div className="flex items-center justify-center gap-2 mt-3">
            <Sparkles size={16} style={{ color: 'var(--accent-primary)' }} />
            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
              Upload, categorize, and process machine documentation with AI
            </p>
          </div>
        </motion.div>

        {/* Main Content */}
        <div className="space-y-8">
          {/* Machine Selection Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="neo-raised p-8"
          >
            <MachineSelector 
              value={selectedMachine} 
              onChange={setSelectedMachine} 
            />
          </motion.div>

          {/* Upload Section */}
          {selectedMachine && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="neo-raised p-8"
            >
              <div className="mb-6">
                <h2 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>
                  Upload Documents
                </h2>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                  Upload documentation for <span className="font-semibold gradient-text">{selectedMachine}</span>
                </p>
              </div>
              
              <DocumentUpload 
                machineId={selectedMachine}
                onUploadComplete={() => {
                  console.log('Upload complete for', selectedMachine);
                }}
              />
            </motion.div>
          )}

          {/* Empty State */}
          {!selectedMachine && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="neo-inset p-12 text-center"
            >
              <div className="neo-flat w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                <FileStack size={40} style={{ color: 'var(--text-muted)' }} />
              </div>
              <h3 className="text-xl font-semibold mb-2" style={{ color: 'var(--text-secondary)' }}>
                Select a Machine to Begin
              </h3>
              <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                Choose a machine or production line from the dropdown above to start uploading documents
              </p>
            </motion.div>
          )}
        </div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.8 }}
          className="mt-12 text-center"
        >
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
            Powered by AI • Secure Document Processing • Real-time Analysis
          </p>
        </motion.div>
      </div>
    </div>
  );
}
