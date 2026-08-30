import { StyleSheet } from 'react-native'
import { scale } from '../../utils/scaling'

const useStyle = () =>
  StyleSheet.create({
    wrapper: {
      width: '100%',
      marginVertical: scale(2)
    },
    inputContainer: {
      minHeight: scale(56),
      justifyContent: 'flex-end',
      paddingHorizontal: scale(12),
      borderRadius: scale(8)
    },
    label: {
      position: 'absolute',
      left: scale(12),
      right: scale(12),
      zIndex: 1
    },
    labelRest: {
      top: scale(19),
      fontSize: scale(13)
    },
    labelFloat: {
      top: scale(7),
      fontSize: scale(10)
    },
    inputRow: {
      flexDirection: 'row',
      alignItems: 'center',
      alignSelf: 'stretch'
    },
    prefix: {
      fontSize: scale(13),
      marginRight: scale(2),
      paddingBottom: scale(8)
    },
    input: {
      flex: 1,
      padding: 0,
      fontSize: scale(13)
    },
    inputRest: {
      paddingTop: scale(8),
      paddingBottom: scale(10)
    },
    inputFloat: {
      paddingTop: scale(16),
      paddingBottom: scale(6)
    },
    error: {
      fontSize: scale(10),
      marginTop: scale(2),
      marginLeft: scale(12)
    }
  })

export default useStyle
