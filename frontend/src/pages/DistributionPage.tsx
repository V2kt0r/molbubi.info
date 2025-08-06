import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/services/api'
import { convertDistributionToLocalTime, formatHour, getUserTimezone } from '@/lib/date'

export default function DistributionPage() {
  const [selectedStations, setSelectedStations] = useState<number[]>([])
  const [searchTerm, setSearchTerm] = useState('')

  // Get all stations for the selector
  const { data: allStations, isLoading: stationsLoading } = useQuery({
    queryKey: ['stations', 'all'],
    queryFn: () => apiClient.getAllStations(),
  })

  const { data: arrivalsRaw, isLoading: arrivalsLoading, error: arrivalsError } = useQuery({
    queryKey: ['distribution', 'arrivals', selectedStations],
    queryFn: () => apiClient.getHourlyArrivalDistribution(
      undefined, // startDate
      undefined, // endDate  
      selectedStations.length > 0 ? selectedStations : undefined
    ),
  })

  // Convert UTC hours to local timezone
  const arrivals = arrivalsRaw ? convertDistributionToLocalTime(arrivalsRaw) : undefined

  const { data: departuresRaw, isLoading: departuresLoading, error: departuresError } = useQuery({
    queryKey: ['distribution', 'departures', selectedStations],
    queryFn: () => apiClient.getHourlyDepartureDistribution(
      undefined, // startDate
      undefined, // endDate
      selectedStations.length > 0 ? selectedStations : undefined
    ),
  })

  // Convert UTC hours to local timezone
  const departures = departuresRaw ? convertDistributionToLocalTime(departuresRaw) : undefined

  const isLoading = arrivalsLoading || departuresLoading || stationsLoading
  const error = arrivalsError || departuresError

  if (isLoading) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[...Array(9)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="text-red-800">
            Error loading distribution: {error instanceof Error ? error.message : 'Unknown error'}
          </div>
        </div>
      </div>
    )
  }

  const totalArrivals = arrivals?.reduce((sum: number, hour) => sum + (hour.arrival_count || 0), 0) || 0
  const totalDepartures = departures?.reduce((sum: number, hour) => sum + (hour.departure_count || 0), 0) || 0
  const peakArrivalHour = arrivals?.reduce((max, hour) => 
    (hour.arrival_count || 0) > (max.arrival_count || 0) ? hour : max, 
    arrivals[0]
  )
  const peakDepartureHour = departures?.reduce((max, hour) => 
    (hour.departure_count || 0) > (max.departure_count || 0) ? hour : max, 
    departures[0]
  )

  const userTimezone = getUserTimezone()

  // Filter stations based on search term
  const filteredStations = allStations?.filter(station =>
    station.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    station.uid.toString().includes(searchTerm)
  ) || []

  // Get selected station objects for display
  const selectedStationObjects = allStations?.filter(station => 
    selectedStations.includes(station.uid)
  ) || []

  // Handle station selection
  const handleStationToggle = (stationId: number) => {
    setSelectedStations(prev => 
      prev.includes(stationId)
        ? prev.filter(id => id !== stationId)
        : [...prev, stationId]
    )
  }

  const handleSelectAll = () => {
    setSelectedStations(filteredStations.map(station => station.uid))
  }

  const handleClearAll = () => {
    setSelectedStations([])
  }

  const removeStation = (stationId: number) => {
    setSelectedStations(prev => prev.filter(id => id !== stationId))
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Bike Distribution Analytics</h1>
        <p className="text-gray-600">
          Hourly pickup and dropoff patterns throughout the day
        </p>
        <p className="text-sm text-gray-500 mt-1">
          Times shown in your local timezone: {userTimezone}
        </p>
      </div>

      {/* Station Selector */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Select Stations to Compare</h3>
        
        {/* Search and Controls */}
        <div className="flex flex-col sm:flex-row gap-4 mb-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search stations by name or ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleSelectAll}
              className="px-4 py-2 text-sm font-medium text-primary-600 hover:text-primary-500 border border-primary-300 rounded-md hover:border-primary-400"
            >
              Select All
            </button>
            <button
              onClick={handleClearAll}
              className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-500 border border-gray-300 rounded-md hover:border-gray-400"
            >
              Clear All
            </button>
          </div>
        </div>

        {/* Selected Stations Chips */}
        {selectedStationObjects.length > 0 && (
          <div className="mb-4">
            <p className="text-sm text-gray-600 mb-2">Selected stations ({selectedStationObjects.length}):</p>
            <div className="flex flex-wrap gap-2">
              {selectedStationObjects.map((station) => (
                <span
                  key={station.uid}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800"
                >
                  {station.name}
                  <button
                    onClick={() => removeStation(station.uid)}
                    className="ml-2 inline-flex items-center justify-center w-4 h-4 rounded-full text-primary-600 hover:bg-primary-200 hover:text-primary-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Station List */}
        {stationsLoading ? (
          <div className="max-h-60 overflow-y-auto border border-gray-200 rounded-md">
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
              <span className="ml-3 text-sm text-gray-500">Loading all stations...</span>
            </div>
          </div>
        ) : filteredStations.length > 0 ? (
          <div className="max-h-60 overflow-y-auto border border-gray-200 rounded-md">
            {filteredStations.map((station) => (
              <label
                key={station.uid}
                className="flex items-center px-4 py-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
              >
                <input
                  type="checkbox"
                  checked={selectedStations.includes(station.uid)}
                  onChange={() => handleStationToggle(station.uid)}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <div className="ml-3 flex-1">
                  <div className="text-sm font-medium text-gray-900">{station.name}</div>
                  <div className="text-sm text-gray-500">
                    ID: {station.uid} • {station.bike_count} bikes available
                  </div>
                </div>
              </label>
            ))}
          </div>
        ) : (
          <div className="max-h-60 overflow-y-auto border border-gray-200 rounded-md">
            <div className="flex items-center justify-center py-8">
              <span className="text-sm text-gray-500">
                {searchTerm ? 'No stations found matching your search.' : 'No stations available.'}
              </span>
            </div>
          </div>
        )}

        {/* Info text */}
        <p className="text-sm text-gray-500 mt-4">
          {stationsLoading ? (
            "Loading station data..."
          ) : selectedStations.length === 0 ? (
            `Showing data for all ${allStations?.length || 0} stations. Select specific stations above to compare their patterns.`
          ) : (
            `Showing data for ${selectedStations.length} selected station${selectedStations.length === 1 ? '' : 's'} out of ${allStations?.length || 0} total.`
          )}
        </p>
      </div>

      {/* Summary Stats */}
      {(arrivals || departures) && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          <div className="bg-white rounded-lg shadow px-6 py-4">
            <div className="text-2xl font-bold text-blue-600">{totalArrivals}</div>
            <div className="text-sm text-gray-500">
              Total Arrivals
              {selectedStations.length > 0 && (
                <span className="block text-xs text-gray-400">
                  ({selectedStations.length} station{selectedStations.length === 1 ? '' : 's'})
                </span>
              )}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow px-6 py-4">
            <div className="text-2xl font-bold text-green-600">{totalDepartures}</div>
            <div className="text-sm text-gray-500">
              Total Departures
              {selectedStations.length > 0 && (
                <span className="block text-xs text-gray-400">
                  ({selectedStations.length} station{selectedStations.length === 1 ? '' : 's'})
                </span>
              )}
            </div>
          </div>
          {peakArrivalHour && (
            <div className="bg-white rounded-lg shadow px-6 py-4">
              <div className="text-2xl font-bold text-purple-600">{formatHour(peakArrivalHour.time)}</div>
              <div className="text-sm text-gray-500">Peak Arrivals</div>
            </div>
          )}
          {peakDepartureHour && (
            <div className="bg-white rounded-lg shadow px-6 py-4">
              <div className="text-2xl font-bold text-orange-600">{formatHour(peakDepartureHour.time)}</div>
              <div className="text-sm text-gray-500">Peak Departures</div>
            </div>
          )}
        </div>
      )}

      {/* Hourly Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Arrivals Chart */}
        {arrivals && arrivals.length > 0 && (
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Hourly Arrivals
              {selectedStations.length > 0 && (
                <span className="text-sm font-normal text-gray-500 ml-2">
                  ({selectedStations.length} station{selectedStations.length === 1 ? '' : 's'})
                </span>
              )}
            </h3>
            <div className="space-y-2">
              {arrivals.map((hour) => {
                const maxCount = Math.max(...arrivals.map((h) => h.arrival_count || 0))
                const percentage = maxCount > 0 ? ((hour.arrival_count || 0) / maxCount) * 100 : 0
                
                return (
                  <div key={hour.time} className="flex items-center">
                    <div className="w-12 text-xs text-gray-500 text-right mr-2">
                      {formatHour(hour.time)}
                    </div>
                    <div className="flex-1 bg-gray-200 rounded-full h-4 relative">
                      <div
                        className="bg-blue-500 h-4 rounded-full flex items-center justify-end pr-2"
                        style={{ width: `${Math.max(percentage, 2)}%` }}
                      >
                        {(hour.arrival_count || 0) > 0 && (
                          <span className="text-xs text-white font-medium">
                            {hour.arrival_count}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Departures Chart */}
        {departures && departures.length > 0 && (
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Hourly Departures
              {selectedStations.length > 0 && (
                <span className="text-sm font-normal text-gray-500 ml-2">
                  ({selectedStations.length} station{selectedStations.length === 1 ? '' : 's'})
                </span>
              )}
            </h3>
            <div className="space-y-2">
              {departures.map((hour) => {
                const maxCount = Math.max(...departures.map((h) => h.departure_count || 0))
                const percentage = maxCount > 0 ? ((hour.departure_count || 0) / maxCount) * 100 : 0
                
                return (
                  <div key={hour.time} className="flex items-center">
                    <div className="w-12 text-xs text-gray-500 text-right mr-2">
                      {formatHour(hour.time)}
                    </div>
                    <div className="flex-1 bg-gray-200 rounded-full h-4 relative">
                      <div
                        className="bg-green-500 h-4 rounded-full flex items-center justify-end pr-2"
                        style={{ width: `${Math.max(percentage, 2)}%` }}
                      >
                        {(hour.departure_count || 0) > 0 && (
                          <span className="text-xs text-white font-medium">
                            {hour.departure_count}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </div>

      {/* Selected Stations Summary */}
      {selectedStationObjects.length > 0 && (
        <div className="mt-8">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Selected Stations Summary</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {selectedStationObjects.map((station) => (
              <div key={station.uid} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-medium text-gray-900 truncate">{station.name}</h4>
                  <button
                    onClick={() => removeStation(station.uid)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ×
                  </button>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Station ID:</span>
                    <span className="text-gray-900">{station.uid}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Available bikes:</span>
                    <span className="text-gray-900">{station.bike_count}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Location:</span>
                    <span className="text-gray-900 text-xs">
                      {station.lat.toFixed(4)}, {station.lng.toFixed(4)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {(!arrivals || arrivals.length === 0) && (!departures || departures.length === 0) && (
        <div className="text-center py-12">
          <div className="text-gray-500">No distribution data available.</div>
        </div>
      )}
    </div>
  )
}