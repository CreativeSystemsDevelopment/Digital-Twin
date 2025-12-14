import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Search, 
  FileText, 
  Download, 
  Eye, 
  Filter,
  Calendar,
  Folder,
  File
} from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

interface Document {
  id: string;
  name: string;
  machine: string;
  category: string;
  size: string;
  uploadDate: string;
  status: 'processed' | 'pending' | 'error';
}

export default function Library() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedMachine, setSelectedMachine] = useState('all');

  const categories = [
    'All Categories',
    'Schematic',
    'Manual Contents',
    'Electrical Construction',
    'Parts List',
    'Cable List',
    'Error List',
  ];

  const machines = ['All Machines', 'UH1650', 'UH2000', 'UH2500'];

  const documents: Document[] = [
    {
      id: '1',
      name: 'SCHEMATIC_DIAGRAM_151-E8810-202-0.pdf',
      machine: 'UH1650',
      category: 'Schematic',
      size: '15.2 MB',
      uploadDate: '2024-12-10',
      status: 'processed',
    },
    {
      id: '2',
      name: 'ELECTRICAL_CONSTRUCTION_DRAWINGS.pdf',
      machine: 'UH1650',
      category: 'Electrical Construction',
      size: '8.7 MB',
      uploadDate: '2024-12-09',
      status: 'processed',
    },
    {
      id: '3',
      name: 'PARTS_LIST_ELECTRICAL.pdf',
      machine: 'UH2000',
      category: 'Parts List',
      size: '2.3 MB',
      uploadDate: '2024-12-08',
      status: 'processed',
    },
    {
      id: '4',
      name: 'CABLE_LIST_COMPLETE.pdf',
      machine: 'UH2500',
      category: 'Cable List',
      size: '5.1 MB',
      uploadDate: '2024-12-07',
      status: 'pending',
    },
    {
      id: '5',
      name: 'MANUAL_CONTENTS_EN.pdf',
      machine: 'UH1650',
      category: 'Manual Contents',
      size: '12.8 MB',
      uploadDate: '2024-12-06',
      status: 'processed',
    },
  ];

  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         doc.machine.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || doc.category === selectedCategory;
    const matchesMachine = selectedMachine === 'all' || doc.machine === selectedMachine;
    return matchesSearch && matchesCategory && matchesMachine;
  });

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold mb-2 gradient-text">
          Document Library
        </h1>
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
          Browse and manage your machine documentation
        </p>
      </motion.div>

      {/* Search and Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <Card variant="raised" className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div className="md:col-span-1">
              <div className="relative">
                <Search 
                  size={18} 
                  className="absolute left-3 top-1/2 transform -translate-y-1/2" 
                  style={{ color: 'var(--text-muted)' }}
                />
                <input
                  type="text"
                  placeholder="Search documents..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="neo-input w-full pl-10"
                />
              </div>
            </div>

            {/* Machine Filter */}
            <div>
              <div className="relative">
                <Folder 
                  size={18} 
                  className="absolute left-3 top-1/2 transform -translate-y-1/2" 
                  style={{ color: 'var(--text-muted)' }}
                />
                <select
                  value={selectedMachine}
                  onChange={(e) => setSelectedMachine(e.target.value)}
                  className="neo-input w-full pl-10"
                >
                  {machines.map(machine => (
                    <option key={machine} value={machine.toLowerCase().replace(' ', '_')}>
                      {machine}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Category Filter */}
            <div>
              <div className="relative">
                <Filter 
                  size={18} 
                  className="absolute left-3 top-1/2 transform -translate-y-1/2" 
                  style={{ color: 'var(--text-muted)' }}
                />
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="neo-input w-full pl-10"
                >
                  {categories.map(category => (
                    <option key={category} value={category.toLowerCase().replace(' ', '_')}>
                      {category}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Results Count */}
          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              Found {filteredDocuments.length} document{filteredDocuments.length !== 1 ? 's' : ''}
            </p>
            <Button variant="secondary" size="sm">
              <Filter size={16} />
              Advanced Filters
            </Button>
          </div>
        </Card>
      </motion.div>

      {/* Documents Grid */}
      <div className="grid grid-cols-1 gap-4">
        {filteredDocuments.map((doc, index) => (
          <motion.div
            key={doc.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 + index * 0.05 }}
          >
            <Card variant="raised" className="p-6 hover:neo-raised transition-all">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4 flex-1 min-w-0">
                  {/* Icon */}
                  <div className="neo-flat p-4 shrink-0">
                    <File size={32} style={{ color: 'var(--accent-primary)' }} />
                  </div>

                  {/* Document Info */}
                  <div className="flex-1 min-w-0">
                    <h3 
                      className="font-semibold text-lg mb-1 truncate" 
                      style={{ color: 'var(--text-primary)' }}
                      title={doc.name}
                    >
                      {doc.name}
                    </h3>
                    <div className="flex items-center gap-4 text-sm" style={{ color: 'var(--text-secondary)' }}>
                      <div className="flex items-center gap-1">
                        <Folder size={14} />
                        <span>{doc.machine}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <FileText size={14} />
                        <span>{doc.category}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar size={14} />
                        <span>{doc.uploadDate}</span>
                      </div>
                    </div>
                    <div className="mt-2">
                      <span 
                        className="text-xs px-3 py-1 rounded-full neo-inset"
                        style={{ 
                          color: doc.status === 'processed' ? 'var(--accent-success)' : 
                                 doc.status === 'pending' ? 'var(--accent-warning)' : 
                                 'var(--accent-error)'
                        }}
                      >
                        {doc.status}
                      </span>
                      <span className="text-xs ml-3" style={{ color: 'var(--text-muted)' }}>
                        {doc.size}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 shrink-0">
                  <button className="neo-button p-3">
                    <Eye size={18} style={{ color: 'var(--text-secondary)' }} />
                  </button>
                  <button className="neo-button p-3">
                    <Download size={18} style={{ color: 'var(--text-secondary)' }} />
                  </button>
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Empty State */}
      {filteredDocuments.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Card variant="inset" className="p-12 text-center">
            <div className="neo-flat w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
              <FileText size={40} style={{ color: 'var(--text-muted)' }} />
            </div>
            <h3 className="text-xl font-semibold mb-2" style={{ color: 'var(--text-secondary)' }}>
              No Documents Found
            </h3>
            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
              Try adjusting your search or filters
            </p>
          </Card>
        </motion.div>
      )}
    </div>
  );
}
