/* eslint-disable react/display-name */
import React, { useState } from 'react'
import { withTranslation } from 'react-i18next'
import {
  Container,
  Row,
  Card,
  Button,
  FormGroup,
  Input,
  Label
} from 'reactstrap'
import Header from '../components/Headers/Header.jsx'
import { Query, Mutation } from '@apollo/client/react/components'
import { gql } from '@apollo/client'
import { adminStaffs, createAdminStaff, deleteAdminStaff } from '../apollo/server'

const STAFFS = gql`
  ${adminStaffs}
`
const CREATE = gql`
  ${createAdminStaff}
`
const DELETE = gql`
  ${deleteAdminStaff}
`

function Staff(props) {
  const { t } = props
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [error, setError] = useState(null)

  return (
    <>
      <Header />
      <Container className="mt--7" fluid>
        <Row>
          <div className="col">
            <Card className="shadow p-4">
              <h3>{t('Add Staff')}</h3>
              <p className="text-muted">
                Staff can only manage orders. Payment keys stay with the
                director.
              </p>
              {error ? <div className="text-danger mb-2">{error}</div> : null}
              <FormGroup>
                <Label>{t('Name')}</Label>
                <Input value={name} onChange={e => setName(e.target.value)} />
              </FormGroup>
              <FormGroup>
                <Label>{t('Email')}</Label>
                <Input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                />
              </FormGroup>
              <FormGroup>
                <Label>{t('Password')}</Label>
                <Input
                  type="password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                />
              </FormGroup>
              <Mutation
                mutation={CREATE}
                refetchQueries={[{ query: STAFFS }]}
                onCompleted={() => {
                  setEmail('')
                  setPassword('')
                  setName('')
                  setError(null)
                }}
                onError={err => {
                  setError(
                    (err.graphQLErrors && err.graphQLErrors[0]?.message) ||
                      err.message
                  )
                }}
              >
                {(create, { loading }) => (
                  <Button
                    color="primary"
                    disabled={loading}
                    onClick={() => {
                      if (!email || !password) {
                        setError(t('Check your email and password'))
                        return
                      }
                      create({
                        variables: { email, password, name: name || 'Staff' }
                      })
                    }}
                  >
                    {t('Add Staff')}
                  </Button>
                )}
              </Mutation>

              <hr />
              <Query query={STAFFS}>
                {({ loading, error: qErr, data }) => {
                  if (loading) return <div>{t('Loading')}...</div>
                  if (qErr) return <div>{t('Error')}: {qErr.message}</div>
                  const rows = data?.adminStaffs || []
                  return (
                    <table className="table">
                      <thead>
                        <tr>
                          <th>{t('Name')}</th>
                          <th>{t('Email')}</th>
                          <th>{t('Role')}</th>
                          <th />
                        </tr>
                      </thead>
                      <tbody>
                        {rows.map(row => (
                          <tr key={row._id}>
                            <td>{row.name}</td>
                            <td>{row.email}</td>
                            <td>{row.role}</td>
                            <td>
                              <Mutation
                                mutation={DELETE}
                                refetchQueries={[{ query: STAFFS }]}
                              >
                                {(del, { loading: delLoading }) => (
                                  <Button
                                    color="danger"
                                    size="sm"
                                    disabled={delLoading}
                                    onClick={() =>
                                      del({ variables: { id: row._id } })
                                    }
                                  >
                                    {t('Delete')}
                                  </Button>
                                )}
                              </Mutation>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )
                }}
              </Query>
            </Card>
          </div>
        </Row>
      </Container>
    </>
  )
}

export default withTranslation()(Staff)
