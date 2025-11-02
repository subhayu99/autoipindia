/**
 * Format a timestamp to a human-readable relative time
 * Examples: "5 mins ago", "2 hours ago", "3 days 2 hours ago"
 */
export function formatRelativeTime(timestamp: string | Date): string {
  const now = new Date();
  const then = new Date(timestamp);
  const diffMs = now.getTime() - then.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSecs < 60) {
    return 'just now';
  } else if (diffMins < 60) {
    return `${diffMins} ${diffMins === 1 ? 'min' : 'mins'} ago`;
  } else if (diffHours < 24) {
    const remainingMins = diffMins % 60;
    if (remainingMins > 0 && diffHours < 12) {
      return `${diffHours} ${diffHours === 1 ? 'hour' : 'hours'} ${remainingMins} ${remainingMins === 1 ? 'min' : 'mins'} ago`;
    }
    return `${diffHours} ${diffHours === 1 ? 'hour' : 'hours'} ago`;
  } else if (diffDays < 7) {
    const remainingHours = diffHours % 24;
    if (remainingHours > 0) {
      return `${diffDays} ${diffDays === 1 ? 'day' : 'days'} ${remainingHours} ${remainingHours === 1 ? 'hour' : 'hours'} ago`;
    }
    return `${diffDays} ${diffDays === 1 ? 'day' : 'days'} ago`;
  } else {
    // For older dates, show the actual date
    return then.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: then.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    });
  }
}

/**
 * Format a duration in milliseconds to human-readable format
 */
export function formatDuration(startTime: string, endTime?: string): string {
  const start = new Date(startTime);
  const end = endTime ? new Date(endTime) : new Date();
  const diffMs = end.getTime() - start.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);

  if (diffSecs < 60) {
    return `${diffSecs}s`;
  } else if (diffMins < 60) {
    return `${diffMins}m ${diffSecs % 60}s`;
  } else {
    const remainingMins = diffMins % 60;
    return `${diffHours}h ${remainingMins}m`;
  }
}
