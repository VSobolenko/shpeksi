import Nav from './components/Nav/Nav.jsx'
import Hero from './components/Hero/Hero.jsx'
import HowItWorks from './components/HowItWorks/HowItWorks.jsx'
import Features from './components/Features/Features.jsx'
import MenuShowcase from './components/MenuShowcase/MenuShowcase.jsx'
import About from './components/About/About.jsx'
import Faq from './components/Faq/Faq.jsx'
import Contact from './components/Contact/Contact.jsx'
import Download from './components/Download/Download.jsx'
import Footer from './components/Footer/Footer.jsx'

export default function App() {
  return (
    <>
      <Nav />
      <main>
        <Hero />
        <HowItWorks />
        <Features />
        <MenuShowcase />
        <About />
        <Faq />
        <Contact />
        <Download />
      </main>
      <Footer />
    </>
  )
}
