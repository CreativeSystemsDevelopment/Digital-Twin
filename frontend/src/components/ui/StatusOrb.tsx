import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';

interface StatusOrbProps {
  status: 'online' | 'processing' | 'offline' | 'warning';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const statusColors = {
  online: {
    bg: 'bg-cyan-400',
    glow: 'shadow-[0_0_10px_rgba(0,240,255,0.6),0_0_20px_rgba(0,240,255,0.3)]',
  },
  processing: {
    bg: 'bg-purple-500',
    glow: 'shadow-[0_0_10px_rgba(168,85,247,0.6),0_0_20px_rgba(168,85,247,0.3)]',
  },
  offline: {
    bg: 'bg-gray-500',
    glow: '',
  },
  warning: {
    bg: 'bg-amber-500',
    glow: 'shadow-[0_0_10px_rgba(245,158,11,0.6),0_0_20px_rgba(245,158,11,0.3)]',
  },
};

const sizes = {
  sm: 'w-2 h-2',
  md: 'w-3 h-3',
  lg: 'w-4 h-4',
};

export function StatusOrb({ status, size = 'md', className }: StatusOrbProps) {
  const colors = statusColors[status];
  
  return (
    <motion.div
      className={cn(
        'rounded-full',
        sizes[size],
        colors.bg,
        colors.glow,
        className
      )}
      animate={status !== 'offline' ? {
        scale: [1, 1.2, 1],
        opacity: [1, 0.8, 1],
      } : undefined}
      transition={{
        duration: 2,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
    />
  );
}
