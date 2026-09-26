import React, { useRef, useEffect } from 'react'
import { Routes, Route, useLocation, Navigate } from 'react-router-dom'
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
  // Reset the scroll position on every navigation. The ref is attached to the
  // content wrapper below, which is *not* rendered while the redirect branch is
  // active; a plain `divRef.current.scrollTop` therefore threw
  // "Cannot set properties of null" on mount and unmounted the whole tree
  // (blank screen). Guard the refs and re-run when the route changes.
  useEffect(() => {
    document.documentElement.scrollTop = 0
    if (document.scrollingElement) {
      document.scrollingElement.scrollTop = 0
    }
    if (divRef.current) {
      divRef.current.scrollTop = 0
    }
  }, [location.pathname])
  // The platform owner has no restaurant, so every tenant-scoped screen would
  // fail for them ("Restaurant context required"). Tenant management is the one
  // screen that works, so send them there instead of showing broken widgets.
  const role = (() => {
    try {
      return JSON.parse(localStorage.getItem('user-pikupo') || '{}').role
    } catch (e) {
      return undefined
    }
  })()
  if (role === 'superadmin' && location.pathname !== '/admin/restaurants') {
    return <Navigate to="/admin/restaurants" replace />
  }
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
