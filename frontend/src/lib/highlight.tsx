import React from 'react'

export function highlightText(text: string, searchQuery: string): React.ReactNode {
  if (!searchQuery.trim()) {
    return text
  }

  const query = searchQuery.trim()
  const regex = new RegExp(`(${query})`, 'gi')
  const parts = text.split(regex)

  return parts.map((part, index) => {
    if (regex.test(part)) {
      return (
        <mark key={index} className="bg-yellow-200 text-gray-900 px-0.5 rounded">
          {part}
        </mark>
      )
    }
    return part
  })
}