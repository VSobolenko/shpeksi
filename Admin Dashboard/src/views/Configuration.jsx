import React from 'react'
import { withTranslation } from 'react-i18next'
import { Container } from 'reactstrap'
import { Query } from '@apollo/client/react/components'
import { gql } from '@apollo/client'
import Header from '../components/Headers/Header.jsx'
import { getConfiguration } from '../apollo/server'
import OrderConfiguration from '../components/Configuration/Order/Order'
import EmailConfiguration from '../components/Configuration/Email/Email'
import PaypalConfiguration from '../components/Configuration/Paypal/Paypal'
import StripeConfiguration from '../components/Configuration/Stripe/Stripe'
import CurrencyConfiguration from '../components/Configuration/Currency/Currency'
import Loader from 'react-loader-spinner'

const GET_CONFIGURATION = gql`
  ${getConfiguration}
`

const Configuration = props => {
  return (
    <>
      <Header />
      <Query query={GET_CONFIGURATION}>
        {({ loading, error, data }) => {
          if (loading) {
            return (
              <Container className="text-center mt-10" fluid>
                <Loader
                  type="TailSpin"
                  color="#fb6340"
                  height={300}
                  width={300}
                  visible={loading}
                />
              </Container>
            )
          }
          if (error) return 'Error :('
          return (
            <Container className="mt--7" fluid>
              <Loader
                type="TailSpin"
                color="#FFF"
                height={25}
                width={30}
                visible={loading}
              />
              <OrderConfiguration prefix={data.configuration.order_id_prefix} />
              <EmailConfiguration
                email={data.configuration.email}
                password={data.configuration.password}
                enabled={data.configuration.enable_email}
              />
              <PaypalConfiguration
                clientId={data.configuration.client_id}
                clientSecret={data.configuration.client_secret}
                sandbox={data.configuration.sandbox}
              />
              <StripeConfiguration
                publishableKey={data.configuration.publishable_key}
                secretKey={data.configuration.secret_key}
              />
              <CurrencyConfiguration
                currencyCode={data.configuration.currency}
                currencySymbol={data.configuration.currency_symbol}
              />
            </Container>
          )
        }}
      </Query>
    </>
  )
}

export default withTranslation()(Configuration)
