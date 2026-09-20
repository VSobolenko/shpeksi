import { useTheme } from '@react-navigation/native'
import PropTypes from 'prop-types'
import React from 'react'
import { Image, TouchableOpacity } from 'react-native'
import Spinner from '../../../components/Spinner/Spinner'
import TextDefault from '../../../components/Text/TextDefault/TextDefault'
import { alignment } from '../../../utils/alignment'
import { moderateScale } from '../../../utils/scaling'
import useStyle from './styles'
import i18n from '../../../../i18n'

const googleIcon = require('../../../assets/images/google.png')

const FdGoogleBtn = props => {
  const styles = useStyle()
  const { colors } = useTheme()
  return (
    <TouchableOpacity
      activeOpacity={0.7}
      style={[styles.mainContainer, props.disabled && { opacity: 0.45 }]}
      disabled={props.disabled}
      onPressIn={props.disabled ? undefined : props.onPressIn}
      onPress={props.disabled ? undefined : props.onPress}>
      {props.loadingIcon
        ? (
        <Spinner backColor="rgba(0,0,0,0.1)" spinnerColor={colors.tagColor} />
          )
        : (
        <>
          <Image
            source={googleIcon}
            style={[
              {
                width: 25,
                height: 25,
                marginLeft: moderateScale(10)
              }
            ]}
          />
          <TextDefault style={alignment.MLlarge} bold>
            {props.disabled
              ? i18n.t('googleSignInUnavailable')
              : i18n.t('signupGoogle')}
          </TextDefault>
        </>
          )}
    </TouchableOpacity>
  )
}

FdGoogleBtn.propTypes = {
  onPress: PropTypes.func,
  loadingIcon: PropTypes.bool,
  onPressIn: PropTypes.func,
  disabled: PropTypes.bool
}
export default FdGoogleBtn
