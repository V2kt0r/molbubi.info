import { useState } from 'react'
import { getDatePresets, isValidDateString, parseDateFromApi } from '../lib/date'

interface DateRangeFilterProps {
  startDate?: string
  endDate?: string
  onDateRangeChange: (startDate?: string, endDate?: string) => void
  className?: string
}

export default function DateRangeFilter({
  startDate,
  endDate,
  onDateRangeChange,
  className = ""
}: DateRangeFilterProps) {
  const [localStartDate, setLocalStartDate] = useState(startDate || "")
  const [localEndDate, setLocalEndDate] = useState(endDate || "")
  
  const presets = getDatePresets()

  const handlePresetClick = (preset: { startDate?: string; endDate?: string; label: string }) => {
    const newStartDate = preset.startDate || ""
    const newEndDate = preset.endDate || ""
    
    setLocalStartDate(newStartDate)
    setLocalEndDate(newEndDate)
    onDateRangeChange(preset.startDate, preset.endDate)
  }

  const handleStartDateChange = (value: string) => {
    setLocalStartDate(value)
    if (!value || isValidDateString(value)) {
      onDateRangeChange(value || undefined, endDate)
    }
  }

  const handleEndDateChange = (value: string) => {
    setLocalEndDate(value)
    if (!value || isValidDateString(value)) {
      onDateRangeChange(startDate, value || undefined)
    }
  }

  const handleClearDates = () => {
    setLocalStartDate("")
    setLocalEndDate("")
    onDateRangeChange(undefined, undefined)
  }

  const isDateRangeActive = startDate || endDate

  // Validation
  const isStartDateValid = !localStartDate || isValidDateString(localStartDate)
  const isEndDateValid = !localEndDate || isValidDateString(localEndDate)
  const isRangeValid = !localStartDate || !localEndDate || 
    (parseDateFromApi(localStartDate)?.getTime() || 0) <= (parseDateFromApi(localEndDate)?.getTime() || 0)

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Preset Buttons */}
      <div className="flex flex-wrap gap-2">
        {Object.values(presets).map((preset) => {
          const isActive = preset.startDate === startDate && preset.endDate === endDate
          return (
            <button
              key={preset.label}
              onClick={() => handlePresetClick(preset)}
              className={`px-3 py-2 text-sm font-medium rounded-md border transition-colors ${
                isActive
                  ? 'bg-primary-600 text-white border-primary-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500'
              }`}
            >
              {preset.label}
            </button>
          )
        })}
      </div>

      {/* Custom Date Inputs */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <label htmlFor="start-date" className="block text-sm font-medium text-gray-700 mb-1">
            Start Date
          </label>
          <input
            id="start-date"
            type="date"
            value={localStartDate}
            onChange={(e) => handleStartDateChange(e.target.value)}
            className={`block w-full px-3 py-2 border rounded-md shadow-sm bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:text-sm ${
              !isStartDateValid
                ? 'border-red-300 focus:border-red-500'
                : 'border-gray-300 focus:border-primary-500'
            }`}
          />
          {!isStartDateValid && (
            <p className="mt-1 text-sm text-red-600">Invalid date format</p>
          )}
        </div>
        
        <div className="flex-1">
          <label htmlFor="end-date" className="block text-sm font-medium text-gray-700 mb-1">
            End Date
          </label>
          <input
            id="end-date"
            type="date"
            value={localEndDate}
            onChange={(e) => handleEndDateChange(e.target.value)}
            className={`block w-full px-3 py-2 border rounded-md shadow-sm bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:text-sm ${
              !isEndDateValid
                ? 'border-red-300 focus:border-red-500'
                : 'border-gray-300 focus:border-primary-500'
            }`}
          />
          {!isEndDateValid && (
            <p className="mt-1 text-sm text-red-600">Invalid date format</p>
          )}
        </div>

        {/* Clear Button */}
        {isDateRangeActive && (
          <div className="flex items-end">
            <button
              onClick={handleClearDates}
              className="px-3 py-2 text-sm text-gray-500 hover:text-gray-700 focus:outline-none"
              title="Clear date filters"
            >
              Clear
            </button>
          </div>
        )}
      </div>

      {/* Validation Messages */}
      {!isRangeValid && (
        <p className="text-sm text-red-600">End date must be after start date</p>
      )}

      {/* Active Filter Display */}
      {isDateRangeActive && isRangeValid && (
        <div className="text-sm text-gray-600">
          <span className="font-medium">Active filter:</span>{' '}
          {startDate && endDate
            ? `${startDate} to ${endDate}`
            : startDate
            ? `From ${startDate}`
            : endDate
            ? `Until ${endDate}`
            : 'All time'}
        </div>
      )}
    </div>
  )
}