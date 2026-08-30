import React, { useRef, useEffect } from 'react'
import { Routes, Route, useLocation } from 'react-router-dom'
// reactstrap components
import { Container } from 'reactstrap'
// core components
import AdminNavbar from '../components/Navbars/AdminNavbar.jsx'
import AdminFooter from '../components/Footers/AdminFooter.jsx'
import Sidebar from '../components/Sidebar/Sidebar.jsx'

import routes from './../routes.js'
import logo from '../assets/img/brand/logo.png'

const Admin = () => {
  const location = useLocation()
  var divRef = useRef(null)
  useEffect(() => {
    document.documentElement.scrollTop = 0
    document.scrollingElement.scrollTop = 0
    divRef.current.scrollTop = 0
  }, [])
  function getRoutes(routes) {
    return routes.map((prop, key) => {
      if (prop.layout === '/admin') {
        const Component = prop.component
        return (
          <Route path={prop.path.slice(1)} element={<Component />} key={key} />
        )
      }
      return null
    })
  }
  function getBrandText(pathname) {
    for (let i = 0; i < routes.length; i++) {
      if (pathname.indexOf(routes[i].layout + routes[i].path) !== -1) {
        return routes[i].name
      }
    }
    return 'Brand'
  }
  return (
    <>
      <Sidebar
        routes={routes}
        logo={{
          innerLink: '/admin/dashboard',
          imgSrc: logo,
          imgAlt: '...'
        }}
      />
      <div className="main-content" ref={divRef}>
        <AdminNavbar brandText={getBrandText(location.pathname)} />
        <Routes>{getRoutes(routes)}</Routes>
        <Container fluid>
          <AdminFooter />
        </Container>
      </div>
    </>
  )
}
export default Admin
