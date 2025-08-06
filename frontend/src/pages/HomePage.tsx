import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../services/api'

export default function HomePage() {
  const { data: stations, isLoading: stationsLoading } = useQuery({
    queryKey: ['stations', 'all'],
    queryFn: () => apiClient.getAllStations(),
  })

  const { data: bikes, isLoading: bikesLoading } = useQuery({
    queryKey: ['bikes'],
    queryFn: () => apiClient.getAllBikes(),
  })

  if (stationsLoading || bikesLoading) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  const totalBikes = stations?.reduce((sum, station) => sum + station.bike_count, 0) || 0
  const activeStations = stations?.length || 0
  const totalTrips = bikes?.reduce((sum, bike) => sum + bike.total_trips, 0) || 0
  const totalDistance = bikes?.reduce((sum, bike) => sum + bike.total_distance_km, 0) || 0

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="border-4 border-dashed border-gray-200 rounded-lg p-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Welcome to molbubi.info
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Real-time bike sharing system monitoring for Budapest
          </p>

          {/* Stats */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8">
            <div className="bg-white rounded-lg shadow px-6 py-4">
              <div className="text-2xl font-bold text-primary-600">{totalBikes}</div>
              <div className="text-sm text-gray-500">Bikes Available</div>
            </div>
            <div className="bg-white rounded-lg shadow px-6 py-4">
              <div className="text-2xl font-bold text-primary-600">{activeStations}</div>
              <div className="text-sm text-gray-500">Active Stations</div>
            </div>
            <div className="bg-white rounded-lg shadow px-6 py-4">
              <div className="text-2xl font-bold text-primary-600">{totalTrips.toLocaleString()}</div>
              <div className="text-sm text-gray-500">Total Trips</div>
            </div>
            <div className="bg-white rounded-lg shadow px-6 py-4">
              <div className="text-2xl font-bold text-primary-600">{Math.round(totalDistance).toLocaleString()} km</div>
              <div className="text-sm text-gray-500">Distance Traveled</div>
            </div>
          </div>

          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-gray-900">Quick Navigation</h2>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <a 
                href="/stations"
                className="bg-primary-500 text-white px-6 py-3 rounded-lg hover:bg-primary-600 transition-colors"
              >
                View Stations
              </a>
              <a 
                href="/bikes"
                className="bg-primary-500 text-white px-6 py-3 rounded-lg hover:bg-primary-600 transition-colors"
              >
                Track Bikes
              </a>
              <a 
                href="/distribution"
                className="bg-primary-500 text-white px-6 py-3 rounded-lg hover:bg-primary-600 transition-colors"
              >
                Distribution Map
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
