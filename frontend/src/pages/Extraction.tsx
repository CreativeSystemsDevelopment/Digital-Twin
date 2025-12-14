import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Cpu, 
  Play, 
  FileText, 
  Zap,
  CheckCircle2,
  Loader2,
  AlertCircle,
  Clock,
  TrendingUp,
  Database
} from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { StatusOrb } from '../components/ui/StatusOrb';

export default function Extraction() {
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractionResults, setExtractionResults] = useState<any>(null);
  const [selectedDocument, setSelectedDocument] = useState<string>('');

  const documents = [
    { id: '1', name: 'SCHEMATIC_DIAGRAM_151-E8810-202-0.pdf', machine: 'UH1650', pages: 129 },
    { id: '2', name: 'ELECTRICAL_CONSTRUCTION_DRAWINGS.pdf', machine: 'UH1650', pages: 45 },
    { id: '3', name: 'PARTS_LIST_ELECTRICAL.pdf', machine: 'UH2000', pages: 23 },
  ];

  const handleStartExtraction = async () => {
    if (!selectedDocument) return;
    
    setIsExtracting(true);
    
    // Simulate extraction process
    setTimeout(() => {
      setExtractionResults({
        pagesProcessed: 2,
        totalPages: 129,
        componentsExtracted: 247,
        wiresExtracted: 189,
        crossRefsExtracted: 56,
        processingTime: '12.3s',
        tokensUsed: 33421,
        cacheHits: 98,
      });
      setIsExtracting(false);
    }, 3000);
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center gap-3 mb-3">
          <div className="neo-raised p-4">
            <Cpu size={32} style={{ color: 'var(--accent-primary)' }} />
          </div>
          <div>
            <h1 className="text-3xl font-bold gradient-text">
              AI Extraction
            </h1>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              Extract structured data from technical documents using Gemini AI
            </p>
          </div>
        </div>
      </motion.div>

      {/* Extraction Setup */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <Card variant="raised" className="p-8">
          <h2 className="text-xl font-bold mb-6" style={{ color: 'var(--text-primary)' }}>
            Configure Extraction
          </h2>

          <div className="space-y-6">
            {/* Document Selection */}
            <div>
              <label className="block text-sm font-semibold mb-3" style={{ color: 'var(--text-secondary)' }}>
                Select Document
              </label>
              <select
                value={selectedDocument}
                onChange={(e) => setSelectedDocument(e.target.value)}
                className="neo-input w-full"
                disabled={isExtracting}
              >
                <option value="">Choose a document...</option>
                {documents.map(doc => (
                  <option key={doc.id} value={doc.id}>
                    {doc.name} ({doc.machine}) - {doc.pages} pages
                  </option>
                ))}
              </select>
            </div>

            {/* Extraction Options */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="neo-flat p-4">
                <div className="flex items-center gap-2 mb-2">
                  <input
                    type="checkbox"
                    id="extract-components"
                    defaultChecked
                    className="neo-input"
                    disabled={isExtracting}
                  />
                  <label 
                    htmlFor="extract-components" 
                    className="text-sm font-medium cursor-pointer"
                    style={{ color: 'var(--text-primary)' }}
                  >
                    Components
                  </label>
                </div>
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  Extract component symbols and labels
                </p>
              </div>

              <div className="neo-flat p-4">
                <div className="flex items-center gap-2 mb-2">
                  <input
                    type="checkbox"
                    id="extract-wires"
                    defaultChecked
                    className="neo-input"
                    disabled={isExtracting}
                  />
                  <label 
                    htmlFor="extract-wires" 
                    className="text-sm font-medium cursor-pointer"
                    style={{ color: 'var(--text-primary)' }}
                  >
                    Wiring
                  </label>
                </div>
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  Extract wire connections and labels
                </p>
              </div>

              <div className="neo-flat p-4">
                <div className="flex items-center gap-2 mb-2">
                  <input
                    type="checkbox"
                    id="extract-refs"
                    defaultChecked
                    className="neo-input"
                    disabled={isExtracting}
                  />
                  <label 
                    htmlFor="extract-refs" 
                    className="text-sm font-medium cursor-pointer"
                    style={{ color: 'var(--text-primary)' }}
                  >
                    Cross References
                  </label>
                </div>
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  Extract cross-reference markers
                </p>
              </div>
            </div>

            {/* Model Info */}
            <div className="neo-inset p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>
                    AI Model: gemini-2.5-flash-001
                  </p>
                  <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                    Context caching enabled • Structured output mode
                  </p>
                </div>
                <StatusOrb status="online" />
              </div>
            </div>

            {/* Action Button */}
            <div className="flex justify-center pt-4">
              <Button
                variant="primary"
                size="lg"
                onClick={handleStartExtraction}
                disabled={!selectedDocument || isExtracting}
                isLoading={isExtracting}
              >
                {isExtracting ? (
                  <>
                    <Loader2 size={20} className="animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Play size={20} />
                    Start Extraction
                  </>
                )}
              </Button>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Extraction Progress/Results */}
      <AnimatePresence>
        {(isExtracting || extractionResults) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
          >
            <Card variant="raised" className="p-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="neo-flat p-3 rounded-lg">
                  <Zap size={24} style={{ color: 'var(--accent-warning)' }} />
                </div>
                <div>
                  <h2 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
                    {isExtracting ? 'Extraction in Progress' : 'Extraction Complete'}
                  </h2>
                  <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                    {isExtracting ? 'Processing document with Gemini AI...' : 'Sample extraction completed successfully'}
                  </p>
                </div>
              </div>

              {isExtracting ? (
                <div className="space-y-4">
                  <div className="neo-inset p-6 text-center">
                    <Loader2 size={48} className="animate-spin mx-auto mb-4" style={{ color: 'var(--accent-primary)' }} />
                    <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                      Analyzing schematic pages...
                    </p>
                  </div>
                </div>
              ) : extractionResults && (
                <div className="space-y-6">
                  {/* Stats Grid */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="neo-flat p-4 text-center">
                      <FileText size={24} className="mx-auto mb-2" style={{ color: 'var(--accent-primary)' }} />
                      <p className="text-2xl font-bold mb-1" style={{ color: 'var(--text-primary)' }}>
                        {extractionResults.pagesProcessed}
                      </p>
                      <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                        Pages Processed
                      </p>
                    </div>

                    <div className="neo-flat p-4 text-center">
                      <Database size={24} className="mx-auto mb-2" style={{ color: 'var(--accent-success)' }} />
                      <p className="text-2xl font-bold mb-1" style={{ color: 'var(--text-primary)' }}>
                        {extractionResults.componentsExtracted}
                      </p>
                      <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                        Components
                      </p>
                    </div>

                    <div className="neo-flat p-4 text-center">
                      <TrendingUp size={24} className="mx-auto mb-2" style={{ color: 'var(--accent-warning)' }} />
                      <p className="text-2xl font-bold mb-1" style={{ color: 'var(--text-primary)' }}>
                        {extractionResults.wiresExtracted}
                      </p>
                      <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                        Wire Connections
                      </p>
                    </div>

                    <div className="neo-flat p-4 text-center">
                      <Clock size={24} className="mx-auto mb-2" style={{ color: 'var(--accent-error)' }} />
                      <p className="text-2xl font-bold mb-1" style={{ color: 'var(--text-primary)' }}>
                        {extractionResults.processingTime}
                      </p>
                      <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                        Processing Time
                      </p>
                    </div>
                  </div>

                  {/* Details */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="neo-inset p-4">
                      <p className="text-sm font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
                        Extraction Details
                      </p>
                      <div className="space-y-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
                        <div className="flex justify-between">
                          <span>Cross References:</span>
                          <span className="font-semibold">{extractionResults.crossRefsExtracted}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Total Pages:</span>
                          <span className="font-semibold">{extractionResults.totalPages}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Cache Hits:</span>
                          <span className="font-semibold">{extractionResults.cacheHits}%</span>
                        </div>
                      </div>
                    </div>

                    <div className="neo-inset p-4">
                      <p className="text-sm font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
                        API Usage
                      </p>
                      <div className="space-y-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
                        <div className="flex justify-between">
                          <span>Tokens Used:</span>
                          <span className="font-semibold">{extractionResults.tokensUsed.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Model:</span>
                          <span className="font-semibold">gemini-2.5-flash</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Status:</span>
                          <span className="flex items-center gap-1">
                            <CheckCircle2 size={14} style={{ color: 'var(--accent-success)' }} />
                            <span className="font-semibold">Success</span>
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-4 justify-center">
                    <Button variant="primary" size="md">
                      <FileText size={18} />
                      View Full Results
                    </Button>
                    <Button variant="secondary" size="md">
                      <Play size={18} />
                      Process Full Document
                    </Button>
                  </div>
                </div>
              )}
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Info Panel */}
      {!isExtracting && !extractionResults && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <Card variant="inset" className="p-6">
            <div className="flex items-start gap-4">
              <AlertCircle size={24} style={{ color: 'var(--accent-primary)' }} />
              <div>
                <h3 className="text-sm font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
                  About AI Extraction
                </h3>
                <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                  This feature uses Google's Gemini AI to analyze technical schematics and extract structured data. 
                  The system identifies components, wire connections, cross-references, and other technical elements 
                  from your documents. Context caching ensures fast, efficient processing for repeated operations.
                </p>
              </div>
            </div>
          </Card>
        </motion.div>
      )}
    </div>
  );
}
