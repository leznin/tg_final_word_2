import FingerprintJS from '@fingerprintjs/fingerprintjs'

// Use the free version of FingerprintJS
let fpPromise: Promise<any> | null = null

export const getFingerprint = async (): Promise<string> => {
  try {
    if (!fpPromise) {
      // Initialize free FingerprintJS
      fpPromise = FingerprintJS.load()
    }

    const fp = await fpPromise
    const result = await fp.get()

    return result.visitorId
  } catch (error) {
    console.error('FingerprintJS error:', error)

    // Fallback: create a simple fingerprint based on browser properties
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    ctx?.fillText('fingerprint', 10, 10)

    const fallbackFingerprint = [
      navigator.userAgent,
      navigator.language,
      screen.width + 'x' + screen.height,
      new Date().getTimezoneOffset(),
      !!window.sessionStorage,
      !!window.localStorage,
      !!window.indexedDB,
      canvas.toDataURL()
    ].join('|')

    // Simple hash function
    let hash = 0
    for (let i = 0; i < fallbackFingerprint.length; i++) {
      const char = fallbackFingerprint.charCodeAt(i)
      hash = ((hash << 5) - hash) + char
      hash = hash & hash // Convert to 32-bit integer
    }

    return Math.abs(hash).toString(36)
  }
}
