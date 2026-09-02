import React from 'react'
import { TouchableOpacity, View } from 'react-native'
import { FontAwesome } from '@expo/vector-icons'

function StarRating ({
  rating = 0,
  maxStars = 5,
  disabled = false,
  selectedStar,
  emptyStarColor = '#aaaaaa',
  fullStarColor = '#000000',
  starSize = 40
}) {
  const stars = Array.from({ length: maxStars }, (_, index) => {
    const value = index + 1
    const name = value <= rating ? 'star' : 'star-o'
    const color = value <= rating ? fullStarColor : emptyStarColor
    return (
      <TouchableOpacity
        key={value}
        activeOpacity={0.7}
        disabled={disabled}
        accessibilityRole="button"
        accessibilityLabel={`${value} star rating`}
        testID={`star-${value}`}
        onPress={() => selectedStar && selectedStar(value)}
      >
        <FontAwesome name={name} size={starSize} color={color} />
      </TouchableOpacity>
    )
  })

  return (
    <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
      {stars}
    </View>
  )
}

export default StarRating
