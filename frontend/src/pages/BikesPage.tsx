import React, { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '../services/api'
import BikeCard from '../components/BikeCard'
import SearchInput from '../components/SearchInput'
import { BikeMovement } from '../types/api'

export default function BikesPage() {
  const [selectedBike, setSelectedBike] = useState<string | null>(null)
  const [historyPages, setHistoryPages] = useState<{ [bikeNumber: string]: number }>({})
  const [accumulatedHistory, setAccumulatedHistory] = useState<{ [bikeNumber: string]: BikeMovement[] }>({})
  const [searchQuery, setSearchQuery] = useState("")
  const navigate = useNavigate()


  const { data: bikes, isLoading, error } = useQuery({
    queryKey: ['bikes', 'all'],
    queryFn: () => apiClient.getAllBikes(),
  })

  const currentPage = selectedBike ? (historyPages[selectedBike] || 1) : 1

  const { data: bikeHistoryResponse, isLoading: historyLoading, error: historyError } = useQuery({
    queryKey: ['bike-history', selectedBike, currentPage],
    queryFn: () => selectedBike ? apiClient.getBikeHistory(selectedBike, currentPage) : Promise.resolve({ data: [], meta: { total: 0, has_next: false, page: 1, pages: 0 } }),
    enabled: !!selectedBike,
  })

  // Handle accumulating history data
  const bikeHistory = selectedBike ? (accumulatedHistory[selectedBike] || []) : []
  const historyMeta = bikeHistoryResponse?.meta

  // Effect to accumulate history when new data is loaded
  React.useEffect(() => {
    if (selectedBike && bikeHistoryResponse?.data) {
      setAccumulatedHistory(prev => {
        const currentHistory = prev[selectedBike] || []
        const newData = bikeHistoryResponse.data
        
        // If this is page 1, replace the history, otherwise append
        const isFirstPage = currentPage === 1
        const updatedHistory = isFirstPage ? newData : [...currentHistory, ...newData]
        
        return {
          ...prev,
          [selectedBike]: updatedHistory
        }
      })
    }
  }, [selectedBike, bikeHistoryResponse, currentPage])

  // Reset history when changing bikes
  const handleBikeSelection = (bikeNumber: string) => {
    const newSelectedBike = selectedBike === bikeNumber ? null : bikeNumber
    setSelectedBike(newSelectedBike)
    
    if (newSelectedBike && !accumulatedHistory[newSelectedBike]) {
      // Reset page to 1 for new bike selection
      setHistoryPages(prev => ({
        ...prev,
        [newSelectedBike]: 1
      }))
    }
  }

  // Filter bikes based on search query
  const filteredBikes = useMemo(() => {
    if (!bikes || !searchQuery.trim()) return bikes

    const query = searchQuery.toLowerCase().trim()
    return bikes.filter(bike => 
      bike.bike_number.toLowerCase().includes(query) ||
      bike.current_location.name.toLowerCase().includes(query) ||
      bike.total_trips.toString().includes(query) ||
      bike.total_distance_km.toString().includes(query)
    )
  }, [bikes, searchQuery])

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Bikes</h1>
        <p className="text-gray-600 mb-4">
          Monitor individual bikes and their status
        </p>
        
        {/* Search Input */}
        <div className="max-w-md">
          <SearchInput
            placeholder="Search bikes by number, location, trips, or distance..."
            onSearch={setSearchQuery}
            className="w-full"
          />
        </div>
        
        {/* Results Count */}
        {searchQuery && filteredBikes && (
          <div className="mt-3 text-sm text-gray-500">
            {filteredBikes.length === 0 
              ? "No bikes found" 
              : `${filteredBikes.length} of ${bikes?.length || 0} bikes`}
          </div>
        )}
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
      {filteredBikes && filteredBikes.length > 0 ? (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {filteredBikes.map((bike) => (
              <li key={bike.bike_number}>
                <BikeCard 
                  bike={bike}
                  showViewHistoryButton={true}
                  onViewHistory={() => handleBikeSelection(bike.bike_number)}
                  isHistoryExpanded={selectedBike === bike.bike_number}
                  showInlineHistory={true}
                  historyData={selectedBike === bike.bike_number ? bikeHistory : []}
                  historyLoading={selectedBike === bike.bike_number ? historyLoading : false}
                  historyError={selectedBike === bike.bike_number ? historyError : null}
                  historyMeta={selectedBike === bike.bike_number ? historyMeta : undefined}
                  onLoadMore={() => {
                    if (selectedBike) {
                      setHistoryPages(prev => ({
                        ...prev,
                        [selectedBike]: (prev[selectedBike] || 1) + 1
                      }))
                    }
                  }}
                  onStationClick={(stationUid) => navigate(`/stations/${stationUid}`)}
                  searchQuery={searchQuery}
                />
              </li>
            ))}
          </ul>
        </div>
      ) : bikes && bikes.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-500">No bikes found.</div>
        </div>
      ) : searchQuery ? (
        <div className="text-center py-12">
          <div className="text-gray-500">
            No bikes match your search "{searchQuery}".
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