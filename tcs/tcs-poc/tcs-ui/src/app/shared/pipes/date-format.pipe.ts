import { Pipe, PipeTransform } from '@angular/core';

/**
 * DateFormatPipe
 * 
 * Formats date values into human-readable strings.
 * Handles various input formats including timestamps, ISO strings, and Date objects.
 * 
 * Requirements: 
 * - 5.3: Format date columns as readable dates
 * - 16.3: Format event timestamps as readable dates
 * 
 * Usage:
 *   {{ dateValue | dateFormat }}
 *   {{ dateValue | dateFormat:'short' }}
 *   {{ timestamp | dateFormat:'full' }}
 */
@Pipe({
  name: 'dateFormat',
  standalone: true
})
export class DateFormatPipe implements PipeTransform {
  transform(value: string | number | Date | null | undefined, format: 'short' | 'medium' | 'long' | 'full' = 'medium'): string {
    if (!value) {
      return '';
    }

    let date: Date;

    // Handle different input types
    if (typeof value === 'number') {
      // Assume timestamp in milliseconds
      date = new Date(value);
    } else if (typeof value === 'string') {
      // Parse ISO string or other date string
      date = new Date(value);
    } else if (value instanceof Date) {
      date = value;
    } else {
      return '';
    }

    // Check if date is valid
    if (isNaN(date.getTime())) {
      return '';
    }

    // Format based on requested format
    switch (format) {
      case 'short':
        // MM/DD/YYYY
        return this.formatShort(date);
      case 'medium':
        // MMM DD, YYYY HH:MM AM/PM
        return this.formatMedium(date);
      case 'long':
        // Month DD, YYYY at HH:MM:SS AM/PM
        return this.formatLong(date);
      case 'full':
        // Day, Month DD, YYYY at HH:MM:SS AM/PM
        return this.formatFull(date);
      default:
        return this.formatMedium(date);
    }
  }

  private formatShort(date: Date): string {
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const year = date.getFullYear();
    return `${month}/${day}/${year}`;
  }

  private formatMedium(date: Date): string {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const month = months[date.getMonth()];
    const day = date.getDate();
    const year = date.getFullYear();
    const time = this.formatTime(date);
    return `${month} ${day}, ${year} ${time}`;
  }

  private formatLong(date: Date): string {
    const months = ['January', 'February', 'March', 'April', 'May', 'June', 
                    'July', 'August', 'September', 'October', 'November', 'December'];
    const month = months[date.getMonth()];
    const day = date.getDate();
    const year = date.getFullYear();
    const time = this.formatTimeWithSeconds(date);
    return `${month} ${day}, ${year} at ${time}`;
  }

  private formatFull(date: Date): string {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const dayName = days[date.getDay()];
    const months = ['January', 'February', 'March', 'April', 'May', 'June', 
                    'July', 'August', 'September', 'October', 'November', 'December'];
    const month = months[date.getMonth()];
    const day = date.getDate();
    const year = date.getFullYear();
    const time = this.formatTimeWithSeconds(date);
    return `${dayName}, ${month} ${day}, ${year} at ${time}`;
  }

  private formatTime(date: Date): string {
    let hours = date.getHours();
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12;
    return `${hours}:${minutes} ${ampm}`;
  }

  private formatTimeWithSeconds(date: Date): string {
    let hours = date.getHours();
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12;
    return `${hours}:${minutes}:${seconds} ${ampm}`;
  }
}
