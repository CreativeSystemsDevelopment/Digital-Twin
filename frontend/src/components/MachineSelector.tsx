import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Plus, Search, Check } from 'lucide-react';

interface Machine {
  id: string;
  label: string;
  documentCount?: number;
}

interface MachineSelectorProps {
  value: string;
  onChange: (machineId: string) => void;
}

export default function MachineSelector({ value, onChange }: MachineSelectorProps) {
  const [machines, setMachines] = useState<Machine[]>([
    { id: 'UH1650', label: 'UH1650', documentCount: 12 },
    { id: 'UH2000', label: 'UH2000', documentCount: 8 },
    { id: 'UH2500', label: 'UH2500', documentCount: 15 },
  ]);
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [newMachineName, setNewMachineName] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setIsCreating(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const filteredMachines = machines.filter(m =>
    m.label.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const selectedMachine = machines.find(m => m.id === value);

  const handleSelect = (machineId: string) => {
    onChange(machineId);
    setIsOpen(false);
    setSearchQuery('');
  };

  const handleCreateMachine = () => {
    if (!newMachineName.trim()) return;
    
    const newMachine: Machine = {
      id: newMachineName.trim(),
      label: newMachineName.trim(),
      documentCount: 0,
    };
    
    setMachines(prev => [...prev, newMachine]);
    onChange(newMachine.id);
    setNewMachineName('');
    setIsCreating(false);
    setIsOpen(false);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <label className="block text-sm font-semibold mb-3" style={{ color: 'var(--text-secondary)' }}>
          Machine / Production Line
        </label>
        
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="neo-flat w-full px-5 py-4 flex items-center justify-between"
        >
          <div className="flex items-center gap-3">
            <div className="neo-inset w-10 h-10 rounded-full flex items-center justify-center">
              <span className="text-sm font-bold gradient-text">
                {selectedMachine ? selectedMachine.label.substring(0, 2).toUpperCase() : '?'}
              </span>
            </div>
            <div className="text-left">
              <p className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                {selectedMachine ? selectedMachine.label : 'Select a machine'}
              </p>
              {selectedMachine && selectedMachine.documentCount !== undefined && (
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  {selectedMachine.documentCount} documents
                </p>
              )}
            </div>
          </div>
          
          <motion.div
            animate={{ rotate: isOpen ? 180 : 0 }}
            transition={{ duration: 0.3 }}
          >
            <ChevronDown size={20} style={{ color: 'var(--text-secondary)' }} />
          </motion.div>
        </button>
      </motion.div>

      {/* Dropdown Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="absolute top-full left-0 right-0 mt-2 neo-raised p-4 z-50"
            style={{ maxHeight: '400px', overflowY: 'auto' }}
          >
            {/* Search */}
            <div className="mb-3">
              <div className="relative">
                <Search 
                  size={16} 
                  className="absolute left-3 top-1/2 transform -translate-y-1/2" 
                  style={{ color: 'var(--text-muted)' }}
                />
                <input
                  type="text"
                  placeholder="Search machines..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="neo-input w-full pl-10 text-sm"
                  autoFocus
                />
              </div>
            </div>

            {/* Machine List */}
            <div className="space-y-2 mb-3">
              {filteredMachines.length > 0 ? (
                filteredMachines.map((machine, index) => (
                  <motion.button
                    key={machine.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    onClick={() => handleSelect(machine.id)}
                    className={`w-full px-4 py-3 rounded-lg text-left transition-all ${
                      value === machine.id ? 'neo-inset' : 'neo-flat'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="neo-inset w-8 h-8 rounded-full flex items-center justify-center">
                          <span className="text-xs font-bold gradient-text">
                            {machine.label.substring(0, 2).toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <p className="font-medium text-sm" style={{ color: 'var(--text-primary)' }}>
                            {machine.label}
                          </p>
                          {machine.documentCount !== undefined && (
                            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                              {machine.documentCount} documents
                            </p>
                          )}
                        </div>
                      </div>
                      
                      {value === machine.id && (
                        <Check size={16} style={{ color: 'var(--accent-success)' }} />
                      )}
                    </div>
                  </motion.button>
                ))
              ) : (
                <p className="text-sm text-center py-4" style={{ color: 'var(--text-muted)' }}>
                  No machines found
                </p>
              )}
            </div>

            {/* Create New Machine */}
            {!isCreating ? (
              <button
                onClick={() => setIsCreating(true)}
                className="neo-button w-full flex items-center justify-center gap-2 py-3"
              >
                <Plus size={16} />
                <span className="text-sm font-medium">Create New Machine</span>
              </button>
            ) : (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="space-y-2"
              >
                <input
                  type="text"
                  placeholder="Enter machine name..."
                  value={newMachineName}
                  onChange={(e) => setNewMachineName(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleCreateMachine();
                    if (e.key === 'Escape') setIsCreating(false);
                  }}
                  className="neo-input w-full text-sm"
                  autoFocus
                />
                <div className="flex gap-2">
                  <button
                    onClick={handleCreateMachine}
                    className="neo-button-primary flex-1 py-2 text-sm"
                    disabled={!newMachineName.trim()}
                  >
                    Create
                  </button>
                  <button
                    onClick={() => {
                      setIsCreating(false);
                      setNewMachineName('');
                    }}
                    className="neo-button flex-1 py-2 text-sm"
                  >
                    Cancel
                  </button>
                </div>
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
