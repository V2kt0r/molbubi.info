import { Routes, Route } from 'react-router-dom'
import Layout from '@/components/Layout'
import HomePage from '@/pages/HomePage'
import StationsPage from '@/pages/StationsPage'
import BikesPage from '@/pages/BikesPage'
import DistributionPage from '@/pages/DistributionPage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/stations" element={<StationsPage />} />
        <Route path="/bikes" element={<BikesPage />} />
        <Route path="/distribution" element={<DistributionPage />} />
      </Routes>
    </Layout>
  )
}

export default App