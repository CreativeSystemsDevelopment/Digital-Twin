import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FileStack, Database, Library, Zap } from 'lucide-react';

export default function Home() {
  const navigate = useNavigate();
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);

  const menuItems = [
    { 
      id: 'data', 
      label: 'Dashboard', 
      icon: Database,
      description: 'View system overview',
      action: () => navigate('/dashboard') 
    },
    { 
      id: 'library', 
      label: 'Library', 
      icon: Library,
      description: 'Browse documents',
      action: () => navigate('/library') 
    },
    { 
      id: 'import', 
      label: 'Import', 
      icon: FileStack,
      description: 'Upload documents',
      action: () => navigate('/documents') 
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-animated p-6 md:p-12 flex items-center justify-center overflow-hidden">
      
      {/* Logo Header */}
      <motion.div
        initial={{ opacity: 0, y: -40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="absolute top-12 left-1/2 transform -translate-x-1/2 flex items-center gap-3"
      >
        <div className="neo-raised p-4">
          <Zap size={32} style={{ color: 'var(--accent-primary)' }} />
        </div>
        <h1 className="text-3xl font-bold gradient-text">
          Digital Twin
        </h1>
      </motion.div>

      {/* Main Menu */}
      <div className="relative z-10 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl w-full">
        {menuItems.map((item, index) => {
          const Icon = item.icon;
          return (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 + index * 0.1 }}
              onMouseEnter={() => setHoveredItem(item.id)}
              onMouseLeave={() => setHoveredItem(null)}
            >
              <button
                onClick={item.action}
                className="neo-raised w-full h-64 p-8 flex flex-col items-center justify-center text-center group"
              >
                <motion.div
                  animate={hoveredItem === item.id ? { scale: 1.1, rotate: 5 } : { scale: 1, rotate: 0 }}
                  transition={{ duration: 0.3 }}
                  className="neo-flat p-6 rounded-full mb-6"
                >
                  <Icon size={48} style={{ color: 'var(--accent-primary)' }} />
                </motion.div>
                
                <h2 
                  className="text-2xl font-bold mb-3" 
                  style={{ color: 'var(--text-primary)' }}
                >
                  {item.label}
                </h2>
                
                <p 
                  className="text-sm" 
                  style={{ color: 'var(--text-secondary)' }}
                >
                  {item.description}
                </p>

                {hoveredItem === item.id && (
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: '60%' }}
                    transition={{ duration: 0.3 }}
                    className="h-1 rounded-full mt-6"
                    style={{ background: 'var(--gradient-accent)' }}
                  />
                )}
              </button>
            </motion.div>
          );
        })}
      </div>

      {/* Footer */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 1 }}
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
      >
        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
          Document Processing & AI Extraction System
        </p>
      </motion.div>
    </div>
  );
}
