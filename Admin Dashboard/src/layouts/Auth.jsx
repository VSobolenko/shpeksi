import React, { useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
// reactstrap components
import { Container, Row } from 'reactstrap'

// core components
import AuthNavbar from '../components/Navbars/AuthNavbar.jsx'
import AuthFooter from '../components/Footers/AuthFooter.jsx'

import routes from '../routes.js'

function Auth() {
  useEffect(() => {
    document.body.classList.add('bg-default')
    return () => {
      document.body.classList.remove('bg-default')
    }
  }, [])
  function getRoutes(routes) {
    return routes.map((prop, key) => {
      if (prop.layout === '/auth') {
        const Component = prop.component
        return (
          <Route path={prop.path.slice(1)} element={<Component />} key={key} />
        )
      }
      return null
    })
  }
  return (
    <>
      <div className="main-content">
        <AuthNavbar />
        <div className="header bg-gradient-warning py-7 py-lg-8">
          <div className="separator separator-bottom separator-skew zindex-100">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              preserveAspectRatio="none"
              version="1.1"
              viewBox="0 0 2560 100"
              x="0"
              y="0">
              <polygon
                className="fill-default"
                points="2560 0 2560 100 0 100"
              />
            </svg>
          </div>
        </div>
        {/* Page content */}
        <Container className="mt--8 pb-5">
          <Row className="justify-content-center">
            <Routes>{getRoutes(routes)}</Routes>
          </Row>
        </Container>
      </div>
      <AuthFooter />
    </>
  )
}

export default Auth
