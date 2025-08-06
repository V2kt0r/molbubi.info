/**
 * Date and timezone utility functions
 */

/**
 * Formats a UTC date string to the user's local timezone
 * @param utcDateString - UTC date string from the API (e.g., "2024-01-15T14:30:00Z")
 * @param options - Intl.DateTimeFormatOptions for formatting
 * @returns Formatted date string in user's local timezone
 */
export function formatLocalDateTime(
  utcDateString: string,
  options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  }
): string {
  try {
    const date = new Date(utcDateString);
    return new Intl.DateTimeFormat('en-US', options).format(date);
  } catch (error) {
    console.warn('Invalid date string:', utcDateString);
    return 'Invalid date';
  }
}

/**
 * Formats a UTC date string to show relative time (e.g., "2 hours ago", "5 minutes ago")
 * @param utcDateString - UTC date string from the API
 * @returns Relative time string
 */
export function formatRelativeTime(utcDateString: string): string {
  try {
    const date = new Date(utcDateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    // If the date is in the future or very recent, show "just now"
    if (diffInSeconds < 60) {
      return 'just now';
    }

    // Minutes
    if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60);
      return `${minutes} minute${minutes === 1 ? '' : 's'} ago`;
    }

    // Hours
    if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600);
      return `${hours} hour${hours === 1 ? '' : 's'} ago`;
    }

    // Days
    if (diffInSeconds < 2592000) { // 30 days
      const days = Math.floor(diffInSeconds / 86400);
      return `${days} day${days === 1 ? '' : 's'} ago`;
    }

    // For older dates, show the formatted date
    return formatLocalDateTime(utcDateString, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch (error) {
    console.warn('Invalid date string:', utcDateString);
    return 'Unknown time';
  }
}

/**
 * Formats a UTC date string to show just the time in user's local timezone
 * @param utcDateString - UTC date string from the API
 * @returns Time string (e.g., "2:30 PM")
 */
export function formatLocalTime(utcDateString: string): string {
  return formatLocalDateTime(utcDateString, {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  });
}

/**
 * Formats a UTC date string to show just the date in user's local timezone
 * @param utcDateString - UTC date string from the API
 * @returns Date string (e.g., "Jan 15, 2024")
 */
export function formatLocalDate(utcDateString: string): string {
  return formatLocalDateTime(utcDateString, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Checks if a date is today in the user's local timezone
 * @param utcDateString - UTC date string from the API
 * @returns true if the date is today
 */
export function isToday(utcDateString: string): boolean {
  try {
    const date = new Date(utcDateString);
    const today = new Date();
    return (
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear()
    );
  } catch (error) {
    return false;
  }
}

/**
 * Gets the user's timezone name (e.g., "America/New_York", "Europe/London")
 * @returns Timezone identifier
 */
export function getUserTimezone(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
}

/**
 * Formats a UTC date with timezone information
 * @param utcDateString - UTC date string from the API
 * @returns Formatted string with timezone (e.g., "Jan 15, 2024, 2:30 PM EST")
 */
export function formatLocalDateTimeWithTimezone(utcDateString: string): string {
  return formatLocalDateTime(utcDateString, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
    timeZoneName: 'short',
  });
}

/**
 * Converts a UTC hour (0-23) to the corresponding hour in the user's local timezone
 * @param utcHour - Hour in UTC (0-23)
 * @returns Hour in user's local timezone (0-23)
 */
export function convertUtcHourToLocal(utcHour: number): number {
  // Create a date for today at the given UTC hour
  const today = new Date();
  const utcDate = new Date(Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate(), utcHour, 0, 0));
  
  // Get the local hour
  return utcDate.getHours();
}

/**
 * Formats an hour number (0-23) as a readable time string
 * @param hour - Hour number (0-23)
 * @returns Formatted time string (e.g., "12 AM", "2 PM")
 */
export function formatHour(hour: number): string {
  return hour === 0 ? '12 AM' : hour < 12 ? `${hour} AM` : hour === 12 ? '12 PM' : `${hour - 12} PM`;
}

/**
 * Converts UTC-based hourly distribution data to local timezone
 * @param utcDistribution - Array of hourly distribution data with UTC hours
 * @returns Array with hours converted to local timezone, sorted by local hour
 */
export function convertDistributionToLocalTime<T extends { time: number }>(utcDistribution: T[]): T[] {
  // Create a map to handle the hour conversion and potential overlaps
  const localHourMap = new Map<number, T>();
  
  utcDistribution.forEach(item => {
    const localHour = convertUtcHourToLocal(item.time);
    const existingItem = localHourMap.get(localHour);
    
    if (existingItem) {
      // If multiple UTC hours map to the same local hour (rare edge case around DST),
      // combine the counts
      const combined = { ...item };
      if ('arrival_count' in item && 'arrival_count' in existingItem) {
        (combined as any).arrival_count = ((item as any).arrival_count || 0) + ((existingItem as any).arrival_count || 0);
      }
      if ('departure_count' in item && 'departure_count' in existingItem) {
        (combined as any).departure_count = ((item as any).departure_count || 0) + ((existingItem as any).departure_count || 0);
      }
      combined.time = localHour;
      localHourMap.set(localHour, combined);
    } else {
      localHourMap.set(localHour, { ...item, time: localHour });
    }
  });
  
  // Convert back to array and sort by local hour
  return Array.from(localHourMap.values()).sort((a, b) => a.time - b.time);
}

/**
 * Gets the current timezone offset in hours from UTC
 * @returns Timezone offset (e.g., -5 for EST, -8 for PST)
 */
export function getTimezoneOffsetHours(): number {
  return -new Date().getTimezoneOffset() / 60;
}