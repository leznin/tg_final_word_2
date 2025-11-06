/**
 * Utility to get the full URL for media files
 */

/**
 * Convert media URL from backend to full URL accessible from frontend
 * @param mediaUrl - URL from backend (e.g., "/static/chat_posts/file.jpg")
 * @returns Full URL that can be used in img/video tags
 */
export const getMediaUrl = (mediaUrl?: string): string | undefined => {
  if (!mediaUrl) return undefined;
  
  // If already a full URL (http/https), return as is
  if (mediaUrl.startsWith('http://') || mediaUrl.startsWith('https://')) {
    return mediaUrl;
  }
  
  // For relative URLs, they will be proxied by Vite in development
  // and served directly in production
  // Just ensure URL starts with /
  const normalizedUrl = mediaUrl.startsWith('/') ? mediaUrl : `/${mediaUrl}`;
  
  return normalizedUrl;
};

/**
 * Get API base URL
 */
export const getApiBaseUrl = (): string => {
  return import.meta.env.VITE_BACKEND_URL || '';
};
