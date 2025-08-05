import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/services/api'

export default function StationsPage() {
  const { data: stations, isLoading, error } = useQuery({
    queryKey: ['stations', 'all'],
    queryFn: () => apiClient.getAllStations(),
  })

  if (isLoading) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          {[...Array(8)].map((_, i) => (
            <div key={i} className="h-16 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="text-red-800">
            Error loading stations: {error instanceof Error ? error.message : 'Unknown error'}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Bike Stations</h1>
        <p className="text-gray-600">
          Overview of all bike sharing stations in Budapest
        </p>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {stations?.map((station) => (
            <li key={station.uid}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {station.name}
                    </p>
                    <p className="text-sm text-gray-500">
                      Station ID: {station.uid}
                    </p>
                  </div>
                  <div className="flex-shrink-0 text-right">
                    <p className="text-sm text-gray-900">
                      <span className="font-medium">Location:</span>
                    </p>
                    <p className="text-sm text-gray-500">
                      {station.lat.toFixed(6)}, {station.lng.toFixed(6)}
                    </p>
                    {station.bike_count !== undefined && (
                      <p className="text-sm text-primary-600 font-medium">
                        {station.bike_count} bikes available
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {stations && stations.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-500">No stations found.</div>
        </div>
      )}
    </div>
  )
}