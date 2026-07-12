import React, { useState, useMemo, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useTripsStore } from '../store/useTripsStore';
import { useFleetStore } from '../store/useFleetStore';
import { useDriversStore } from '../store/useDriversStore';
import { useAuthStore } from '../store/useAuthStore';
import { StatusPill } from '../components/shared/StatusPill';
import { isLicenseExpired } from '../lib/calculations';
import { getPermission } from '../lib/rbac';
import { X } from 'lucide-react';
import { tripSchema, type TripFormValues } from '../schemas/tripSchema';

export const TripsPage: React.FC = () => {
  const { trips, isLoading, fetchTrips, createTrip, dispatchTrip, completeTrip, cancelTrip } = useTripsStore();
  const { vehicles, fetchVehicles, getAvailableVehicles } = useFleetStore();
  const { drivers, fetchDrivers, getAvailableDrivers } = useDriversStore();
  const userRole = useAuthStore(s => s.user?.role);
  const canManageTrips = userRole ? getPermission(userRole, 'trips') === 'full' : false;

  const [showCompleteDialog, setShowCompleteDialog] = useState(false);
  const [completingTripId, setCompletingTripId] = useState('');
  const [finalOdometer, setFinalOdometer] = useState('');
  const [fuelConsumed, setFuelConsumed] = useState('');
  const [submitError, setSubmitError] = useState('');
  const [actionError, setActionError] = useState('');

  useEffect(() => {
    fetchVehicles();
    fetchDrivers();
    fetchTrips();
  }, [fetchVehicles, fetchDrivers, fetchTrips]);

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<TripFormValues>({
    resolver: zodResolver(tripSchema),
    defaultValues: {
      source: 'Gandhinagar Depot',
      destination: 'Ahmedabad Hub',
      vehicleId: '',
      driverId: '',
      cargoWeight: '',
      plannedDistance: '',
    },
  });

  const availableVehicles = getAvailableVehicles();
  const availableDrivers = getAvailableDrivers();

  const selectedVehicleId = watch('vehicleId');
  const selectedDriverId = watch('driverId');
  const selectedVehicle = vehicles.find(v => v.id === selectedVehicleId);
  const selectedDriver = drivers.find(d => d.id === selectedDriverId);

  // Cross-record validation (capacity / availability / licence) – runs after RHF.
  const validationErrors = useMemo(() => {
    const errors: string[] = [];
    const weight = Number(watch('cargoWeight'));

    if (selectedVehicle && weight > selectedVehicle.capacity) {
      errors.push(`Vehicle Capacity: ${selectedVehicle.capacityLabel}\nCargo Weight: ${weight} kg\n✗ Capacity exceeded by ${weight - selectedVehicle.capacity} kg — dispatch blocked`);
    }
    if (selectedDriver && isLicenseExpired(selectedDriver.licenseExpiry)) {
      errors.push(`✗ Driver ${selectedDriver.name}'s license has expired — dispatch blocked`);
    }
    if (selectedVehicleId && selectedVehicle && selectedVehicle.status !== 'Available') {
      errors.push(`✗ Vehicle ${selectedVehicle.name} is not Available (${selectedVehicle.status}) — dispatch blocked`);
    }
    if (selectedDriverId && selectedDriver && selectedDriver.status !== 'Available') {
      errors.push(`✗ Driver ${selectedDriver.name} is not Available (${selectedDriver.status}) — dispatch blocked`);
    }
    return errors;
  }, [selectedVehicleId, selectedDriverId, selectedVehicle, selectedDriver, watch('cargoWeight')]);

  const onSubmit = async (values: TripFormValues) => {
    setSubmitError('');
    if (validationErrors.length > 0) {
      setSubmitError(validationErrors.join('\n'));
      return;
    }
    try {
      await createTrip({
        source: values.source,
        destination: values.destination,
        vehicleId: values.vehicleId,
        driverId: values.driverId,
        cargoWeight: Number(values.cargoWeight),
        plannedDistance: Number(values.plannedDistance),
        eta: `${Math.round(Number(values.plannedDistance) / 60 * 60)} min`,
      });
      // The store just created the trip on the backend, which defaults to DRAFT.
      // Now we automatically dispatch it, finding the newest draft trip.
      const lastTrip = useTripsStore.getState().trips.findLast(t => t.status === 'Draft');
      if (lastTrip) {
        await dispatchTrip(lastTrip.id);
      }
      reset();
    } catch (err: any) {
      setSubmitError(err.message || 'Failed to create and dispatch trip.');
    }
  };

  const handleAction = async (action: () => Promise<void>) => {
    setActionError('');
    try {
      await action();
    } catch (err: any) {
      setActionError(err.message || 'Action failed.');
    }
  };

  const handleComplete = (tripId: string) => {
    setCompletingTripId(tripId);
    setShowCompleteDialog(true);
    setFinalOdometer('');
    setFuelConsumed('');
  };

  const handleCompleteSubmit = async () => {
    if (!finalOdometer || !fuelConsumed) return;
    setActionError('');
    try {
      await completeTrip(completingTripId, parseInt(finalOdometer), parseFloat(fuelConsumed));
      setShowCompleteDialog(false);
    } catch (err: any) {
      setActionError(err.message || 'Failed to complete trip.');
      setShowCompleteDialog(false);
    }
  };

  const getVehicleName = (id: string | null) => vehicles.find(v => v.id === id)?.name || 'Unassigned';
  const getDriverName = (id: string | null) => drivers.find(d => d.id === id)?.name || 'Unassigned';

  const lifecycleSteps = ['Draft', 'Dispatched', 'Completed', 'Cancelled'];

  const inputClass =
    'w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange';
  const labelClass = 'text-[10px] uppercase text-text-faint tracking-wider mb-1 block';
  const fieldErrorClass = 'text-red text-[11px] mt-1';

  return (
    <div>
      <h1 className="text-base font-bold mb-4">Trip Dispatcher {isLoading && <span className="text-xs font-normal text-text-faint ml-2">(Loading...)</span>}</h1>

      {actionError && (
        <div className="border border-red bg-[rgba(226,88,92,0.14)] text-red rounded-lg px-3.5 py-3 text-xs mb-4 whitespace-pre-line">
          {actionError}
        </div>
      )}

      {/* Lifecycle stepper */}
      <div className="bg-panel-2 border border-border rounded-lg p-3.5 mb-4">
        <div className="text-xs text-text-dim uppercase tracking-wider mb-3 font-bold">Trip Lifecycle</div>
        <div className="flex items-center gap-1.5">
          {lifecycleSteps.map((step, i) => (
            <React.Fragment key={step}>
              <div className="flex flex-col items-center gap-1.5 text-[10px] text-text-faint">
                <div className={`w-3 h-3 rounded-full ${
                  i === 0 ? 'bg-green' : i === 1 ? 'bg-blue shadow-[0_0_0_3px_rgba(77,144,226,0.16)]' : 'bg-border'
                }`} />
                {step}
              </div>
              {i < lifecycleSteps.length - 1 && (
                <div className="flex-1 h-0.5 bg-border -mt-4" />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-[1.6fr_1fr] gap-4">
        {canManageTrips && (
          <div className="bg-panel-2 border border-border rounded-lg p-3.5">
            <div className="text-xs text-text-dim uppercase tracking-wider mb-3 font-bold">Create Trip</div>
            <form onSubmit={handleSubmit(onSubmit)}>
              <div className="flex flex-col gap-2.5">
                <div>
                  <label className={labelClass}>Source</label>
                  <input {...register('source')} className={inputClass} />
                  {errors.source && <div className={fieldErrorClass}>{errors.source.message}</div>}
                </div>
                <div>
                  <label className={labelClass}>Destination</label>
                  <input {...register('destination')} className={inputClass} />
                  {errors.destination && <div className={fieldErrorClass}>{errors.destination.message}</div>}
                </div>
                <div>
                  <label className={labelClass}>Vehicle (Available only)</label>
                  <select
                    value={selectedVehicleId}
                    onChange={e => setValue('vehicleId', e.target.value, { shouldValidate: true })}
                    className={inputClass}
                  >
                    <option value="">Select vehicle...</option>
                    {availableVehicles.map(v => (
                      <option key={v.id} value={v.id}>{v.name} · {v.capacityLabel} capacity</option>
                    ))}
                  </select>
                  {errors.vehicleId && <div className={fieldErrorClass}>{errors.vehicleId.message}</div>}
                </div>
                <div>
                  <label className={labelClass}>Driver (Available only)</label>
                  <select
                    value={selectedDriverId}
                    onChange={e => setValue('driverId', e.target.value, { shouldValidate: true })}
                    className={inputClass}
                  >
                    <option value="">Select driver...</option>
                    {availableDrivers.map(d => (
                      <option key={d.id} value={d.id}>{d.name}</option>
                    ))}
                  </select>
                  {errors.driverId && <div className={fieldErrorClass}>{errors.driverId.message}</div>}
                </div>
                <div>
                  <label className={labelClass}>Cargo Weight (kg)</label>
                  <input type="number" {...register('cargoWeight')} className={inputClass} />
                  {errors.cargoWeight && <div className={fieldErrorClass}>{errors.cargoWeight.message}</div>}
                </div>
                <div>
                  <label className={labelClass}>Planned Distance (km)</label>
                  <input type="number" {...register('plannedDistance')} className={inputClass} />
                  {errors.plannedDistance && <div className={fieldErrorClass}>{errors.plannedDistance.message}</div>}
                </div>
              </div>

              {submitError && (
                <div className="border border-red bg-[rgba(226,88,92,0.14)] text-red rounded-lg px-3.5 py-3 text-xs mt-3.5 whitespace-pre-line">
                  {submitError}
                </div>
              )}

              <div className="flex gap-2.5 mt-3.5">
                <button
                  type="submit"
                  className="bg-orange text-[#1a0f02] border-none py-2 px-3.5 rounded-md font-bold text-[12.5px] cursor-pointer hover:bg-orange-hover transition-colors"
                >
                  Dispatch
                </button>
                <button type="button" onClick={() => reset()} className="bg-panel-2 text-text-dim border border-border py-2 px-3.5 rounded-md text-[12.5px] cursor-pointer hover:text-text transition-colors">
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Live Board */}
        <div className="bg-panel-2 border border-border rounded-lg p-3.5">
          <div className="text-xs text-text-dim uppercase tracking-wider mb-3 font-bold">Live Board</div>
          {trips.map(trip => (
            <div key={trip.id} className="py-2.5 border-b border-border-soft last:border-b-0">
              <div className="flex justify-between items-center mb-1">
                <b className="text-xs">{trip.id}</b>
                <StatusPill status={trip.status} />
              </div>
              <div className="text-text-dim text-[11.5px]">
                {trip.source} → {trip.destination}
              </div>
              <div className="flex justify-between text-[11px] text-text-faint mt-1">
                <span>{getVehicleName(trip.vehicleId)} / {getDriverName(trip.driverId)}</span>
                <span>{trip.eta || ''}</span>
              </div>
              {/* Action buttons */}
              {canManageTrips && trip.status === 'Draft' && (
                <div className="flex gap-2 mt-2">
                  <button onClick={() => handleAction(() => dispatchTrip(trip.id))} className="bg-blue/20 text-blue border-none py-1 px-2 rounded text-[10px] font-bold cursor-pointer hover:bg-blue/30">Dispatch</button>
                  <button onClick={() => handleAction(() => cancelTrip(trip.id))} className="bg-red/20 text-red border-none py-1 px-2 rounded text-[10px] font-bold cursor-pointer hover:bg-red/30">Cancel</button>
                </div>
              )}
              {canManageTrips && trip.status === 'Dispatched' && (
                <div className="flex gap-2 mt-2">
                  <button onClick={() => handleComplete(trip.id)} className="bg-green/20 text-green border-none py-1 px-2 rounded text-[10px] font-bold cursor-pointer hover:bg-green/30">Complete</button>
                  <button onClick={() => handleAction(() => cancelTrip(trip.id))} className="bg-red/20 text-red border-none py-1 px-2 rounded text-[10px] font-bold cursor-pointer hover:bg-red/30">Cancel</button>
                </div>
              )}
            </div>
          ))}
          <div className="text-text-faint text-[11px] mt-3">
            On Complete: odometer → fuel log → expenses → Vehicle &amp; Driver Available
          </div>
        </div>
      </div>

      {/* Complete Trip Dialog */}
      {showCompleteDialog && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
          <div className="bg-panel border border-border rounded-lg p-6 w-[380px]">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-sm font-bold">Complete Trip {completingTripId}</h2>
              <button onClick={() => setShowCompleteDialog(false)} className="text-text-faint hover:text-text cursor-pointer bg-transparent border-none">
                <X size={16} />
              </button>
            </div>
            <div className="flex flex-col gap-3">
              <div>
                <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Final Odometer</label>
                <input type="number" value={finalOdometer} onChange={e => setFinalOdometer(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange" />
              </div>
              <div>
                <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Fuel Consumed (liters)</label>
                <input type="number" value={fuelConsumed} onChange={e => setFuelConsumed(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange" />
              </div>
            </div>
            <div className="flex gap-2.5 mt-4">
              <button
                onClick={handleCompleteSubmit}
                disabled={!finalOdometer || !fuelConsumed}
                className="bg-green text-[#0a1f10] border-none py-2 px-4 rounded-md font-bold text-[12.5px] cursor-pointer hover:opacity-90 transition-colors disabled:opacity-50"
              >
                Complete Trip
              </button>
              <button onClick={() => setShowCompleteDialog(false)} className="bg-panel-2 text-text-dim border border-border py-2 px-4 rounded-md text-[12.5px] cursor-pointer hover:text-text transition-colors">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
