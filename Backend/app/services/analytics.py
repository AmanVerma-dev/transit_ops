"""Analytics service — computes metrics from raw repository data."""
import logging
from typing import Optional
from datetime import date

from app.repositories.analytics import AnalyticsRepository
from app.schemas.analytics import (
    AnalyticsFilter,
    FleetUtilizationResponse,
    FuelEfficiencyResponse,
    FuelEfficiencyItem,
    OperationalCostResponse,
    VehicleROIResponse,
    VehicleROIItem,
    TripSummaryResponse,
)

logger = logging.getLogger("transitops.analytics")

# Estimated fuel price per liter for cost calculations
FUEL_PRICE_PER_LITER = 1.50


class AnalyticsService:
    def __init__(self, repo: AnalyticsRepository):
        self.repo = repo

    def get_fleet_utilization(self, f: AnalyticsFilter) -> FleetUtilizationResponse:
        total_vehicles = self.repo.count_active_vehicles(region=f.region)
        vehicles_with_trips = self.repo.count_vehicles_with_completed_trips(
            start_date=f.start_date, end_date=f.end_date, region=f.region
        )
        completed = self.repo.count_completed_trips(
            vehicle_id=f.vehicle_id, driver_id=f.driver_id,
            start_date=f.start_date, end_date=f.end_date, region=f.region
        )
        pct = (vehicles_with_trips / total_vehicles * 100) if total_vehicles > 0 else 0.0
        logger.info("Fleet utilization calculated: %.1f%% (%d/%d vehicles)", pct, vehicles_with_trips, total_vehicles)
        return FleetUtilizationResponse(
            total_vehicles=total_vehicles,
            vehicles_with_completed_trips=vehicles_with_trips,
            utilization_percentage=round(pct, 2),
            total_completed_trips=completed,
        )

    def get_fuel_efficiency(self, f: AnalyticsFilter) -> FuelEfficiencyResponse:
        rows = self.repo.get_fuel_efficiency_by_vehicle(
            vehicle_id=f.vehicle_id, start_date=f.start_date, end_date=f.end_date, region=f.region
        )
        items = []
        total_dist = 0.0
        total_fuel = 0.0
        for vid, reg, dist, fuel in rows:
            eff = round(dist / fuel, 2) if fuel > 0 else 0.0
            items.append(FuelEfficiencyItem(
                vehicle_id=vid, registration_number=reg,
                total_distance_km=float(dist), total_fuel_liters=float(fuel),
                efficiency_km_per_liter=eff,
            ))
            total_dist += float(dist)
            total_fuel += float(fuel)
        fleet_avg = round(total_dist / total_fuel, 2) if total_fuel > 0 else 0.0
        logger.info("Fuel efficiency computed for %d vehicles, fleet avg %.2f km/L", len(items), fleet_avg)
        return FuelEfficiencyResponse(items=items, fleet_avg_efficiency=fleet_avg)

    def get_operational_cost(self, f: AnalyticsFilter) -> OperationalCostResponse:
        fuel_rows = self.repo.get_fuel_liters_by_vehicle(
            vehicle_id=f.vehicle_id, start_date=f.start_date, end_date=f.end_date, region=f.region
        )
        maint_rows = self.repo.get_maintenance_cost_by_vehicle(
            vehicle_id=f.vehicle_id, start_date=f.start_date, end_date=f.end_date, region=f.region
        )

        fuel_map = {vid: (reg, float(liters)) for vid, reg, liters in fuel_rows}
        maint_map = {vid: (reg, float(cost)) for vid, reg, cost in maint_rows}

        all_vids = set(fuel_map.keys()) | set(maint_map.keys())
        breakdown = []
        total_fuel = 0.0
        total_maint = 0.0
        for vid in sorted(all_vids):
            fuel_reg, fuel_liters = fuel_map.get(vid, ("", 0.0))
            maint_reg, maint_cost = maint_map.get(vid, ("", 0.0))
            reg = fuel_reg or maint_reg
            fuel_cost = round(fuel_liters * FUEL_PRICE_PER_LITER, 2)
            total_fuel += fuel_cost
            total_maint += maint_cost
            breakdown.append({
                "vehicle_id": vid,
                "registration_number": reg,
                "fuel_cost": fuel_cost,
                "maintenance_cost": round(maint_cost, 2),
                "total": round(fuel_cost + maint_cost, 2),
            })

        logger.info("Operational cost computed: fuel=$%.2f, maintenance=$%.2f", total_fuel, total_maint)
        return OperationalCostResponse(
            total_fuel_cost_estimate=round(total_fuel, 2),
            total_maintenance_cost=round(total_maint, 2),
            total_cost=round(total_fuel + total_maint, 2),
            breakdown_by_vehicle=breakdown,
        )

    def get_vehicle_roi(self, f: AnalyticsFilter) -> VehicleROIResponse:
        rev_rows = self.repo.get_revenue_by_vehicle(
            vehicle_id=f.vehicle_id, start_date=f.start_date, end_date=f.end_date, region=f.region
        )
        fuel_rows = self.repo.get_fuel_liters_by_vehicle(
            vehicle_id=f.vehicle_id, start_date=f.start_date, end_date=f.end_date, region=f.region
        )
        maint_rows = self.repo.get_maintenance_cost_by_vehicle(
            vehicle_id=f.vehicle_id, start_date=f.start_date, end_date=f.end_date, region=f.region
        )

        fuel_map = {vid: float(liters) for vid, _, liters in fuel_rows}
        maint_map = {vid: float(cost) for vid, _, cost in maint_rows}

        items = []
        fleet_rev = 0.0
        fleet_cost = 0.0
        for vid, reg, acq_cost, revenue in rev_rows:
            fuel_cost = fuel_map.get(vid, 0.0) * FUEL_PRICE_PER_LITER
            maint_cost = maint_map.get(vid, 0.0)
            op_cost = round(fuel_cost + maint_cost, 2)
            net = round(float(revenue) - op_cost, 2)
            items.append(VehicleROIItem(
                vehicle_id=vid, registration_number=reg,
                acquisition_cost=float(acq_cost),
                total_revenue=float(revenue),
                total_operating_cost=op_cost,
                net_roi=net,
            ))
            fleet_rev += float(revenue)
            fleet_cost += op_cost

        logger.info("Vehicle ROI computed for %d vehicles", len(items))
        return VehicleROIResponse(
            items=items,
            fleet_total_revenue=round(fleet_rev, 2),
            fleet_total_cost=round(fleet_cost, 2),
            fleet_net_roi=round(fleet_rev - fleet_cost, 2),
        )

    def get_trip_summary(self, f: AnalyticsFilter) -> TripSummaryResponse:
        counts = self.repo.get_trip_counts_by_status(
            vehicle_id=f.vehicle_id, driver_id=f.driver_id,
            start_date=f.start_date, end_date=f.end_date, region=f.region
        )
        avg_dist, avg_rev, total_rev, total_dist = self.repo.get_trip_averages(
            vehicle_id=f.vehicle_id, driver_id=f.driver_id,
            start_date=f.start_date, end_date=f.end_date, region=f.region
        )
        return TripSummaryResponse(
            total_trips=sum(counts.values()),
            completed_trips=counts.get("COMPLETED", 0),
            cancelled_trips=counts.get("CANCELLED", 0),
            active_trips=counts.get("DISPATCHED", 0),
            draft_trips=counts.get("DRAFT", 0),
            average_distance_km=round(float(avg_dist), 2),
            average_revenue=round(float(avg_rev), 2),
            total_revenue=round(float(total_rev), 2),
            total_distance_km=round(float(total_dist), 2),
        )
