export const ML_THRESHOLDS = {
  LOW: 0.3,
  MEDIUM: 0.6,
};

export const getMLRisk = (score) => {
  if (score === null || score === undefined) return { label: 'N/A', color: '#666' };
  if (score < ML_THRESHOLDS.LOW) return { label: 'LOW', color: '#00C851' };
  if (score < ML_THRESHOLDS.MEDIUM) return { label: 'MEDIUM', color: '#ffbb33' };
  return { label: 'HIGH', color: '#ff4444' };
};