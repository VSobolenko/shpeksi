import { AntDesign } from '@expo/vector-icons'
import { useNavigation, useTheme } from '@react-navigation/native'
import React, { useLayoutEffect } from 'react'
import { TouchableOpacity, View } from 'react-native'
import i18n from '../../../i18n'
import { TextDefault, WrapperView } from '../../components'
import { NAVIGATION_SCREEN } from '../../utils/constant'
import useStyle from './styles'

const links = [
  {
    title: 'Product Page',
    url: '#'
  },
  {
    title: 'Docs',
    url: '#'
  },
  {
    title: 'Blog',
    url: '#'
  },
  { title: 'About Us', url: '#' }
]
function Help() {
  const styles = useStyle()
  const navigation = useNavigation()
  const { colors } = useTheme()

  useLayoutEffect(() => {
    navigation.setOptions({
      headerTitle: i18n.t('titleHelp'),
      headerRight: null
    })
  }, [navigation])

  return (
    <WrapperView>
      <View style={styles.flex}>
        {links.map(({ title, url }, index) => (
          <TouchableOpacity
            onPress={() =>
              navigation.navigate(NAVIGATION_SCREEN.HelpBrowser, { title, url })
            }
            style={styles.itemContainer}
            key={index}
          >
            <TextDefault H4>{i18n.t(title)}</TextDefault>
            <TouchableOpacity>
              <AntDesign
                name="arrowright"
                size={22}
                color={colors.fontMainColor}
              />
            </TouchableOpacity>
          </TouchableOpacity>
        ))}
      </View>
    </WrapperView>
  )
}

export default Help
