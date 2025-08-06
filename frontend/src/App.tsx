import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import StationsPage from './pages/StationsPage'
import StationDetailPage from './pages/StationDetailPage'
import BikesPage from './pages/BikesPage'
import DistributionPage from './pages/DistributionPage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/stations" element={<StationsPage />} />
        <Route path="/stations/:stationId" element={<StationDetailPage />} />
        <Route path="/bikes" element={<BikesPage />} />
        <Route path="/distribution" element={<DistributionPage />} />
      </Routes>
    </Layout>
  )
}

export default App