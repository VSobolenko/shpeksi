/* eslint-disable react/display-name */
import React, { useState } from 'react'
import { Container, Badge, Row, Card, Modal } from 'reactstrap'
import Header from '../components/Headers/Header.jsx'
import AddonComponent from '../components/Addon/Addon'
import { addons, deleteAddon } from '../apollo/server'
import CustomLoader from '../components/Loader/CustomLoader'
import DataTable from 'react-data-table-component'
import orderBy from 'lodash/orderBy'
import { withTranslation } from 'react-i18next'
import { gql } from '@apollo/client'
import { Query, Mutation } from '@apollo/client/react/components'
import Loader from 'react-loader-spinner'
import Alert from '../components/Alert'

const GET_ADDONS = gql`
  ${addons}
`
const DELETE_ADDON = gql`
  ${deleteAddon}
`

const Addon = props => {
  const [addon, setAddon] = useState(null)
  const [editModal, setEditModal] = useState(false)
  const [alert, setAlert] = useState(null)

  const showAlert = (message, severity) => {
    setAlert({ message, severity })
    setTimeout(() => setAlert(null), 2500)
  }

  const toggleModal = addon => {
    setEditModal(!editModal)
    setAddon(addon)
  }

  const customSort = (rows, field, direction) => {
    const handleField = row => {
      if (row[field] && isNaN(row[field])) {
        return row[field].toLowerCase()
      }

      return row[field]
    }

    return orderBy(rows, handleField, direction)
  }

  const handleSort = (column, sortDirection) =>
    console.log(column.selector, sortDirection)

  const columns = [
    {
      name: 'Title',
      sortable: true,
      selector: 'title'
    },
    {
      name: 'Description',
      sortable: true,
      selector: 'description'
    },
    {
      name: 'Minimum',
      sortable: true,
      selector: 'quantity_minimum'
    },
    {
      name: 'Maximum',
      sortable: true,
      selector: 'quantity_maximum'
    },
    {
      name: 'Action',
      cell: row => <>{actionButtons(row)}</>
    }
  ]

  const actionButtons = row => {
    return (
      <>
        <Badge
          href="#pablo"
          onClick={e => {
            e.preventDefault()
            toggleModal(row)
          }}
          color="primary">
          Edit
        </Badge>
        &nbsp;&nbsp;
        <Mutation
          mutation={DELETE_ADDON}
          refetchQueries={[{ query: GET_ADDONS, variables: { page: 0 } }]}>
          {(deleteAddon, { loading: deleteLoading }) => {
            if (deleteLoading) {
              return (
                <Loader
                  type="ThreeDots"
                  color="#BB2124"
                  height={20}
                  width={40}
                  visible={deleteLoading}
                />
              )
            }
            return (
              <>
                <Badge
                  href="#pablo"
                  color="danger"
                  onClick={e => {
                    e.preventDefault()
                    if (!window.confirm(`${t('Delete')} "${row.title}"? ${t('This cannot be undone.')}`)) {
                      return
                    }
                    deleteAddon({ variables: { id: row._id } })
                      .then(() => showAlert(t('Deleted'), 'success'))
                      .catch(() => showAlert(t('Could not delete. Please try again.'), 'danger'))
                  }}>
                  {t('Delete')}
                </Badge>
              </>
            )
          }}
        </Mutation>
      </>
    )
  }

  const { t } = props
  return (
    <>
      <Header />
      {/* Page content */}
      <Container className="mt--7" fluid>
        <AddonComponent
          refetchQueries={[{ query: GET_ADDONS, variables: { page: 0 } }]}
        />
        <Row className="mt-5">
          <div className="col">
            <Card className="shadow">
              {alert && (
                <Alert message={alert.message} severity={alert.severity} />
              )}
              <Query query={GET_ADDONS} variables={{ page: 0 }}>
                {({ loading, error, data }) => {
                  if (error) {
                    return (
                      <tr>
                        <td>
                          `${t('Error')}! ${error.message}`
                        </td>
                      </tr>
                    )
                  }
                  return (
                    <DataTable
                      title={t('Addons')}
                      columns={columns}
                      data={data && data.allAddons ? data.allAddons : []}
                      pagination
                      progressPending={loading}
                      progressComponent={<CustomLoader />}
                      onSort={handleSort}
                      sortFunction={customSort}
                      defaultSortField="title"
                    />
                  )
                }}
              </Query>
            </Card>
          </div>
        </Row>
        <Modal
          className="modal-dialog-centered"
          size="lg"
          isOpen={editModal}
          toggle={() => {
            toggleModal()
          }}>
          <AddonComponent
            addon={addon}
            refetchQueries={[{ query: GET_ADDONS, variables: { page: 0 } }]}
          />
        </Modal>
      </Container>
    </>
  )
}

export default withTranslation()(Addon)
