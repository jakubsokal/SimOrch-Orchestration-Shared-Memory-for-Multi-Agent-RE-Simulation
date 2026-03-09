import { type FC } from 'react';
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

interface LoadingProps {
  size?: number;
  thickness?: number;
  label?: string;
  direction?: 'row' | 'column';
  gap?: number;
}

const Loading: FC<LoadingProps> = ({
  size = 32,
  thickness = 4,
  label,
  direction = 'row',
  gap = 1,
}) => {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', flexDirection: direction, gap }}>
      <CircularProgress size={size} thickness={thickness} />
      {label ? (
        <Typography variant="body2" color="text.secondary">
          {label}
        </Typography>
      ) : null}
    </Box>
  );
};

export default Loading;