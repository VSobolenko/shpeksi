/* eslint-disable react/prop-types */
import { Asset } from 'expo-asset'
import * as SplashScreen from 'expo-splash-screen'
import React, { useEffect, useMemo, useState } from 'react'
import { Animated, StyleSheet, View } from 'react-native'
import { COLORS } from '../../Theme'

/**
 * Fade-out overlay splash. Never scale the layout (that "shrinks" the whole
 * screen) and never return null (that flashes a black frame).
 */
function AnimatedSplashScreen({ children, image }) {
  const opacity = useMemo(() => new Animated.Value(1), [])
  const [isAppReady, setAppReady] = useState(false)
  const [animationCompleted, setAnimationCompleted] = useState(false)

  useEffect(() => {
    if (!isAppReady) return
    Animated.timing(opacity, {
      toValue: 0,
      duration: 450,
      useNativeDriver: true
    }).start(({ finished }) => {
      if (finished) setAnimationCompleted(true)
    })
  }, [isAppReady, opacity])

  const onImageLoaded = async() => {
    try {
      await SplashScreen.hideAsync()
    } catch (e) {
      // ignore — native splash may already be gone
    } finally {
      setAppReady(true)
    }
  }

  return (
    <View style={styles.root}>
      {children}
      {!animationCompleted && (
        <Animated.View
          pointerEvents="none"
          style={[styles.overlay, { opacity }]}
        >
          <Animated.Image
            style={styles.image}
            source={image}
            onLoadEnd={onImageLoaded}
            onError={onImageLoaded}
            fadeDuration={0}
            resizeMode="cover"
          />
        </Animated.View>
      )}
    </View>
  )
}

function AnimatedSplash({ children, image }) {
  const [isSplashReady, setSplashReady] = useState(false)

  useEffect(() => {
    let mounted = true
    Asset.fromModule(image)
      .downloadAsync()
      .catch(() => {})
      .finally(() => {
        if (mounted) setSplashReady(true)
      })
    // Fail-safe: never leave the user on a blank frame
    const t = setTimeout(() => {
      if (mounted) setSplashReady(true)
    }, 2500)
    return () => {
      mounted = false
      clearTimeout(t)
    }
  }, [image])

  if (!isSplashReady) {
    return <View style={[styles.root, styles.fallback]} />
  }

  return <AnimatedSplashScreen image={image}>{children}</AnimatedSplashScreen>
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: COLORS.primary || '#febb2c'
  },
  fallback: {
    backgroundColor: '#febb2c'
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: '#febb2c'
  },
  image: {
    width: '100%',
    height: '100%'
  }
})

export default React.memo(AnimatedSplash)
