/* eslint-disable react/display-name */
import React, { useState } from 'react'
import { gql } from '@apollo/client'
import { Query, Mutation } from '@apollo/client/react/components'
import { withTranslation } from 'react-i18next'
import CategoryComponent from '../components/Category/Category'
import CustomLoader from '../components/Loader/CustomLoader'
// reactstrap components
import { Badge, Card, Container, Row, Modal } from 'reactstrap'
// core components
import Header from '../components/Headers/Header.jsx'
import { categories, deleteCategory, getFoods } from '../apollo/server'
import DataTable from 'react-data-table-component'
import orderBy from 'lodash/orderBy'
import Loader from 'react-loader-spinner'
import Alert from '../components/Alert'

const GET_CATEGORIES = gql`
  ${categories}
`
const DELETE_CATEGORY = gql`
  ${deleteCategory}
`
const GET_FOODS = gql`
  ${getFoods}
`

const Category = props => {
  const { t } = props
  const [editModal, setEditModal] = useState(false)
  const [category, setCategory] = useState(null)
  const [alert, setAlert] = useState(null)

  const showAlert = (message, severity) => {
    setAlert({ message, severity })
    setTimeout(() => setAlert(null), 2500)
  }

  const toggleModal = category => {
    setEditModal(!editModal)
    setCategory(category)
  }

  const customSort = (rows, field, direction) => {
    const handleField = row => {
      if (row[field]) {
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
      name: t('Image'),
      cell: row => (
        <>
          {!!row.img_menu && (
            <img className="img-responsive" src={row.img_menu} alt="img menu" />
          )}
          {!row.img_menu && t('No Image')}
        </>
      )
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
          mutation={DELETE_CATEGORY}
          refetchQueries={[
            { query: GET_CATEGORIES, variables: { page: 0 } },
            { query: GET_FOODS, variables: { page: 0 } }
          ]}>
          {(deleteCategory, { loading: deleteLoading }) => {
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
                  deleteCategory({ variables: { id: row._id } })
                    .then(() => showAlert(t('Deleted'), 'success'))
                    .catch(err => {
                      // The API refuses to delete a category that still has
                      // foods; show why instead of a generic failure.
                      const code = err?.graphQLErrors?.[0]?.extensions?.code
                      showAlert(
                        code === 'CATEGORY_NOT_EMPTY'
                          ? t(
                            'This category still has items. Remove or move them first.'
                          )
                          : t('Could not delete. Please try again.'),
                        'danger'
                      )
                    })
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
        <CategoryComponent />
        {/* Table */}
        <Row className="mt-5">
          <div className="col">
            <Card className="shadow">
              {alert && (
                <Alert message={alert.message} severity={alert.severity} />
              )}
              <Query query={GET_CATEGORIES} variables={{ page: 0 }}>
                {({ loading, error, data }) => {
                  if (error) {
                    return (
                      <span>
                        {t('Error')}! {error.message}
                      </span>
                    )
                  }
                  return (
                    <DataTable
                      title={t('Categories')}
                      columns={columns}
                      data={data && data.categories ? data.categories : []}
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
            toggleModal(null)
          }}>
          <CategoryComponent category={category} />
        </Modal>
      </Container>
    </>
  )
}
export default withTranslation()(Category)
