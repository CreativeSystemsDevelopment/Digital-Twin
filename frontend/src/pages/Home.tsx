import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

export default function Home() {
  const navigate = useNavigate();
  const [activeModal, setActiveModal] = useState<'import' | null>(null);
  const [machineId, setMachineId] = useState('');

  const menuItems = [
    { id: 'data', label: 'Data', action: () => console.log('Data clicked') },
    { id: 'library', label: 'Library', action: () => console.log('Library clicked') },
    { id: 'import', label: 'Import', action: () => navigate('/documents') },
  ];

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && machineId.trim()) {
      console.log('Submitting machine:', machineId);
      navigate('/documents');
      setActiveModal(null);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white/90 flex items-center justify-center selection:bg-white/20 font-light overflow-hidden">
      
      {/* Ambient Background Glow */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-white/5 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-white/5 rounded-full blur-[120px]" />
      </div>

      {/* Main Menu */}
      <div className="relative z-10 flex gap-12 items-center">
        {menuItems.map((item) => (
          <motion.button
            key={item.id}
            onClick={item.action}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            className="group relative py-2"
          >
            <span className="text-xl font-thin tracking-[0.2em] text-white/40 group-hover:text-white transition-all duration-500 uppercase group-hover:drop-shadow-[0_0_10px_rgba(255,255,255,0.5)]">
              {item.label}
            </span>
          </motion.button>
        ))}
      </div>

      {/* Import Modal */}
      <AnimatePresence>
        {activeModal === 'import' && (
          <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setActiveModal(null)}
              className="absolute inset-0 bg-black/80 backdrop-blur-sm"
            />

            {/* Modal Content */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, filter: 'blur(10px)' }}
              animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
              exit={{ opacity: 0, scale: 0.95, filter: 'blur(10px)' }}
              className="relative"
            >
              <div className="flex items-baseline gap-4">
                <label 
                  htmlFor="machine-id" 
                  className="text-xl font-thin text-white/60 uppercase tracking-[0.2em] whitespace-nowrap"
                >
                  Machine -
                </label>
                <input
                  id="machine-id"
                  type="text"
                  value={machineId}
                  onChange={(e) => setMachineId(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="enter name"
                  className="bg-transparent border-none outline-none focus:outline-none focus:ring-0 focus:border-none ring-0 text-xl font-thin text-white placeholder-white/20 tracking-wider w-64"
                  autoFocus
                />
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
