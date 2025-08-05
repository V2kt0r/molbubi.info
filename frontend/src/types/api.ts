import { z } from 'zod';

// Station with bike count schema (from /stations/ endpoint)
export const StationBikeCountSchema = z.object({
  uid: z.number(),
  name: z.string(),
  lat: z.number(),
  lng: z.number(),
  bike_count: z.number(),
});

export type StationBikeCount = z.infer<typeof StationBikeCountSchema>;

// Current location schema for bikes
export const CurrentLocationSchema = z.object({
  uid: z.number(),
  name: z.string(),
  lat: z.number(),
  lng: z.number(),
});

// Bike with statistics schema (from /bikes endpoint)
export const BikeWithStatsSchema = z.object({
  bike_number: z.string(),
  total_trips: z.number(),
  total_distance_km: z.number(),
  current_location: CurrentLocationSchema,
});

export type BikeWithStats = z.infer<typeof BikeWithStatsSchema>;

// Hourly distribution schema (from /distribution/arrivals/hour and /distribution/departures/hour)
export const HourlyDistributionSchema = z.object({
  time: z.number(), // 0-23 (hour of day)
  arrival_count: z.number().optional(),
  departure_count: z.number().optional(),
});

export type HourlyDistribution = z.infer<typeof HourlyDistributionSchema>;

// Station info schema for bike movements
export const MovementStationSchema = z.object({
  uid: z.number(),
  name: z.string(),
  lat: z.number(),
  lng: z.number(),
});

// Bike Movement schema (from bike history endpoint)
export const BikeMovementSchema = z.object({
  bike_number: z.string(),
  start_station: MovementStationSchema,
  end_station: MovementStationSchema,
  start_time: z.string(), // UTC timestamp
  end_time: z.string(), // UTC timestamp
  distance_km: z.number(),
});

export type BikeMovement = z.infer<typeof BikeMovementSchema>;

// Bike Stay schema
export const BikeStaySchema = z.object({
  id: z.number(),
  bike_number: z.string(),
  station_uid: z.number(),
  start_time: z.string(),
  end_time: z.string().nullable(),
});

export type BikeStay = z.infer<typeof BikeStaySchema>;

// API Response wrapper (your API uses data + meta structure)
export const ApiResponseSchema = <T>(itemSchema: z.ZodSchema<T>) => z.object({
  data: z.array(itemSchema),
  meta: z.object({
    page: z.number(),
    per_page: z.number(),
    total: z.number(),
    pages: z.number(),
    has_next: z.boolean(),
    has_prev: z.boolean(),
  }),
});

// API Response schemas
export const StationsResponseSchema = ApiResponseSchema(StationBikeCountSchema);
export const BikesResponseSchema = ApiResponseSchema(BikeWithStatsSchema);
export const BikeMovementsResponseSchema = ApiResponseSchema(BikeMovementSchema);
export const BikeStaysResponseSchema = z.array(BikeStaySchema);
export const HourlyDistributionResponseSchema = z.array(HourlyDistributionSchema);

// API Error schema
export const ApiErrorSchema = z.object({
  detail: z.string(),
});

export type ApiError = z.infer<typeof ApiErrorSchema>;