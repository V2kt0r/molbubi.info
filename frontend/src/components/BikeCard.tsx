import { BikeWithStats, BikeMovement } from '../types/api'
import { formatLocalDateTime, formatRelativeTime } from '../lib/date'
import { highlightText } from '../lib/highlight'

interface BikeCardProps {
  bike: BikeWithStats
  showViewHistoryButton?: boolean
  onViewHistory?: () => void
  isHistoryExpanded?: boolean
  // Inline history props
  showInlineHistory?: boolean
  historyData?: BikeMovement[]
  historyLoading?: boolean
  historyError?: Error | null
  historyMeta?: {
    total: number
    has_next: boolean
    page: number
    pages: number
  }
  onLoadMore?: () => void
  onStationClick?: (stationUid: number) => void
  searchQuery?: string
}

export default function BikeCard({ 
  bike, 
  showViewHistoryButton = false, 
  onViewHistory,
  isHistoryExpanded = false,
  showInlineHistory = false,
  historyData = [],
  historyLoading = false,
  historyError = null,
  historyMeta,
  onLoadMore,
  onStationClick,
  searchQuery = ""
}: BikeCardProps) {
  return (
    <div className="px-4 py-4 sm:px-6">
      <div className="flex items-center justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-gray-900">
              Bike #{highlightText(bike.bike_number, searchQuery)}
            </p>
            {showViewHistoryButton && onViewHistory && (
              <button
                onClick={onViewHistory}
                className="text-sm text-primary-600 hover:text-primary-500 font-medium"
              >
                {isHistoryExpanded ? 'Hide History' : 'View History'}
              </button>
            )}
          </div>
          <div className="flex space-x-4 text-sm text-gray-500">
            <span>
              Location: {highlightText(bike.current_location.name, searchQuery)}
            </span>
            <span>
              {highlightText(bike.total_trips.toString(), searchQuery)} trips
            </span>
            <span>
              {highlightText(bike.total_distance_km.toFixed(1), searchQuery)} km total
            </span>
          </div>
        </div>
        <div className="flex-shrink-0 flex flex-col items-end space-y-2">
          <div className="text-right">
            <div className="text-sm font-medium text-gray-900">
              {bike.total_distance_km.toFixed(1)} km
            </div>
            <div className="text-xs text-gray-500">
              Total Distance
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm font-medium text-primary-600">
              {bike.total_trips} trips
            </div>
            <div className="text-xs text-gray-500">
              Total Trips
            </div>
          </div>
          {bike.total_trips > 0 && (
            <div className="text-right">
              <div className="text-xs text-gray-500">
                Avg: {(bike.total_distance_km / bike.total_trips).toFixed(1)} km/trip
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Inline History Section */}
      {showInlineHistory && isHistoryExpanded && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-900 mb-4">Trip History</h4>
          
          {historyLoading ? (
            <div className="flex items-center justify-center py-6">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>
              <span className="ml-2 text-sm text-gray-500">Loading history...</span>
            </div>
          ) : historyError ? (
            <div className="text-center py-6 text-sm text-red-600">
              Error loading history: {historyError.message}
            </div>
          ) : historyData && historyData.length > 0 ? (
            <div className="space-y-2">
              {historyData.map((trip, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors">
                  <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between space-y-2 sm:space-y-0">
                    <div className="flex-1 min-w-0">
                      <div className="text-sm text-gray-900">
                        {onStationClick ? (
                          <>
                            <button
                              onClick={() => onStationClick(trip.start_station.uid)}
                              className="font-medium text-primary-600 hover:text-primary-700 hover:underline"
                            >
                              {trip.start_station.name}
                            </button>
                            <span className="mx-2 text-gray-400">→</span>
                            <button
                              onClick={() => onStationClick(trip.end_station.uid)}
                              className="font-medium text-primary-600 hover:text-primary-700 hover:underline"
                            >
                              {trip.end_station.name}
                            </button>
                          </>
                        ) : (
                          <>
                            <span className="font-medium">{trip.start_station.name}</span>
                            <span className="mx-2 text-gray-400">→</span>
                            <span className="font-medium">{trip.end_station.name}</span>
                          </>
                        )}
                      </div>
                      <div className="mt-1 text-xs text-gray-500">
                        Distance: {trip.distance_km.toFixed(2)} km
                      </div>
                    </div>
                    <div className="text-right text-xs text-gray-500 sm:ml-4">
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
              
              {/* Pagination Info and Load More */}
              {historyMeta && (
                <div className="mt-4 flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
                  <div className="text-sm text-gray-500">
                    Showing {historyData.length} of {historyMeta.total} trips
                    {historyMeta.page > 1 && ` (Page ${historyMeta.page} of ${historyMeta.pages})`}
                  </div>
                  {historyMeta.has_next && onLoadMore && (
                    <button
                      onClick={onLoadMore}
                      className="inline-flex items-center justify-center px-3 py-2 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
                    >
                      Load More Trips
                    </button>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-6 text-sm text-gray-500">
              No trip history available for this bike
            </div>
          )}
        </div>
      )}
    </div>
  )
}