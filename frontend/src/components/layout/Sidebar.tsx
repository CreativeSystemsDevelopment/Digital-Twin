import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Home, 
  Upload, 
  Cpu, 
  FileText, 
  Settings, 
  Menu, 
  X,
  Zap
} from 'lucide-react';
import { cn } from '../../lib/utils';

const navItems = [
  { path: '/', label: 'Dashboard', icon: Home },
  { path: '/upload', label: 'Import', icon: Upload },
  { path: '/extraction', label: 'AI Extraction', icon: Cpu },
  { path: '/documents', label: 'Documents', icon: FileText },
  { path: '/settings', label: 'Settings', icon: Settings },
];

export function Sidebar() {
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Mobile menu button */}
      <motion.button
        className="lg:hidden fixed top-4 left-4 z-50 p-3 rounded-xl bg-[var(--bg-card)] border border-white/10"
        onClick={() => setIsOpen(!isOpen)}
        whileTap={{ scale: 0.95 }}
      >
        {isOpen ? <X size={24} /> : <Menu size={24} />}
      </motion.button>

      {/* Backdrop for mobile */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
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
          'w-64 lg:w-48', // Reduced width
          'bg-[var(--bg-secondary)] border-r border-white/5',
          'flex flex-col',
          'transform lg:transform-none transition-transform duration-300',
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        {/* Logo */}
        <div className="h-14 flex items-center px-4 border-b border-white/5">
          <Link to="/" className="flex items-center gap-2" onClick={() => setIsOpen(false)}>
            <div className="w-6 h-6 rounded bg-cyan-900/50 flex items-center justify-center border border-cyan-500/20">
              <Zap className="w-3 h-3 text-cyan-400" />
            </div>
            <span className="text-sm font-medium tracking-tight text-white/90">
              Digital Twin
            </span>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-2 px-2 space-y-0.5 overflow-y-auto">
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
                    'relative flex items-center gap-3 px-3 py-2 rounded-md transition-all duration-200',
                    isActive 
                      ? 'bg-white/5 text-cyan-400' 
                      : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-white/5'
                  )}
                >
                  {isActive && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute left-0 w-0.5 h-full bg-cyan-500 rounded-full"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                    />
                  )}
                  <Icon size={16} className={cn("transition-colors", isActive ? "text-cyan-400" : "text-white/40")} />
                  <span className="text-xs font-medium">{item.label}</span>
                </div>
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="p-3 border-t border-white/5">
          <div className="flex items-center gap-2 px-2 py-1.5 rounded-md bg-white/5 border border-white/5">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[10px] font-medium text-[var(--text-muted)] uppercase tracking-wider">System Online</span>
          </div>
        </div>
      </motion.aside>
    </>
  );
}
