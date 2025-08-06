import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../services/api'
import { formatLocalDateTime, formatRelativeTime } from '../lib/date'
import BikeCard from '../components/BikeCard'

export default function BikesPage() {
  const [selectedBike, setSelectedBike] = useState<string | null>(null)


  const { data: bikes, isLoading, error } = useQuery({
    queryKey: ['bikes'],
    queryFn: () => apiClient.getBikes(),
  })

  const { data: bikeHistory, isLoading: historyLoading } = useQuery({
    queryKey: ['bike-history', selectedBike],
    queryFn: () => selectedBike ? apiClient.getBikeHistory(selectedBike) : Promise.resolve([]),
    enabled: !!selectedBike,
  })

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Bikes</h1>
        <p className="text-gray-600">
          Monitor individual bikes and their status
        </p>
      </div>


      {/* Loading State */}
      {isLoading && (
        <div className="animate-pulse space-y-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-20 bg-gray-200 rounded"></div>
          ))}
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="text-red-800">
            Error loading bikes: {error instanceof Error ? error.message : 'Unknown error'}
          </div>
        </div>
      )}

      {/* Bikes List */}
      {bikes && bikes.length > 0 && (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {bikes.map((bike) => (
              <li key={bike.bike_number}>
                <BikeCard 
                  bike={bike}
                  showViewHistoryButton={true}
                  onViewHistory={() => setSelectedBike(selectedBike === bike.bike_number ? null : bike.bike_number)}
                  isHistoryExpanded={selectedBike === bike.bike_number}
                />
                
                {/* Bike History Section */}
                {selectedBike === bike.bike_number && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <h4 className="text-sm font-medium text-gray-900 mb-3">Recent Trip History</h4>
                    
                    {historyLoading ? (
                      <div className="flex items-center justify-center py-4">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>
                        <span className="ml-2 text-sm text-gray-500">Loading history...</span>
                      </div>
                    ) : bikeHistory && bikeHistory.length > 0 ? (
                      <div className="space-y-3 max-h-64 overflow-y-auto">
                        {bikeHistory.slice(0, 10).map((trip, index) => (
                          <div key={index} className="bg-gray-50 rounded-lg p-3">
                            <div className="flex items-start justify-between">
                              <div className="flex-1 min-w-0">
                                <div className="text-sm text-gray-900">
                                  <span className="font-medium">{trip.start_station.name}</span>
                                  <span className="mx-2 text-gray-400">→</span>
                                  <span className="font-medium">{trip.end_station.name}</span>
                                </div>
                                <div className="mt-1 text-xs text-gray-500">
                                  Distance: {trip.distance_km.toFixed(2)} km
                                </div>
                              </div>
                              <div className="text-right text-xs text-gray-500 ml-4">
                                <div className="font-medium text-gray-700">
                                  {formatRelativeTime(trip.end_time)}
                                </div>
                                <div className="mt-1">
                                  {formatLocalDateTime(trip.start_time, {
                                    month: 'short',
                                    day: 'numeric',
                                    hour: '2-digit',
                                    minute: '2-digit',
                                    hour12: true
                                  })}
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                        {bikeHistory.length > 10 && (
                          <div className="text-center text-xs text-gray-500 py-2">
                            Showing 10 most recent trips out of {bikeHistory.length} total
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="text-center py-4 text-sm text-gray-500">
                        No trip history available
                      </div>
                    )}
                  </div>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Empty State */}
      {bikes && bikes.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-500">No bikes found.</div>
        </div>
      )}
    </div>
  )
}