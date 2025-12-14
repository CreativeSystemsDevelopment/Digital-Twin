import { motion, type HTMLMotionProps } from 'framer-motion';
import { forwardRef } from 'react';
import { cn } from '../../lib/utils';

interface CardProps extends HTMLMotionProps<'div'> {
  variant?: 'raised' | 'inset' | 'flat';
  hover?: boolean;
}

const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = 'raised', hover = true, children, ...props }, ref) => {
    const variants = {
      raised: 'neo-raised',
      inset: 'neo-inset',
      flat: 'neo-flat',
    };

    return (
      <motion.div
        ref={ref}
        className={cn(
          'p-6',
          variants[variant],
          className
        )}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        {...props}
      >
        {children}
      </motion.div>
    );
  }
);

Card.displayName = 'Card';

export { Card };
