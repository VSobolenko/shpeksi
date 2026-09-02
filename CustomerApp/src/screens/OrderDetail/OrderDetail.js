import { MaterialIcons } from '@expo/vector-icons'
import { useNavigation, useRoute, useTheme } from '@react-navigation/native'
import React, { useContext, useEffect, useLayoutEffect } from 'react'
import { ScrollView, TouchableOpacity, View } from 'react-native'
import i18n from '../../../i18n'
import {
  Spinner,
  TextDefault,
  TextError,
  WrapperView
} from '../../components'
import { orderStatuses } from '../../components/Menu/StatusCard/StatusCard'
import ConfigurationContext from '../../context/Configuration'
import UserContext from '../../context/User'
import { alignment } from '../../utils/alignment'
import { NAVIGATION_SCREEN } from '../../utils/constant'
import { scale } from '../../utils/scaling'
import useStyle from './styles'

function calculatePrice(food) {
  let foodPrice = food.variation.price
  food.addons.forEach((addons) => {
    addons.options.forEach((addon) => {
      foodPrice += addon.price
    })
  })
  return foodPrice
}

function OrderDetail() {
  const styles = useStyle()
  const route = useRoute()
  const { colors } = useTheme()
  const navigation = useNavigation()
  const id = route.params._id ?? null
  const cart = route.params.clearCart ?? false
  const { loadingOrders, errorOrders, orders, clearCart } =
    useContext(UserContext)
  const configuration = useContext(ConfigurationContext)

  const order = orders.find((o) => o._id === id)

  useLayoutEffect(() => {
    navigation.setOptions({
      headerTitle: i18n.t('orderDetail'),
      headerRight: null
    })
  }, [navigation])

  useEffect(() => {
    return () => {
      if (cart) {
        clear()
      }
    }
  }, [cart])
  async function clear() {
    await clearCart()
  }

  if (loadingOrders || !order) return <Spinner />
  if (errorOrders) return <TextError text={i18n.t('error')} />
  return (
    <WrapperView>
      <ScrollView style={[styles.flex]}>
        <View style={styles.container}>
          <TextDefault
            textColor={colors.buttonBackgroundBlue}
            bolder
            H3
            style={alignment.MBsmall}
          >
            {i18n.t('thankYou')}
          </TextDefault>
          <TextDefault
            textColor={colors.fontSecondColor}
            medium
            H5
            style={[alignment.MTsmall]}
          >
            {i18n.t('orderId')}
          </TextDefault>
          <TextDefault H4 bolder style={alignment.PTxSmall}>
            {order.order_id}
          </TextDefault>
          <TextDefault
            textColor={colors.fontSecondColor}
            bold
            H5
            style={[alignment.MTlarge]}
          >
            {i18n.t('status')}
          </TextDefault>
          <TextDefault
            textColor={colors.buttonBackgroundBlue}
            H4
            medium
            style={[alignment.MBsmall, alignment.MTxSmall]}
          >
            {i18n.t(order.order_status)}{' '}
            <TextDefault medium>
              {/* ({checkStatus(i18n.t(order.order_status))?.statusText || "..."}) */}
              {`(${i18n.t(orderStatuses[order.order_status]?.statusText)})`}
            </TextDefault>
          </TextDefault>
        </View>
        <View style={[styles.marginBottom10, styles.orderReceipt]}>
          {order.items.map((item, index) => (
            <View style={[styles.marginBottom10, styles.floatView]} key={index}>
              <TextDefault H5 style={{ width: '10%' }}>
                {item.quantity}x
              </TextDefault>
              <TextDefault
                textColor={colors.fontMainColor}
                style={{ width: '65%' }}
              >
                {item.food.title}
              </TextDefault>
              <TextDefault
                textColor={colors.fontMainColor}
                style={{ width: '25%' }}
                right
              >
                {configuration.currency_symbol}
                {parseFloat(calculatePrice(item)).toFixed(2)}
              </TextDefault>
            </View>
          ))}
          <View style={[styles.horizontalLine, styles.marginBottom10]} />
          <View style={[styles.marginBottom10, styles.floatView]}>
            <TextDefault
              textColor={colors.fontMainColor}
              medium
              style={{ width: '40%' }}
            >
              {i18n.t('subTotal')}
            </TextDefault>
            <TextDefault
              textColor={colors.fontMainColor}
              medium
              style={{ width: '60%' }}
              right
            >
              {configuration.currency_symbol}
              {parseFloat(order.order_amount).toFixed(2)}
            </TextDefault>
          </View>
          <View style={[styles.floatView]}>
            <TextDefault
              textColor={colors.fontMainColor}
              bold
              style={{ width: '40%' }}
            >
              {i18n.t('total')}
            </TextDefault>
            <TextDefault
              textColor={colors.fontMainColor}
              bold
              style={{ width: '60%' }}
              right
            >
              {configuration.currency_symbol}
              {parseFloat(order.order_amount).toFixed(2)}
            </TextDefault>
          </View>
        </View>
        {i18n.t(order.order_status) === i18n.t('COMPLETED') &&
          order.review &&
          order.review.rating === 0 && (
            <View style={styles.orderReceipt}>
              <TextDefault H3 bolder style={alignment.MBsmall}>
                {i18n.t('anySuggestion')}
              </TextDefault>
              <TextDefault
                textColor={colors.fontSecondColor}
                bold
                style={[alignment.MBsmall, alignment.MTsmall]}
              >
                {i18n.t('reviewRegarding')}
              </TextDefault>
              <TouchableOpacity
                activeOpacity={0.7}
                style={[styles.floatView, { justifyContent: 'center' }]}
                onPress={() =>
                  navigation.navigate(NAVIGATION_SCREEN.RateAndReview, {
                    _id: order._id
                  })
                }
              >
                <MaterialIcons
                  name="rate-review"
                  size={scale(20)}
                  color={colors.iconColorPrimary}
                />
                <TextDefault
                  textColor={colors.iconColorPrimary}
                  style={[alignment.MBsmall, alignment.MTsmall, alignment.ML10]}
                  H5
                  bold
                  center
                >
                  {i18n.t('writeReview')}
                </TextDefault>
              </TouchableOpacity>
            </View>
        )}
      </ScrollView>
    </WrapperView>
  )
}

export default OrderDetail
