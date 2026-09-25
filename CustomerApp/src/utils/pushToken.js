import * as Notifications from 'expo-notifications'
import Constants from 'expo-constants'
import { Platform } from 'react-native'

/**
 * Never block login/register on push setup. Missing EAS projectId or
 * simulator / denied permission must not hang the auth flow.
 */
export async function getNotificationTokenSafe() {
  try {
    const isDevice =
      Constants.isDevice ??
      Constants.expoConfig?.extra?.isDevice ??
      true
    if (!isDevice && Platform.OS !== 'android') {
      return null
    }
    const { status: existing } = await Notifications.getPermissionsAsync()
    let status = existing
    if (existing !== 'granted') {
      const req = await Notifications.requestPermissionsAsync()
      status = req.status
    }
    if (status !== 'granted') return null

    const projectId =
      Constants.expoConfig?.extra?.eas?.projectId ||
      Constants.easConfig?.projectId ||
      process.env.EAS_PROJECT_ID

    const opts = projectId ? { projectId } : undefined
    const token = await Notifications.getExpoPushTokenAsync(opts)
    return token?.data || null
  } catch (e) {
    console.warn('push token skipped', e?.message || e)
    return null
  }
}
