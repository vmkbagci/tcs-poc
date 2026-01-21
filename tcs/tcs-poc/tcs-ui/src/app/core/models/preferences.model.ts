/**
 * User Preferences Models
 * 
 * These interfaces define the structure of user preferences.
 * Currently used by stub PreferencesService, ready for future implementation.
 */

// ============================================================================
// User Preferences
// ============================================================================

export interface UserPreferences {
  theme?: ThemePreference;
  gridPreferences?: GridPreferences;
  defaultFilters?: DefaultFilters;
  notifications?: NotificationPreferences;
}

export type ThemePreference = 'light' | 'dark' | 'auto';

// ============================================================================
// Grid Preferences
// ============================================================================

export interface GridPreferences {
  [gridId: string]: GridColumnPreferences;
}

export interface GridColumnPreferences {
  columnVisibility: Record<string, boolean>;
  columnOrder?: string[];
  columnWidths?: Record<string, number>;
  defaultSort?: {
    column: string;
    direction: 'asc' | 'desc';
  };
}

// ============================================================================
// Default Filters
// ============================================================================

export interface DefaultFilters {
  tradeList?: {
    tradeType?: string;
    book?: string;
    counterparty?: string;
  };
}

// ============================================================================
// Notification Preferences
// ============================================================================

export interface NotificationPreferences {
  enableValidationNotifications?: boolean;
  enableSaveNotifications?: boolean;
  enableErrorNotifications?: boolean;
  notificationDuration?: number; // in milliseconds
}

// ============================================================================
// Preference Keys
// ============================================================================

export enum PreferenceKey {
  THEME = 'theme',
  GRID_PREFERENCES = 'gridPreferences',
  DEFAULT_FILTERS = 'defaultFilters',
  NOTIFICATIONS = 'notifications',
}
