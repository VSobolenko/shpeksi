import { useTheme } from '@react-navigation/native'
import React, { useImperativeHandle, useRef, useState } from 'react'
import { Text, TextInput, View } from 'react-native'
import useStyle from './styles'

function TextField(props) {
  const { colors } = useTheme()
  const styles = useStyle()
  const inputRef = useRef(null)

  const controlled = props.value !== undefined
  const [internalValue, setInternalValue] = useState(props.defaultValue ?? '')
  const [focused, setFocused] = useState(false)

  const value = controlled ? props.value : internalValue
  const hasValue = value !== undefined && value !== null && value !== ''
  const floatLabel = focused || hasValue

  const textColor = props.textColor || colors.fontMainColor
  const baseColor = props.baseColor || colors.fontSecondColor
  const errorColor = props.errorColor || colors.errorColor
  const tintColor = props.tintColor || colors.selected
  const inputColor = props.error ? errorColor : textColor
  const labelColor = props.error
    ? errorColor
    : floatLabel
      ? tintColor
      : baseColor

  useImperativeHandle(props.ref, () => ({
    setValue: text => setInternalValue(text),
    focus: () => inputRef.current && inputRef.current.focus(),
    blur: () => inputRef.current && inputRef.current.blur(),
    value: () => value
  }))

  function handleChangeText(text) {
    if (!controlled) setInternalValue(text)
    if (props.onChangeText) props.onChangeText(text)
  }

  return (
    <View style={styles.wrapper}>
      <View style={[styles.inputContainer, props.inputContainerStyle]}>
        {props.label
          ? (
          <Text
            style={[
              styles.label,
              floatLabel ? styles.labelFloat : styles.labelRest,
              props.labelTextStyle,
              { color: labelColor }
            ]}
            numberOfLines={1}>
            {props.label}
          </Text>
            )
          : null}
        <View style={styles.inputRow}>
          {props.prefix
            ? (
            <Text style={[styles.prefix, { color: inputColor }]}>
              {props.prefix}
            </Text>
              )
            : null}
          <TextInput
            ref={inputRef}
            style={[
              styles.input,
              floatLabel ? styles.inputFloat : styles.inputRest,
              props.style,
              { color: inputColor }
            ]}
            value={value}
            editable={props.editable}
            onChangeText={handleChangeText}
            testID={props.testID}
            accessibilityLabel={props.accessibilityLabel}
            onFocus={event => {
              setFocused(true)
              if (props.onFocus) props.onFocus(event)
            }}
            onBlur={event => {
              setFocused(false)
              if (props.onBlur) props.onBlur(event)
            }}
            secureTextEntry={props.secureTextEntry}
            keyboardType={props.keyboardType}
            multiline={props.multiline}
            maxLength={props.maxLength}
            textAlignVertical={props.textAlignVertical}
            placeholder={props.placeholder}
            autoCapitalize={props.autoCapitalize}
          />
        </View>
      </View>
      {props.error
        ? (
        <Text style={[styles.error, { color: errorColor }]} numberOfLines={2}>
          {props.error}
        </Text>
          )
        : null}
    </View>
  )
}

export default TextField
