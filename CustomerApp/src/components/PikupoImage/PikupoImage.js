/* eslint-disable react/prop-types */
import React, { useState } from 'react'
import { Image, View } from 'react-native'
import { isObject } from 'validate.js'
import Spinner from '../Spinner/Spinner'
import useStyle from './styles'

// Keep placeholders small — multi-MB PNGs caused endless Android loaders.
const PLACEHOLDER = require('../../assets/images/placeholder.png')

function PikupoImage({
  imgSource,
  imgStyle = null,
  resizeMode = 'cover',
  spinnerProps
}) {
  const styles = useStyle()
  const [loading, setLoading] = useState(true)
  const [failed, setFailed] = useState(false)

  const hasRemote =
    isObject(imgSource) &&
    typeof imgSource.uri === 'string' &&
    imgSource.uri.length > 0
  const hasLocalModule = typeof imgSource === 'number'
  const useSource =
    !failed && (hasRemote || hasLocalModule) ? imgSource : PLACEHOLDER
  const style = imgStyle || styles.imgContainer

  return (
    <View style={style}>
      {loading
        ? (
        <Spinner animating size="small" style={style} {...spinnerProps} />
          )
        : null}
      <Image
        source={
          isObject(useSource)
            ? { ...useSource, cache: 'force-cache' }
            : useSource
        }
        defaultSource={PLACEHOLDER}
        style={[styles.imgResponsive, style]}
        onLoadStart={() => setLoading(true)}
        onLoadEnd={() => setLoading(false)}
        onError={() => {
          setFailed(true)
          setLoading(false)
        }}
        resizeMode={failed || !hasRemote ? 'contain' : resizeMode}
      />
    </View>
  )
}

export default React.memo(PikupoImage)
