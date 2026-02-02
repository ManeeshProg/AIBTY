// Midnight Oracle Theme
// Deep, mystical palette with warm accents

export const theme = {
  // Core backgrounds - midnight depth
  midnight: '#0A0E1A',
  deepNavy: '#0F1629',
  cardDark: '#151B2E',
  cardLight: '#1A2238',

  // Primary accent - ethereal indigo
  indigo: '#6366F1',
  indigoLight: '#818CF8',
  indigoMuted: '#4F46E5',
  indigoGlow: 'rgba(99, 102, 241, 0.3)',

  // Verdict colors
  verdictBetter: '#10B981', // Emerald success
  verdictBetterGlow: 'rgba(16, 185, 129, 0.25)',
  verdictSame: '#F59E0B', // Amber neutral
  verdictSameGlow: 'rgba(245, 158, 11, 0.25)',
  verdictWorse: '#EF4444', // Soft coral warning
  verdictWorseGlow: 'rgba(239, 68, 68, 0.25)',

  // Streak fire gradient
  streakFlame: '#FF6B35',
  streakEmber: '#F7931A',
  streakGold: '#FFD700',

  // Text hierarchy
  textPrimary: '#FFFFFF',
  textSecondary: '#94A3B8',
  textMuted: '#64748B',
  textDim: '#475569',

  // Accents
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',

  // Borders and dividers
  border: 'rgba(148, 163, 184, 0.1)',
  borderLight: 'rgba(148, 163, 184, 0.2)',

  // Overlay
  overlay: 'rgba(10, 14, 26, 0.8)',
};

const tintColorLight = '#6366F1';
const tintColorDark = '#818CF8';

export default {
  light: {
    text: '#1E293B',
    background: '#F8FAFC',
    tint: tintColorLight,
    tabIconDefault: '#94A3B8',
    tabIconSelected: tintColorLight,
  },
  dark: {
    text: '#FFFFFF',
    background: '#0A0E1A',
    tint: tintColorDark,
    tabIconDefault: '#64748B',
    tabIconSelected: tintColorDark,
  },
};
