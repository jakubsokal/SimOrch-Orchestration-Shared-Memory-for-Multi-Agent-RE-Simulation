import { type FC, useEffect } from 'react';
import { CheckCircle, XCircle, Info, AlertTriangle, X } from 'lucide-react';

type PopUpType = 'success' | 'error' | 'info' | 'warning';

export interface PopUpItem {
  id: string;
  type: PopUpType;
  message: string;
  description?: string;
  duration?: number;
}

interface PopUpProps {
  popUps: PopUpItem[];
  onClose: (id: string) => void;
}

const STYLES: Record<PopUpType, { container: string; icon: string; Icon: FC<{ size?: number }> }> = {
  success: { container: 'border-green-200 bg-green-50', icon: 'text-green-600', Icon: ({ size }) => <CheckCircle size={size} /> },
  error: { container: 'border-red-200 bg-red-50', icon: 'text-red-600', Icon: ({ size }) => <XCircle size={size} /> },
  info: { container: 'border-blue-200 bg-blue-50', icon: 'text-blue-600', Icon: ({ size }) => <Info size={size} /> },
  warning: { container: 'border-yellow-200 bg-yellow-50', icon: 'text-yellow-600', Icon: ({ size }) => <AlertTriangle size={size} /> },
};

const PopUp: FC<PopUpProps> = ({ popUps, onClose }) => {
  if (popUps.length === 0) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2 items-end">
      {popUps.map(({ id, type, message, description, duration = 10000 }) => {
        const { container, icon, Icon } = STYLES[type];

        return (
          <PopUpEntry
            key={id}
            id={id}
            container={container}
            icon={icon}
            Icon={Icon}
            message={message}
            description={description}
            duration={duration}
            onClose={() => onClose(id)}
          />
        );
      })}
    </div>
  );
};

const PopUpEntry: FC<{
  id: string;
  container: string;
  icon: string;
  Icon: FC<{ size?: number }>;
  message: string;
  description?: string;
  duration: number;
  onClose: () => void;
}> = ({ container, icon, Icon, message, description, duration, onClose }) => {
  useEffect(() => {
    if (duration === 0) return;
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [duration, onClose]);

  return (
    <div className={`flex items-start gap-3 px-4 py-3 rounded-lg border shadow-sm w-full max-w-sm ${container}`}>
      <span className={`mt-0.5 shrink-0 ${icon}`}>
        <Icon size={16} />
      </span>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-gray-900">{message}</p>
        {description && <p className="text-xs text-gray-500 mt-0.5">{description}</p>}
      </div>
      <button onClick={onClose} className="shrink-0 text-gray-400 hover:text-gray-600 transition-colors mt-0.5">
        <X size={14} />
      </button>
    </div>
  );
};

export default PopUp;