import { useMutation } from '@apollo/client'
import { Ionicons } from '@expo/vector-icons'
import { useNavigation, useRoute, useTheme } from '@react-navigation/native'
import { gql } from '@apollo/client'
import React, { useLayoutEffect, useState } from 'react'
import {
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  TouchableOpacity,
  View
} from 'react-native'
import { FilledTextField } from '../../components'
import i18n from '../../../i18n'
import { editAddress } from '../../apollo/server'
import {
  FlashMessage,
  Spinner,
  TextDefault,
  WrapperView
} from '../../components'
import { alignment } from '../../utils/alignment'
import { scale } from '../../utils/scaling'
import useStyle from './styles'

const EDIT_ADDRESS = gql`
  ${editAddress}
`

const labelValues = [
  {
    title: 'Home',
    value: 'Home'
  },
  {
    title: 'Work',
    value: 'Work'
  },
  {
    title: 'Other',
    value: 'Other'
  }
]

function EditAddress() {
  const { colors } = useTheme()
  const route = useRoute()
  const styles = useStyle()
  const navigation = useNavigation()
  const [_id] = useState(route.params._id ?? null)
  const [selectedLabel, setSelectedLabel] = useState(
    route.params.label ?? labelValues[0].value
  )
  const [deliveryAddress, setDeliveryAddress] = useState(
    route.params.delivery_address ?? ''
  )
  const [deliveryDetails, setDeliveryDetails] = useState(
    route.params.details ?? ''
  )
  const [deliveryAddressError, setDeliveryAddressError] = useState('')
  const [deliveryDetailsError, setDeliveryDetailsError] = useState('')

  const [mutate, { loading }] = useMutation(EDIT_ADDRESS, {
    onCompleted,
    onError
  })

  useLayoutEffect(() => {
    navigation.setOptions({
      headerRight: null,
      title: i18n.t('editAddress')
    })
  }, [navigation])

  function onCompleted() {
    FlashMessage({
      message: i18n.t('addressUpdated')
    })
    navigation.goBack()
  }

  function onError(error) {
    FlashMessage({
      message: `${i18n.t('AnErrorOccured')} ${error}`
    })
  }

  return (
    <WrapperView>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={Platform.OS === 'android' ? 20 : 0}
        style={styles.flex}
        enabled>
        <View style={styles.flex}>
          <ScrollView
            style={styles.flex}
            contentContainerStyle={styles.subContainer}
            showsVerticalScrollIndicator={false}>
            <View style={styles.upperContainer}>
              <View style={styles.labelButtonContainer}>
                <View style={alignment.PBsmall}>
                  <TextDefault H5 bold>
                    {i18n.t('labelAs')}
                  </TextDefault>
                </View>
                <View style={styles.buttonInline}>
                  {labelValues.map((label, index) => {
                    const isSelected = selectedLabel === label.value
                    return (
                      <TouchableOpacity
                        activeOpacity={0.5}
                        key={index}
                        style={
                          isSelected ? styles.activeLabel : styles.labelButton
                        }
                        onPress={() => {
                          setSelectedLabel(label.value)
                        }}>
                        {isSelected && (
                          <Ionicons
                            name="checkmark-circle"
                            size={20}
                            color={colors.lightBackground}
                          />
                        )}
                        <TextDefault
                          textColor={
                            isSelected
                              ? colors.lightBackground
                              : colors.placeHolderColor
                          }
                          bold
                          center>
                          {i18n.t(label.title)}
                        </TextDefault>
                      </TouchableOpacity>
                    )
                  })}
                </View>
              </View>

              <View style={styles.addressContainer}>
                <FilledTextField
                  error={deliveryAddressError}
                  value={deliveryAddress}
                  label={i18n.t('fullAddress')}
                  fontSize={scale(12)}
                  labelFontSize={scale(12)}
                  activeLineWidth={0}
                  lineWidth={0}
                  labelHeight={20}
                  maxLength={100}
                  textColor={colors.fontMainColor}
                  baseColor={colors.fontMainColor}
                  errorColor={colors.errorColor}
                  tintColor={
                    !deliveryAddressError ? colors.selected : colors.errorColor
                  }
                  labelOffset={{ y1: -5 }}
                  labelTextStyle={styles.labelStyle}
                  inputContainerStyle={styles.textContainer}
                  onChangeText={text => {
                    setDeliveryAddress(text)
                  }}
                  onBlur={() => {
                    setDeliveryAddressError(
                      !deliveryAddress.trim().length
                        ? i18n.t('addressReq')
                        : null
                    )
                  }}
                />
                <FilledTextField
                  error={deliveryDetailsError}
                  label={i18n.t('addressDetails')}
                  labelFontSize={scale(12)}
                  activeLineWidth={0}
                  lineWidth={0}
                  labelHeight={20}
                  fontSize={scale(12)}
                  textAlignVertical="top"
                  multiline={false}
                  maxLength={30}
                  textColor={colors.fontMainColor}
                  baseColor={colors.fontMainColor}
                  errorColor={colors.errorColor}
                  tintColor={
                    !deliveryDetailsError ? colors.selected : colors.errorColor
                  }
                  labelTextStyle={styles.labelStyle}
                  inputContainerStyle={styles.textContainer}
                  labelOffset={{ y1: -5 }}
                  value={deliveryDetails}
                  onChangeText={text => {
                    setDeliveryDetails(text)
                  }}
                  onBlur={() => {
                    setDeliveryDetailsError(
                      !deliveryDetails.trim().length
                        ? i18n.t('addressDetailsRequired')
                        : null
                    )
                  }}
                />
              </View>
            </View>

            <TouchableOpacity
              disabled={loading}
              onPress={() => {
                const deliveryAddressError = !deliveryAddress.trim().length
                  ? i18n.t('addressReq')
                  : null
                const deliveryDetailsError = !deliveryDetails.trim().length
                  ? i18n.t('addressReq')
                  : null

                setDeliveryAddressError(deliveryAddressError)
                setDeliveryDetailsError(deliveryDetailsError)

                if (
                  deliveryAddressError === null &&
                  deliveryDetailsError === null
                ) {
                  mutate({
                    variables: {
                      addressInput: {
                        _id: _id,
                        delivery_address: deliveryAddress.trim(),
                        details: deliveryDetails.trim(),
                        label: selectedLabel
                      }
                    }
                  })
                }
              }}
              activeOpacity={0.5}
              style={styles.saveBtnContainer}>
              {loading ? (
                <View style={styles.spinnerView}>
                  <Spinner
                    backColor="transparent"
                    spinnerColor={colors.buttonText}
                  />
                </View>
              ) : (
                <TextDefault textColor={colors.buttonText} H5 bold>
                  {i18n.t('saveContBtn')}
                </TextDefault>
              )}
            </TouchableOpacity>
            <TouchableOpacity
              style={[alignment.PBsmall, alignment.PTsmall]}
              activeOpacity={0.7}
              onPress={() => navigation.goBack()}>
              <TextDefault H4 bold>
                {i18n.t('cancel')}
              </TextDefault>
            </TouchableOpacity>
          </ScrollView>
        </View>
      </KeyboardAvoidingView>
    </WrapperView>
  )
}

export default EditAddress
