import { cn } from '../../lib/utils';

interface StatusOrbProps {
  status: 'online' | 'processing' | 'offline' | 'warning' | 'success' | 'error';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  label?: string;
}

const sizes = {
  sm: 'w-2 h-2',
  md: 'w-3 h-3',
  lg: 'w-4 h-4',
};

export function StatusOrb({ status, size = 'md', className, label }: StatusOrbProps) {
  const orbClass = status === 'online' || status === 'success' ? 'pulse-orb-success' :
                   status === 'processing' ? 'pulse-orb-processing' :
                   status === 'warning' || status === 'error' ? 'pulse-orb-error' :
                   'pulse-orb';
  
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div className={cn('pulse-orb', sizes[size], orbClass)} />
      {label && (
        <span className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>
          {label}
        </span>
      )}
    </div>
  );
}
