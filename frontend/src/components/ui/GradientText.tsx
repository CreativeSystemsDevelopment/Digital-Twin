import { cn } from '../../lib/utils';

interface GradientTextProps {
  children: React.ReactNode;
  className?: string;
  animated?: boolean;
}

export function GradientText({ children, className, animated = true }: GradientTextProps) {
  return (
    <span className={cn(animated && 'gradient-text', className)}>
      {children}
    </span>
  );
}
