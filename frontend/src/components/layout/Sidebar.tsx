import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Home, 
  Upload, 
  Cpu, 
  Library, 
  Settings, 
  Menu, 
  X,
  Zap
} from 'lucide-react';
import { cn } from '../../lib/utils';

const navItems = [
  { path: '/', label: 'Home', icon: Home },
  { path: '/dashboard', label: 'Dashboard', icon: Cpu },
  { path: '/documents', label: 'Import', icon: Upload },
  { path: '/library', label: 'Library', icon: Library },
  { path: '/extraction', label: 'AI Extraction', icon: Cpu },
  { path: '/settings', label: 'Settings', icon: Settings },
];

export function Sidebar() {
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Mobile menu button */}
      <motion.button
        className="lg:hidden fixed top-4 left-4 z-50 neo-raised p-3"
        onClick={() => setIsOpen(!isOpen)}
        whileTap={{ scale: 0.95 }}
      >
        {isOpen ? <X size={24} style={{ color: 'var(--text-primary)' }} /> : <Menu size={24} style={{ color: 'var(--text-primary)' }} />}
      </motion.button>

      {/* Backdrop for mobile */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="lg:hidden fixed inset-0 z-40"
            style={{ background: 'rgba(0, 0, 0, 0.7)', backdropFilter: 'blur(8px)' }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.aside
        className={cn(
          'fixed lg:static inset-y-0 left-0 z-40',
          'w-64 lg:w-56',
          'flex flex-col',
          'transform lg:transform-none transition-transform duration-300',
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
        style={{ background: 'var(--bg-secondary)' }}
      >
        {/* Logo */}
        <div className="h-16 flex items-center px-4 neo-flat mx-3 my-3">
          <Link to="/" className="flex items-center gap-2 w-full" onClick={() => setIsOpen(false)}>
            <div className="neo-inset w-8 h-8 rounded-lg flex items-center justify-center">
              <Zap className="w-4 h-4" style={{ color: 'var(--accent-primary)' }} />
            </div>
            <span className="text-sm font-semibold gradient-text">
              Digital Twin
            </span>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-2 px-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            const Icon = item.icon;
            
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setIsOpen(false)}
                className="block"
              >
                <div
                  className={cn(
                    'relative flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-200',
                    isActive 
                      ? 'neo-inset' 
                      : 'neo-flat hover:neo-raised'
                  )}
                >
                  <Icon 
                    size={18} 
                    style={{ 
                      color: isActive ? 'var(--accent-primary)' : 'var(--text-secondary)' 
                    }} 
                  />
                  <span 
                    className="text-sm font-medium"
                    style={{ 
                      color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)' 
                    }}
                  >
                    {item.label}
                  </span>
                </div>
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="p-3">
          <div className="neo-inset px-3 py-2 flex items-center gap-2">
            <div className="pulse-orb pulse-orb-success" />
            <span className="text-[10px] font-medium uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>
              System Online
            </span>
          </div>
        </div>
      </motion.aside>
    </>
  );
}
