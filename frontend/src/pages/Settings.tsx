import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Settings as SettingsIcon, 
  Key, 
  Database, 
  Palette,
  Bell,
  Save,
  RefreshCw
} from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { StatusOrb } from '../components/ui/StatusOrb';

export default function Settings() {
  const [apiKey, setApiKey] = useState('sk-••••••••••••••••');
  const [storageLimit, setStorageLimit] = useState('100');
  const [notifications, setNotifications] = useState(true);

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
            <SettingsIcon size={32} style={{ color: 'var(--accent-primary)' }} />
          </div>
          <div>
            <h1 className="text-3xl font-bold gradient-text">
              Settings
            </h1>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              Configure your Digital Twin system
            </p>
          </div>
        </div>
      </motion.div>

      {/* API Configuration */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <Card variant="raised" className="p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="neo-flat p-3 rounded-lg">
              <Key size={24} style={{ color: 'var(--accent-primary)' }} />
            </div>
            <div>
              <h2 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
                API Configuration
              </h2>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                Manage API keys and external services
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold mb-2" style={{ color: 'var(--text-secondary)' }}>
                Gemini API Key
              </label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="neo-input w-full"
                placeholder="Enter your Gemini API key"
              />
              <p className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>
                Required for AI extraction features. Get your key from Google AI Studio.
              </p>
            </div>

            <div className="neo-inset p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
                    API Status
                  </p>
                  <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                    Connected to gemini-2.5-flash-001
                  </p>
                </div>
                <StatusOrb status="online" label="Active" />
              </div>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Storage Configuration */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <Card variant="raised" className="p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="neo-flat p-3 rounded-lg">
              <Database size={24} style={{ color: 'var(--accent-success)' }} />
            </div>
            <div>
              <h2 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
                Storage Settings
              </h2>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                Manage document storage and data retention
              </p>
            </div>
          </div>

          <div className="space-y-6">
            <div>
              <label className="block text-sm font-semibold mb-2" style={{ color: 'var(--text-secondary)' }}>
                Storage Limit (GB)
              </label>
              <input
                type="number"
                value={storageLimit}
                onChange={(e) => setStorageLimit(e.target.value)}
                className="neo-input w-full"
                min="10"
                max="1000"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="neo-flat p-4">
                <p className="text-sm font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>
                  Current Usage
                </p>
                <p className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>
                  12.3 GB
                </p>
                <div className="neo-progress">
                  <div className="neo-progress-fill" style={{ width: '12.3%' }} />
                </div>
                <p className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>
                  12.3% of {storageLimit} GB used
                </p>
              </div>

              <div className="neo-flat p-4">
                <p className="text-sm font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>
                  Documents Stored
                </p>
                <p className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>
                  35
                </p>
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  Across 3 machines
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <Button variant="secondary" size="sm">
                <RefreshCw size={16} />
                Clear Cache
              </Button>
              <Button variant="secondary" size="sm">
                <Database size={16} />
                Optimize Storage
              </Button>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Appearance */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <Card variant="raised" className="p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="neo-flat p-3 rounded-lg">
              <Palette size={24} style={{ color: 'var(--accent-warning)' }} />
            </div>
            <div>
              <h2 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
                Appearance
              </h2>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                Customize the interface appearance
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="neo-flat p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>
                    Theme
                  </p>
                  <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                    Dark neomorphic theme active
                  </p>
                </div>
                <div className="flex gap-2">
                  <button className="neo-inset w-10 h-10 rounded-lg" title="Dark Theme">
                    <div className="w-full h-full rounded-lg" style={{ background: 'var(--neo-bg)' }} />
                  </button>
                </div>
              </div>
            </div>

            <div className="neo-flat p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>
                    Accent Color
                  </p>
                  <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                    Primary accent color for highlights
                  </p>
                </div>
                <div className="flex gap-2">
                  <button className="neo-inset w-10 h-10 rounded-lg overflow-hidden">
                    <div className="w-full h-full" style={{ background: 'var(--accent-primary)' }} />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Notifications */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        <Card variant="raised" className="p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="neo-flat p-3 rounded-lg">
              <Bell size={24} style={{ color: 'var(--accent-error)' }} />
            </div>
            <div>
              <h2 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
                Notifications
              </h2>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                Manage system notifications and alerts
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="neo-flat p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>
                    Enable Notifications
                  </p>
                  <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                    Receive alerts about uploads and extractions
                  </p>
                </div>
                <label className="relative inline-block w-12 h-6">
                  <input
                    type="checkbox"
                    checked={notifications}
                    onChange={(e) => setNotifications(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className={`w-12 h-6 rounded-full transition-all ${notifications ? 'neo-button-primary' : 'neo-inset'}`}>
                    <div className={`absolute top-1 left-1 w-4 h-4 rounded-full transition-transform ${notifications ? 'translate-x-6 bg-white' : 'translate-x-0 neo-raised'}`} />
                  </div>
                </label>
              </div>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Save Button */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        className="flex justify-center pt-4"
      >
        <Button variant="primary" size="lg">
          <Save size={20} />
          Save Settings
        </Button>
      </motion.div>
    </div>
  );
}
