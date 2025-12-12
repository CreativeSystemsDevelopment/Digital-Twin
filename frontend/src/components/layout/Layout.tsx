import { Outlet } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Sidebar } from './Sidebar';

export function Layout() {
  return (
    <div className="flex min-h-screen bg-[#0a0a0a] text-white/90 font-sans selection:bg-cyan-500/30">
      <Sidebar />
      
      <main className="flex-1 relative overflow-hidden">
        <div className="h-full overflow-y-auto p-4 lg:p-6 pt-20 lg:pt-6">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
            className="max-w-6xl mx-auto"
          >
            <Outlet />
          </motion.div>
        </div>
      </main>
    </div>
  );
}
