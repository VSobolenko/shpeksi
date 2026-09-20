import React, { useState } from 'react'
import { withTranslation } from 'react-i18next'
// reactstrap components
import {
  Button,
  Card,
  CardHeader,
  CardBody,
  FormGroup,
  Form,
  Input,
  InputGroupAddon,
  InputGroupText,
  InputGroup,
  Col,
  UncontrolledAlert
} from 'reactstrap'

import { Navigate, useLocation } from 'react-router-dom'
import { Mutation } from '@apollo/client/react/components'
import { gql } from '@apollo/client'
import { adminLogin } from '../apollo/server'
import { validateFunc } from '../constraints/constraints'
const LOGIN = gql`
  ${adminLogin}
`

const Login = props => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [emailError, setEmailError] = useState(null)
  const [passwordError, setPasswordError] = useState(null)
  const [error, setError] = useState(null)
  const [redirectToReferrer, setRedirectToReferrer] = useState(
    !!localStorage.getItem('user-pikupo')
  )

  const onBlur = (event, field) => {
    if (field === 'email') {
      setEmailError(!validateFunc({ email: email }, 'email'))
    }
    if (field === 'password') {
      setPasswordError(!validateFunc({ password: password }, 'password'))
    }
  }
  const validate = () => {
    const EmailError = !validateFunc({ email: email }, 'email')
    const PasswordError = !validateFunc({ password: password }, 'password')
    setEmailError(EmailError)
    setPasswordError(PasswordError)
    const isValid = EmailError && PasswordError
    // Report *why* nothing happens. Previously an invalid field only turned the
    // input red: the mutation was skipped and the user saw no message at all.
    setError(isValid ? null : t('Check your email and password'))
    return isValid
  }

  const location = useLocation()
  const { from } = location.state || { from: { pathname: '/' } }
  const { t } = props
  if (redirectToReferrer) return <Navigate to={from} replace />
  return (
    <>
      <Col lg="5" md="7">
        <Card className="bg-secondary shadow border-0">
          <CardHeader className="bg-transparent pb-5">
            <div className="text-muted text-center mt-2 mb-3">
              <small>{t('Sign in credentials')}</small>
            </div>
          </CardHeader>
          <CardBody className="px-lg-5 py-lg-5">
            <Form role="form">
              <FormGroup
                className={
                  emailError === null
                    ? ''
                    : emailError
                      ? 'has-success'
                      : 'has-danger'
                }>
                <InputGroup className="input-group-alternative">
                  <InputGroupAddon addonType="prepend">
                    <InputGroupText>
                      <i className="ni ni-email-83" />
                    </InputGroupText>
                  </InputGroupAddon>
                  <Input
                    value={email}
                    onChange={event => {
                      setEmail(event.target.value)
                      setError(null)
                    }}
                    onBlur={event => {
                      onBlur(event, 'email')
                    }}
                    placeholder="Email"
                    type="email"
                  />
                </InputGroup>
              </FormGroup>
              <FormGroup
                className={
                  passwordError === null
                    ? ''
                    : passwordError
                      ? 'has-success'
                      : 'has-danger'
                }>
                <InputGroup className="input-group-alternative">
                  <InputGroupAddon addonType="prepend">
                    <InputGroupText>
                      <i className="ni ni-lock-circle-open" />
                    </InputGroupText>
                  </InputGroupAddon>
                  <Input
                    value={password}
                    onChange={event => {
                      setPassword(event.target.value)
                      setError(null)
                    }}
                    onBlur={event => {
                      onBlur(event, 'password')
                    }}
                    placeholder="Password"
                    type="password"
                  />
                </InputGroup>
              </FormGroup>

              <div className="text-center">
                <Mutation
                  mutation={LOGIN}
                  onCompleted={data => {
                    localStorage.setItem(
                      'user-pikupo',
                      JSON.stringify(data.adminLogin)
                    )
                    setRedirectToReferrer(true)
                    setEmailError(null)
                    setPasswordError(null)
                  }}
                  onError={error => {
                    setEmailError(null)
                    setPasswordError(null)
                    setError(error.graphQLErrors[0].message)
                  }}>
                  {(adminLogin, { loading, error }) => {
                    return (
                      <Button
                        className="my-4"
                        color="primary"
                        type="button"
                        onClick={() => {
                          setEmailError(null)
                          setPasswordError(null)
                          if (validate()) {
                            adminLogin({ variables: { password, email } })
                          }
                        }}>
                        {t('Sign in')}
                      </Button>
                    )
                  }}
                </Mutation>
              </div>
              {error && (
                <UncontrolledAlert color="danger" fade={true}>
                  <span className="alert-inner--text">{error}</span>
                </UncontrolledAlert>
              )}
            </Form>
          </CardBody>
        </Card>
      </Col>
    </>
  )
}

export default withTranslation()(Login)
