/* eslint-disable react/display-name */
import React, { useState } from 'react'
import { withTranslation } from 'react-i18next'
import {
  Container,
  Row,
  Card,
  CardHeader,
  CardBody,
  Button,
  FormGroup,
  Input,
  Label,
  Badge
} from 'reactstrap'
import Header from '../components/Headers/Header.jsx'
import { Query, Mutation } from '@apollo/client/react/components'
import { gql } from '@apollo/client'
import {
  restaurants,
  createRestaurant,
  createRestaurantDirector,
  setRestaurantActive
} from '../apollo/server'

const RESTAURANTS = gql`
  ${restaurants}
`
const CREATE_RESTAURANT = gql`
  ${createRestaurant}
`
const CREATE_DIRECTOR = gql`
  ${createRestaurantDirector}
`
const SET_ACTIVE = gql`
  ${setRestaurantActive}
`

const emptyForm = {
  name: '',
  slug: '',
  directorName: '',
  directorEmail: '',
  directorPassword: ''
}

// The slug is the value baked into a client's mobile build, so it has to be
// URL-safe and stable: derived from the name, lowercase, no punctuation.
function slugify(value) {
  return (value || '')
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

function Restaurants(props) {
  const { t } = props
  const [form, setForm] = useState(emptyForm)
  const [error, setError] = useState(null)
  const [created, setCreated] = useState(null)
  const [directorFor, setDirectorFor] = useState(null)
  const [director, setDirector] = useState({ email: '', password: '', name: '' })

  const update = (field, value) =>
    setForm(prev => ({ ...prev, [field]: value }))

  return (
    <>
      <Header />
      <Container className="mt--7" fluid>
        <Row>
          <div className="col">
            <Card className="shadow">
              <CardHeader className="border-0">
                <h3 className="mb-0">{t('Restaurants')}</h3>
                <p className="text-muted mb-0">
                  {t(
                    'Every restaurant is one mobile build. The slug below is the value baked into that build.'
                  )}
                </p>
                {created ? (
                  <div className="alert alert-success mt-3 mb-0">
                    {t('Restaurant created')}: <strong>{created.name}</strong> —{' '}
                    {t('Slug')} <code>{created.slug}</code>.{' '}
                    {t(
                      'Build the client app with RESTAURANT_SLUG set to this value.'
                    )}
                  </div>
                ) : null}
              </CardHeader>
              <CardBody>
                <Query query={RESTAURANTS} fetchPolicy="cache-and-network">
                  {({ loading, error: qErr, data }) => {
                    if (loading && !data) {
                      return <div>{t('Loading')}...</div>
                    }
                    if (qErr) {
                      return (
                        <div className="text-danger">
                          {t('Error')}: {qErr.message}
                        </div>
                      )
                    }
                    const rows = data?.restaurants || []
                    if (!rows.length) {
                      return <p>{t('No restaurants yet')}</p>
                    }
                    return (
                      <div className="table-responsive">
                        <table className="table align-items-center">
                          <thead>
                            <tr>
                              <th>{t('Name')}</th>
                              <th>{t('Slug')}</th>
                              <th>{t('Status')}</th>
                              <th className="text-right">{t('Actions')}</th>
                            </tr>
                          </thead>
                          <tbody>
                            {rows.map(row => (
                              <React.Fragment key={row._id}>
                                <tr>
                                  <td>{row.name}</td>
                                  <td>
                                    <code>{row.slug}</code>
                                  </td>
                                  <td>
                                    <Badge
                                      color={
                                        row.is_active ? 'success' : 'secondary'
                                      }>
                                      {row.is_active
                                        ? t('Active')
                                        : t('Inactive')}
                                    </Badge>
                                  </td>
                                  <td className="text-right">
                                    <Button
                                      size="sm"
                                      color="info"
                                      onClick={() =>
                                        setDirectorFor(
                                          directorFor === row._id
                                            ? null
                                            : row._id
                                        )
                                      }>
                                      {t('Set director')}
                                    </Button>{' '}
                                    <Mutation
                                      mutation={SET_ACTIVE}
                                      refetchQueries={[{ query: RESTAURANTS }]}>
                                      {(setActive, { loading: busy }) => (
                                        <Button
                                          size="sm"
                                          color={
                                            row.is_active ? 'danger' : 'success'
                                          }
                                          disabled={busy}
                                          onClick={() =>
                                            setActive({
                                              variables: {
                                                id: row._id,
                                                isActive: !row.is_active
                                              }
                                            })
                                          }>
                                          {row.is_active
                                            ? t('Deactivate')
                                            : t('Activate')}
                                        </Button>
                                      )}
                                    </Mutation>
                                  </td>
                                </tr>
                                {directorFor === row._id ? (
                                  <tr>
                                    <td colSpan="4" className="bg-light">
                                      <Row>
                                        <div className="col-md-4">
                                          <FormGroup>
                                            <Label>{t('Director name')}</Label>
                                            <Input
                                              value={director.name}
                                              onChange={e =>
                                                setDirector(prev => ({
                                                  ...prev,
                                                  name: e.target.value
                                                }))
                                              }
                                            />
                                          </FormGroup>
                                        </div>
                                        <div className="col-md-4">
                                          <FormGroup>
                                            <Label>
                                              {t('Director email')}
                                            </Label>
                                            <Input
                                              type="email"
                                              value={director.email}
                                              onChange={e =>
                                                setDirector(prev => ({
                                                  ...prev,
                                                  email: e.target.value
                                                }))
                                              }
                                            />
                                          </FormGroup>
                                        </div>
                                        <div className="col-md-4">
                                          <FormGroup>
                                            <Label>
                                              {t('Director password')}
                                            </Label>
                                            <Input
                                              type="password"
                                              value={director.password}
                                              onChange={e =>
                                                setDirector(prev => ({
                                                  ...prev,
                                                  password: e.target.value
                                                }))
                                              }
                                            />
                                          </FormGroup>
                                        </div>
                                      </Row>
                                      <Mutation
                                        mutation={CREATE_DIRECTOR}
                                        refetchQueries={[
                                          { query: RESTAURANTS }
                                        ]}
                                        onCompleted={() => {
                                          setDirectorFor(null)
                                          setDirector({
                                            email: '',
                                            password: '',
                                            name: ''
                                          })
                                          setError(null)
                                        }}
                                        onError={err => {
                                          setError(
                                            err.graphQLErrors?.[0]?.message ||
                                              err.message
                                          )
                                        }}>
                                        {(createDirector, { loading: busy }) => (
                                          <Button
                                            color="primary"
                                            disabled={
                                              busy ||
                                              !director.email ||
                                              !director.password
                                            }
                                            onClick={() =>
                                              createDirector({
                                                variables: {
                                                  restaurantId: row._id,
                                                  email: director.email,
                                                  password: director.password,
                                                  name:
                                                    director.name ||
                                                    t('Director')
                                                }
                                              })
                                            }>
                                            {t('Save director')}
                                          </Button>
                                        )}
                                      </Mutation>
                                      {error ? (
                                        <div className="text-danger mt-2">
                                          {error}
                                        </div>
                                      ) : null}
                                    </td>
                                  </tr>
                                ) : null}
                              </React.Fragment>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )
                  }}
                </Query>
              </CardBody>
            </Card>

            <Card className="shadow mt-4">
              <CardHeader className="border-0">
                <h3 className="mb-0">{t('Add Restaurant')}</h3>
                <p className="text-muted mb-0">
                  {t(
                    'The director account is created together with the restaurant and can change its password afterwards.'
                  )}
                </p>
              </CardHeader>
              <CardBody>
                {error ? <div className="text-danger mb-2">{error}</div> : null}
                <Row>
                  <div className="col-md-6">
                    <FormGroup>
                      <Label>{t('Name')}</Label>
                      <Input
                        value={form.name}
                        onChange={e => {
                          const name = e.target.value
                          setForm(prev => ({
                            ...prev,
                            name,
                            // Keep the slug in step with the name until the
                            // operator edits it by hand.
                            slug:
                              prev.slug === '' || prev.slug === slugify(prev.name)
                                ? slugify(name)
                                : prev.slug
                          }))
                        }}
                      />
                    </FormGroup>
                  </div>
                  <div className="col-md-6">
                    <FormGroup>
                      <Label>{t('Slug')}</Label>
                      <Input
                        value={form.slug}
                        placeholder="client-slug"
                        onChange={e => update('slug', slugify(e.target.value))}
                      />
                    </FormGroup>
                  </div>
                  <div className="col-md-4">
                    <FormGroup>
                      <Label>{t('Director name')}</Label>
                      <Input
                        value={form.directorName}
                        onChange={e =>
                          update('directorName', e.target.value)
                        }
                      />
                    </FormGroup>
                  </div>
                  <div className="col-md-4">
                    <FormGroup>
                      <Label>{t('Director email')}</Label>
                      <Input
                        type="email"
                        value={form.directorEmail}
                        onChange={e =>
                          update('directorEmail', e.target.value)
                        }
                      />
                    </FormGroup>
                  </div>
                  <div className="col-md-4">
                    <FormGroup>
                      <Label>{t('Director password')}</Label>
                      <Input
                        type="password"
                        value={form.directorPassword}
                        onChange={e =>
                          update('directorPassword', e.target.value)
                        }
                      />
                    </FormGroup>
                  </div>
                </Row>
                <Mutation
                  mutation={CREATE_RESTAURANT}
                  refetchQueries={[{ query: RESTAURANTS }]}
                  onCompleted={data => {
                    setCreated(data.createRestaurant)
                    setForm(emptyForm)
                    setError(null)
                  }}
                  onError={err => {
                    setCreated(null)
                    setError(
                      err.graphQLErrors?.[0]?.message || err.message
                    )
                  }}>
                  {(create, { loading }) => (
                    <Button
                      color="primary"
                      disabled={loading}
                      onClick={() => {
                        if (
                          !form.name ||
                          !form.slug ||
                          !form.directorEmail ||
                          !form.directorPassword
                        ) {
                          setCreated(null)
                          setError(t('Fill in every field'))
                          return
                        }
                        create({
                          variables: {
                            name: form.name,
                            slug: form.slug,
                            directorEmail: form.directorEmail,
                            directorPassword: form.directorPassword,
                            directorName: form.directorName || t('Director')
                          }
                        })
                      }}>
                      {t('Create')}
                    </Button>
                  )}
                </Mutation>
              </CardBody>
            </Card>
          </div>
        </Row>
      </Container>
    </>
  )
}

export default withTranslation()(Restaurants)
