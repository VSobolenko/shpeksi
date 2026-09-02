import React from 'react'
import { useQuery, gql } from '@apollo/client'
import PropTypes from 'prop-types'

import { getConfiguration } from '../apollo/server'

const GETCONFIGURATION = gql`
  ${getConfiguration}
`

const ConfigurationContext = React.createContext({})

export const ConfigurationProvider = props => {
  const { loading, data, error } = useQuery(GETCONFIGURATION)
  const configuration =
    loading || error || !data.configuration
      ? { currency: '', currency_symbol: '' }
      : data.configuration
  return (
    <ConfigurationContext value={configuration}>
      {props.children}
    </ConfigurationContext>
  )
}

ConfigurationProvider.propTypes = {
  children: PropTypes.node.isRequired
}

export const ConfigurationConsumer = ConfigurationContext.Consumer
export default ConfigurationContext
