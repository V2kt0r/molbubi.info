import { BikeWithStats } from '../types/api'

interface BikeCardProps {
  bike: BikeWithStats
  showViewHistoryButton?: boolean
  onViewHistory?: () => void
  isHistoryExpanded?: boolean
}

export default function BikeCard({ 
  bike, 
  showViewHistoryButton = false, 
  onViewHistory,
  isHistoryExpanded = false 
}: BikeCardProps) {
  return (
    <div className="px-4 py-4 sm:px-6">
      <div className="flex items-center justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-gray-900">
              Bike #{bike.bike_number}
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
              Location: {bike.current_location.name}
            </span>
            <span>
              {bike.total_trips} trips
            </span>
            <span>
              {bike.total_distance_km.toFixed(1)} km total
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
    </div>
  )
}