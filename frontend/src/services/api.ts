import axios, { AxiosInstance, AxiosError } from 'axios';
import { ENV } from '../lib/env';
import {
  StationBikeCount,
  BikeWithStats,
  BikeMovement,
  BikeStay,
  HourlyDistribution,
  StationsResponseSchema,
  BikesResponseSchema,
  BikeMovementsResponseSchema,
  HourlyDistributionResponseSchema,
  ApiErrorSchema,
  ApiError,
} from '../types/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: ENV.API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        if (ENV.IS_DEVELOPMENT) {
          console.log('API Request:', config.method?.toUpperCase(), config.url);
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        if (ENV.IS_DEVELOPMENT) {
          console.log('API Response:', response.status, response.config.url);
        }
        return response;
      },
      (error: AxiosError) => {
        const apiError = this.handleError(error);
        return Promise.reject(apiError);
      }
    );
  }

  private handleError(error: AxiosError): ApiError {
    if (error.response?.data) {
      try {
        const parsedError = ApiErrorSchema.parse(error.response.data);
        return parsedError;
      } catch {
        // If parsing fails, create a generic error
      }
    }

    // Default error handling
    const message = error.message || 'An unexpected error occurred';
    return { detail: message };
  }

  // Stations endpoints
  async getStations(page: number = 1, limit: number = 100): Promise<StationBikeCount[]> {
    const response = await this.client.get(`/stations/?skip=${(page - 1) * limit}&limit=${limit}`);
    const parsed = StationsResponseSchema.parse(response.data);
    return parsed.data;
  }

  // Get all stations by fetching all pages
  async getAllStations(): Promise<StationBikeCount[]> {
    let allStations: StationBikeCount[] = [];
    let page = 1;
    let hasMore = true;
    const limit = 300;

    while (hasMore) {
      const response = await this.client.get(`/stations/?skip=${(page - 1) * limit}&limit=${limit}`);
      const parsed = StationsResponseSchema.parse(response.data);
      
      allStations.push(...parsed.data);
      
      hasMore = parsed.meta.has_next;
      page++;
    }

    return allStations;
  }

  async getStation(stationId: number): Promise<StationBikeCount> {
    const response = await this.client.get(`/stations/${stationId}`);
    return response.data;
  }

  async getBikesAtStation(stationId: number): Promise<string[]> {
    const response = await this.client.get(`/stations/${stationId}/bikes`);
    return response.data;
  }

  // Bikes endpoints
  async getBikes(): Promise<BikeWithStats[]> {
    const response = await this.client.get('/bikes/');
    const parsed = BikesResponseSchema.parse(response.data);
    return parsed.data;
  }

  async getAllBikes(): Promise<BikeWithStats[]> {
    let allBikes: BikeWithStats[] = []
    let page = 1
    let hasMore = true
    const limit = 2000

    while (hasMore) {
      const response = await this.client.get(`/bikes/?skip=${(page - 1) * limit}&limit=${limit}`);
      const parsed = BikesResponseSchema.parse(response.data);

      allBikes.push(...parsed.data)

      hasMore = parsed.meta.has_next;
      page++;
    }

    return allBikes
  }

  async getBikeHistory(bikeNumber: string): Promise<BikeMovement[]> {
    const response = await this.client.get(`/bikes/${bikeNumber}/history`);
    const parsed = BikeMovementsResponseSchema.parse(response.data);
    return parsed.data;
  }

  // Current bike distribution (using stations data)
  async getCurrentDistribution(): Promise<StationBikeCount[]> {
    return this.getStations(); // Same data, just renamed for clarity
  }

  // Distribution endpoints (for analytics)
  async getHourlyArrivalDistribution(
    startDate?: string,
    endDate?: string,
    stationUids?: number[]
  ): Promise<HourlyDistribution[]> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    stationUids?.forEach(uid => params.append('station_uids', uid.toString()));
    
    const response = await this.client.get(`/distribution/arrivals/hour?${params.toString()}`);
    return HourlyDistributionResponseSchema.parse(response.data).map(item => ({
      ...item,
      arrival_count: item.arrival_count || 0,
    }));
  }

  async getHourlyDepartureDistribution(
    startDate?: string,
    endDate?: string,
    stationUids?: number[]
  ): Promise<HourlyDistribution[]> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    stationUids?.forEach(uid => params.append('station_uids', uid.toString()));
    
    const response = await this.client.get(`/distribution/departures/hour?${params.toString()}`);
    return HourlyDistributionResponseSchema.parse(response.data).map(item => ({
      ...item,
      departure_count: item.departure_count || 0,
    }));
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export types for consumers
export type { StationBikeCount, BikeWithStats, BikeMovement, BikeStay, HourlyDistribution, ApiError };
