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

/**
 * Formats a Date object to YYYY-MM-DD string for API usage
 * @param date - Date object to format
 * @returns Formatted date string (e.g., "2024-01-15")
 */
export function formatDateForApi(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * Gets date N days ago from today
 * @param days - Number of days ago
 * @returns Date object
 */
export function getDaysAgo(days: number): Date {
  const date = new Date();
  date.setDate(date.getDate() - days);
  return date;
}

/**
 * Gets today's date
 * @returns Today's Date object
 */
export function getToday(): Date {
  return new Date();
}

/**
 * Parses YYYY-MM-DD string to Date object
 * @param dateString - Date string in YYYY-MM-DD format
 * @returns Date object or null if invalid
 */
export function parseDateFromApi(dateString: string): Date | null {
  try {
    const date = new Date(dateString + 'T00:00:00');
    return isNaN(date.getTime()) ? null : date;
  } catch {
    return null;
  }
}

/**
 * Validates if a date string is in YYYY-MM-DD format
 * @param dateString - Date string to validate
 * @returns true if valid format
 */
export function isValidDateString(dateString: string): boolean {
  const regex = /^\d{4}-\d{2}-\d{2}$/;
  if (!regex.test(dateString)) return false;
  
  const date = parseDateFromApi(dateString);
  return date !== null;
}

/**
 * Gets preset date ranges for filtering
 * @returns Object with preset date ranges formatted for API
 */
export function getDatePresets() {
  const today = getToday();
  const yesterday = getDaysAgo(1);
  
  return {
    today: {
      startDate: formatDateForApi(today),
      endDate: formatDateForApi(today),
      label: 'Today'
    },
    lastDay: {
      startDate: formatDateForApi(yesterday),
      endDate: formatDateForApi(yesterday),
      label: 'Yesterday'
    },
    last7Days: {
      startDate: formatDateForApi(getDaysAgo(7)),
      endDate: formatDateForApi(today),
      label: 'Last 7 Days'
    },
    last30Days: {
      startDate: formatDateForApi(getDaysAgo(30)),
      endDate: formatDateForApi(today),
      label: 'Last 30 Days'
    },
    last90Days: {
      startDate: formatDateForApi(getDaysAgo(90)),
      endDate: formatDateForApi(today),
      label: 'Last 90 Days'
    },
    allTime: {
      startDate: undefined,
      endDate: undefined,
      label: 'All Time'
    }
  };
}