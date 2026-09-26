/* eslint-disable react/display-name */
import React, { useState } from 'react'
import { Badge, Container, Row, Card, Modal } from 'reactstrap'
import Header from '../components/Headers/Header.jsx'
import OptionComponent from '../components/Option/Option'
import CustomLoader from '../components/Loader/CustomLoader'
import DataTable from 'react-data-table-component'
import orderBy from 'lodash/orderBy'

import { withTranslation } from 'react-i18next'
import { Query, Mutation } from '@apollo/client/react/components'
import { options, deleteOption } from '../apollo/server'
import { gql } from '@apollo/client'
import Loader from 'react-loader-spinner'
import Alert from '../components/Alert'

const GET_OPTIONS = gql`
  ${options}
`
const DELETE_OPTION = gql`
  ${deleteOption}
`

const Option = props => {
  const { t } = props
  const [editModal, setEditModal] = useState(false)
  const [option, setOption] = useState(null)
  const [alert, setAlert] = useState(null)

  const showAlert = (message, severity) => {
    setAlert({ message, severity })
    setTimeout(() => setAlert(null), 2500)
  }

  const toggleModal = option => {
    setEditModal(!editModal)
    setOption(option)
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
      name: t('Title'),
      sortable: true,
      selector: 'title'
    },
    {
      name: t('Description'),
      sortable: true,
      selector: 'description'
    },
    {
      name: t('Price'),
      sortable: true,
      selector: 'price'
    },
    {
      name: t('Actions'),
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
          mutation={DELETE_OPTION}
          refetchQueries={[{ query: GET_OPTIONS, variables: { page: 0 } }]}>
          {(deleteOption, { loading: deleteLoading }) => {
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
              <Badge
                href="#pablo"
                color="danger"
                onClick={e => {
                  e.preventDefault()
                  if (!window.confirm(`${t('Delete')} "${row.title}"? ${t('This cannot be undone.')}`)) {
                    return
                  }
                  deleteOption({ variables: { id: row._id } })
                    .then(() => showAlert(t('Deleted'), 'success'))
                    .catch(() => showAlert(t('Could not delete. Please try again.'), 'danger'))
                }}>
                {t('Delete')}
              </Badge>
            )
          }}
        </Mutation>
      </>
    )
  }

  return (
    <>
      <Header />
      {/* Page content */}
      <Container className="mt--7" fluid>
        <OptionComponent
          refetchQueries={[{ query: GET_OPTIONS, variables: { page: 0 } }]}
        />
        <Row className="mt-5">
          <div className="col">
            <Card className="shadow">
              {alert && (
                <Alert message={alert.message} severity={alert.severity} />
              )}
              <Query query={GET_OPTIONS} variables={{ page: 0 }}>
                {({ loading, error, data }) => {
                  if (error) {
                    return (
                      <tr>
                        <td>
                          {t('Error')}! {error.message}
                        </td>
                      </tr>
                    )
                  }
                  return (
                    <DataTable
                      title={t('Options')}
                      columns={columns}
                      data={data && data.allOptions ? data.allOptions : []}
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
          <OptionComponent
            option={option}
            refetchQueries={[{ query: GET_OPTIONS, variables: { page: 0 } }]}
          />
        </Modal>
      </Container>
    </>
  )
}

export default withTranslation()(Option)
