import { motion } from 'framer-motion';
import { 
  Activity, 
  FileText, 
  Cpu, 
  TrendingUp, 
  Clock,
  CheckCircle2,
  AlertCircle,
  Database
} from 'lucide-react';
import { StatusOrb } from '../components/ui/StatusOrb';
import { Card } from '../components/ui/Card';

export default function Dashboard() {
  const machines = [
    { id: 'UH1650', name: 'UH1650', documents: 12, status: 'online', lastSync: '2 hours ago' },
    { id: 'UH2000', name: 'UH2000', documents: 8, status: 'online', lastSync: '5 hours ago' },
    { id: 'UH2500', name: 'UH2500', documents: 15, status: 'processing', lastSync: '1 hour ago' },
  ];

  const recentActivity = [
    { id: 1, type: 'upload', machine: 'UH1650', file: 'SCHEMATIC_DIAGRAM.pdf', time: '10 minutes ago', status: 'success' },
    { id: 2, type: 'extraction', machine: 'UH2500', file: 'ELECTRICAL_PARTS.pdf', time: '1 hour ago', status: 'processing' },
    { id: 3, type: 'upload', machine: 'UH2000', file: 'MANUAL_CONTENTS.pdf', time: '3 hours ago', status: 'success' },
    { id: 4, type: 'extraction', machine: 'UH1650', file: 'CABLE_LIST.pdf', time: '5 hours ago', status: 'success' },
  ];

  const stats = [
    { label: 'Total Machines', value: '3', icon: Database, color: 'var(--accent-primary)' },
    { label: 'Total Documents', value: '35', icon: FileText, color: 'var(--accent-success)' },
    { label: 'AI Extractions', value: '127', icon: Cpu, color: 'var(--accent-warning)' },
    { label: 'Processing', value: '2', icon: Activity, color: 'var(--accent-error)' },
  ];

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold mb-2 gradient-text">
          Dashboard
        </h1>
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
          Overview of your Digital Twin system
        </p>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 + index * 0.05 }}
            >
              <Card variant="raised" className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="neo-flat p-3 rounded-lg">
                    <Icon size={24} style={{ color: stat.color }} />
                  </div>
                  <TrendingUp size={16} style={{ color: 'var(--accent-success)' }} />
                </div>
                <div>
                  <p className="text-3xl font-bold mb-1" style={{ color: 'var(--text-primary)' }}>
                    {stat.value}
                  </p>
                  <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                    {stat.label}
                  </p>
                </div>
              </Card>
            </motion.div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Machines */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <Card variant="raised" className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="neo-flat p-3 rounded-lg">
                <Database size={24} style={{ color: 'var(--accent-primary)' }} />
              </div>
              <div>
                <h2 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
                  Machines
                </h2>
                <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                  Connected production lines
                </p>
              </div>
            </div>

            <div className="space-y-3">
              {machines.map((machine, index) => (
                <motion.div
                  key={machine.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 + index * 0.1 }}
                  className="neo-flat p-4 hover:neo-raised transition-all cursor-pointer"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <div className="neo-inset w-10 h-10 rounded-lg flex items-center justify-center">
                        <span className="text-sm font-bold gradient-text">
                          {machine.name.substring(0, 2)}
                        </span>
                      </div>
                      <div>
                        <p className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                          {machine.name}
                        </p>
                        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                          {machine.documents} documents
                        </p>
                      </div>
                    </div>
                    <StatusOrb 
                      status={machine.status === 'online' ? 'online' : 'processing'} 
                      size="sm"
                    />
                  </div>
                  <div className="flex items-center gap-2 text-xs" style={{ color: 'var(--text-muted)' }}>
                    <Clock size={12} />
                    <span>Last sync: {machine.lastSync}</span>
                  </div>
                </motion.div>
              ))}
            </div>
          </Card>
        </motion.div>

        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <Card variant="raised" className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="neo-flat p-3 rounded-lg">
                <Activity size={24} style={{ color: 'var(--accent-success)' }} />
              </div>
              <div>
                <h2 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
                  Recent Activity
                </h2>
                <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                  Latest system events
                </p>
              </div>
            </div>

            <div className="space-y-3">
              {recentActivity.map((activity, index) => (
                <motion.div
                  key={activity.id}
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 + index * 0.1 }}
                  className="neo-flat p-4"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-start gap-3 flex-1 min-w-0">
                      <div className="neo-inset p-2 rounded-lg mt-0.5">
                        {activity.type === 'upload' ? (
                          <FileText size={16} style={{ color: 'var(--accent-primary)' }} />
                        ) : (
                          <Cpu size={16} style={{ color: 'var(--accent-warning)' }} />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-sm truncate" style={{ color: 'var(--text-primary)' }}>
                          {activity.file}
                        </p>
                        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                          {activity.machine} • {activity.time}
                        </p>
                      </div>
                    </div>
                    {activity.status === 'success' ? (
                      <CheckCircle2 size={16} style={{ color: 'var(--accent-success)' }} />
                    ) : (
                      <AlertCircle size={16} style={{ color: 'var(--accent-warning)' }} />
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </Card>
        </motion.div>
      </div>

      {/* System Status */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
      >
        <Card variant="raised" className="p-6">
          <h2 className="text-xl font-bold mb-4" style={{ color: 'var(--text-primary)' }}>
            System Status
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="neo-flat p-4">
              <StatusOrb status="online" label="API Server" />
              <p className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>
                Running on port 8000
              </p>
            </div>
            <div className="neo-flat p-4">
              <StatusOrb status="online" label="Gemini AI" />
              <p className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>
                gemini-2.5-flash-001
              </p>
            </div>
            <div className="neo-flat p-4">
              <StatusOrb status="online" label="Storage" />
              <p className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>
                12.3 GB / 100 GB used
              </p>
            </div>
          </div>
        </Card>
      </motion.div>
    </div>
  );
}
