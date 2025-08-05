# Molbubi Frontend

React + TypeScript frontend for the Molbubi bike tracking system.

## Technology Stack

- **React 18** with TypeScript for the UI framework
- **Vite** for fast development and optimized builds
- **TailwindCSS** for utility-first styling
- **React Query (TanStack Query)** for server state management
- **React Router v6** for client-side routing
- **Axios** for HTTP requests
- **Zod** for runtime type validation

## Development

### Prerequisites

- Node.js 20+
- npm or yarn

### Local Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# The app will be available at http://localhost:3000
```

### Building for Production

```bash
# Build the application
npm run build

# Preview the production build
npm run preview
```

### Docker Development

The frontend is integrated with the main Docker Compose setup:

```bash
# Build and start all services including frontend
docker compose up -d --build

# Start only the frontend service
docker compose up frontend

# The frontend will be available at http://localhost:3000
```

## Environment Configuration

The application uses environment variables for configuration:

### Required Variables

- `REACT_APP_API_BASE_URL`: Base URL for the API service (default: http://localhost:8080)
- `REACT_APP_ENVIRONMENT`: Environment name (dev/staging/prod)

### Docker Environment

When running with Docker Compose, these variables are automatically loaded from the `.env` file in the project root.

## Project Structure

```
src/
├── components/          # Reusable UI components
├── pages/              # Route-specific page components
├── services/           # API client and external services
├── types/              # TypeScript type definitions
├── lib/                # Utility functions and configurations
├── hooks/              # Custom React hooks (future)
├── context/            # React Context providers (future)
└── assets/             # Images, icons, etc. (future)
```

## API Integration

The frontend connects to the FastAPI backend service and provides interfaces for:

- **Stations**: View all bike stations and their details
- **Bikes**: Monitor individual bikes and their status
- **Distribution**: Real-time bike availability across stations
- **Movements**: Bike movement history and tracking
- **Stays**: Bike stay duration and patterns

## Features

### Current Features

- Responsive design with TailwindCSS
- Real-time data fetching with React Query
- Station overview and filtering
- Bike tracking and status monitoring
- Distribution visualization
- Error handling and loading states

### Future Enhancements

- Interactive maps for station visualization
- Real-time updates with WebSocket
- Historical data charts and analytics
- Advanced filtering and search
- Mobile-optimized interface

## Code Quality

The project includes:

- **TypeScript** for type safety
- **ESLint** for code linting
- **Prettier** for code formatting (to be added)
- **Strict mode** TypeScript configuration

## Deployment

The frontend is designed to work seamlessly with:

- **Docker Compose** for local development
- **Nginx** reverse proxy for production
- **Environment-based configuration** for different deployment targets
- **CI/CD integration** with GitHub Actions

For production deployment, the application builds to static files that can be served by any web server or CDN.