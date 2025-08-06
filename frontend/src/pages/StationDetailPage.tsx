import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../services/api'
import BikeCard from '../components/BikeCard'

export default function StationDetailPage() {
  const { stationId } = useParams<{ stationId: string }>()
  const stationIdNum = stationId ? parseInt(stationId) : null

  // Get station details
  const { data: station, isLoading: stationLoading, error: stationError } = useQuery({
    queryKey: ['station', stationIdNum],
    queryFn: () => stationIdNum ? apiClient.getStation(stationIdNum) : null,
    enabled: !!stationIdNum,
  })

  // Get bikes at this station
  const { data: bikeNumbers, isLoading: bikesLoading, error: bikesError } = useQuery({
    queryKey: ['station-bikes', stationIdNum],
    queryFn: () => stationIdNum ? apiClient.getBikesAtStation(stationIdNum) : null,
    enabled: !!stationIdNum,
  })

  // Get all bikes data to match with bike numbers at station
  const { data: allBikes, isLoading: allBikesLoading } = useQuery({
    queryKey: ['bikes', 'all'],
    queryFn: () => apiClient.getAllBikes(),
  })

  // Filter bikes data to only show bikes currently at this station
  const stationBikes = allBikes?.filter(bike => 
    bikeNumbers?.includes(bike.bike_number)
  ) || []

  const isLoading = stationLoading || bikesLoading || allBikesLoading
  const error = stationError || bikesError

  if (!stationIdNum) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="text-red-800">Invalid station ID</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <Link
          to="/stations"
          className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 mb-6"
        >
          ← Back to Stations
        </Link>
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="text-red-800">
            Error loading station: {error instanceof Error ? error.message : 'Unknown error'}
          </div>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <Link
          to="/stations"
          className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 mb-6"
        >
          ← Back to Stations
        </Link>
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/3"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-24 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      {/* Back navigation */}
      <Link
        to="/stations"
        className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 mb-6"
      >
        ← Back to Stations
      </Link>

      {/* Station info */}
      {station && (
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{station.name}</h1>
          <div className="text-gray-600 space-y-1">
            <p>Station ID: {station.uid}</p>
            <p>Location: {station.lat.toFixed(6)}, {station.lng.toFixed(6)}</p>
            <p className="text-primary-600 font-medium">
              {bikeNumbers?.length !== undefined ? `${bikeNumbers.length} bikes available` : 'Loading bike count...'}
            </p>
          </div>
        </div>
      )}

      {/* Bikes at station */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Bikes at This Station ({stationBikes.length})
        </h2>

        {stationBikes.length > 0 ? (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {stationBikes.map((bike) => (
                <li key={bike.bike_number}>
                  <BikeCard bike={bike} />
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <div className="text-center py-12 bg-gray-50 rounded-lg">
            <div className="text-gray-500">
              {bikeNumbers?.length === 0 
                ? "No bikes currently at this station" 
                : "Loading bike details..."}
            </div>
          </div>
        )}
      </div>

      {/* Additional info */}
      {bikeNumbers && bikeNumbers.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
          <div className="text-blue-800 text-sm">
            <strong>Note:</strong> This shows bikes currently stationed here. 
            Total statistics include the bike's full history across all stations.
          </div>
        </div>
      )}
    </div>
  )
}