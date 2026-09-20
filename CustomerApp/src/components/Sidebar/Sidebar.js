/* eslint-disable react/prop-types */
import { SimpleLineIcons } from '@expo/vector-icons'
import { DrawerContentScrollView, DrawerItem } from '@react-navigation/drawer'
import { DrawerActions, useTheme } from '@react-navigation/native'
import React, { useContext } from 'react'
import { Animated, View } from 'react-native'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import i18n from '../../../i18n'
import UserContext from '../../context/User'
import NavigationService from '../../routes/navigationService'
import { alignment } from '../../utils/alignment'
import { ICONS_NAME, NAVIGATION_SCREEN } from '../../utils/constant'
import { scale } from '../../utils/scaling'
import { CustomIcon } from '../CustomIcon'
import SideDrawerProfile from '../Drawer/Profile/DrawerProfile'
import { TextDefault } from '../Text'
import useStyle from './styles'

const MENU = [
  {
    title: 'home',
    icon: ICONS_NAME.Home,
    navigateTo: NAVIGATION_SCREEN.Menu,
    isAuth: false
  },
  {
    title: 'titleProfile',
    icon: 'user',
    navigateTo: 'Profile',
    isAuth: true
  },
  {
    title: 'titleOrders',
    icon: ICONS_NAME.Cart,
    navigateTo: NAVIGATION_SCREEN.MyOrders,
    isAuth: true
  },
  {
    title: 'myAddresses',
    icon: ICONS_NAME.Location,
    navigateTo: NAVIGATION_SCREEN.Addresses,
    isAuth: true
  },
  {
    title: 'titleHelp',
    icon: ICONS_NAME.Info,
    navigateTo: NAVIGATION_SCREEN.Help,
    isAuth: false
  },
  {
    title: 'titleSettings',
    icon: ICONS_NAME.Setting,
    navigateTo: NAVIGATION_SCREEN.Settings,
    isAuth: true
  }
]

function SidebBar(props) {
  const styles = useStyle()
  const { colors } = useTheme()
  const navigation = props.navigation
  const inset = useSafeAreaInsets()
  const { isLoggedIn, logout } = useContext(UserContext)
  const navigationName = NavigationService.currentRoute()?.name
  return (
    <DrawerContentScrollView
      {...props}
      contentContainerStyle={styles.scrollContent}
    >
      <Animated.View
        style={{
          flex: 1,
          backgroundColor: 'transparent',
          marginBottom: inset.bottom
        }}
      >
        <View style={styles.headerContainer}>
          <SideDrawerProfile navigation={navigation} />
        </View>
        <View style={styles.menuContainer}>
          <View>
            {MENU.map((item, index) => (
              <DrawerItem
                pressColor={'rgba(0,0,0,0.2)'}
                key={`DRAWER_ITEM_LIST_${index}`}
                style={styles.drawerItem}
                activeBackgroundColor={'transparent'}
                activeTintColor={colors.black}
                inactiveTintColor={colors.fontWhite}
                focused={navigationName === item.navigateTo}
                label={(props) => (
                  <TextDefault
                    H5
                    medium
                    numberOfLines={2}
                    textColor={props.color}
                    style={[styles.textView, styles.flex]}
                  >
                    {i18n.t(item.title)}
                  </TextDefault>
                )}
                icon={(props) => {
                  if (item.icon !== 'user') {
                    return (
                      <CustomIcon
                        name={item.icon}
                        color={props.color}
                        size={scale(22)}
                      />
                    )
                  } else {
                    return (
                      <SimpleLineIcons
                        name={item.icon}
                        color={props.color}
                        size={scale(22)}
                      />
                    )
                  }
                }}
                onPress={async() => {
                  const screen =
                    item.isAuth && !isLoggedIn
                      ? NAVIGATION_SCREEN.CreateAccount
                      : item.navigateTo
                  navigation.navigate('noDrawer', { screen })
                  navigation.dispatch(DrawerActions.closeDrawer())
                }}
              />
            ))}
          </View>
          <View style={alignment.PBmedium}>
            {isLoggedIn && (
              <DrawerItem
                pressColor={'rgba(0,0,0,0.2)'}
                style={styles.drawerItem}
                label={() => (
                  <TextDefault
                    H5
                    medium
                    textColor={styles.whiteFont.color}
                    style={[styles.textView, styles.flex]}
                  >
                    {i18n.t('titleLogout')}
                  </TextDefault>
                )}
                icon={() => (
                  <CustomIcon
                    name={ICONS_NAME.Exit}
                    color={styles.whiteFont.color}
                    size={scale(22)}
                  />
                )}
                onPress={async() => {
                  logout()
                  navigation.navigate('noDrawer', {
                    screen: NAVIGATION_SCREEN.Menu
                  })
                  navigation.dispatch(DrawerActions.closeDrawer())
                }}
              />
            )}
          </View>
        </View>
      </Animated.View>
    </DrawerContentScrollView>
  )
}
export default SidebBar
