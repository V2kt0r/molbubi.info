import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '../services/api'
import SearchInput from '../components/SearchInput'
import { highlightText } from '../lib/highlight'

export default function StationsPage() {
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState("")
  
  const { data: stations, isLoading, error } = useQuery({
    queryKey: ['stations', 'all'],
    queryFn: () => apiClient.getAllStations(),
  })

  const handleStationClick = (stationUid: number) => {
    navigate(`/stations/${stationUid}`)
  }

  // Filter stations based on search query
  const filteredStations = useMemo(() => {
    if (!stations || !searchQuery.trim()) return stations

    const query = searchQuery.toLowerCase().trim()
    return stations.filter(station => 
      station.name.toLowerCase().includes(query) ||
      station.uid.toString().includes(query) ||
      (station.bike_count !== undefined && station.bike_count.toString().includes(query))
    )
  }, [stations, searchQuery])

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
        <p className="text-gray-600 mb-4">
          Overview of all bike sharing stations in Budapest
        </p>
        
        {/* Search Input */}
        <div className="max-w-md">
          <SearchInput
            placeholder="Search stations by name, ID, or bike count..."
            onSearch={setSearchQuery}
            className="w-full"
          />
        </div>
        
        {/* Results Count */}
        {searchQuery && filteredStations && (
          <div className="mt-3 text-sm text-gray-500">
            {filteredStations.length === 0 
              ? "No stations found" 
              : `${filteredStations.length} of ${stations?.length || 0} stations`}
          </div>
        )}
      </div>

      {filteredStations && filteredStations.length > 0 ? (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {filteredStations.map((station) => (
              <li key={station.uid}>
                <div 
                  className="px-4 py-4 sm:px-6 hover:bg-gray-50 cursor-pointer transition-colors duration-150"
                  onClick={() => handleStationClick(station.uid)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {highlightText(station.name, searchQuery)}
                      </p>
                      <p className="text-sm text-gray-500">
                        Station ID: {highlightText(station.uid.toString(), searchQuery)}
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
                          {highlightText(station.bike_count.toString(), searchQuery)} bikes available
                        </p>
                      )}
                      <p className="text-xs text-gray-400 mt-1">
                        Click to view bikes →
                      </p>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      ) : stations && stations.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-500">No stations found.</div>
        </div>
      ) : searchQuery ? (
        <div className="text-center py-12">
          <div className="text-gray-500">
            No stations match your search "{searchQuery}".
            <button 
              onClick={() => setSearchQuery("")}
              className="ml-2 text-primary-600 hover:text-primary-700 underline"
            >
              Clear search
            </button>
          </div>
        </div>
      ) : null}
    </div>
  )
}