import React, { useState, useMemo } from 'react';
import { useTripsStore } from '../store/useTripsStore';
import { useFleetStore } from '../store/useFleetStore';
import { useDriversStore } from '../store/useDriversStore';
import { StatusPill } from '../components/shared/StatusPill';
import { isLicenseExpired } from '../lib/calculations';
import { X } from 'lucide-react';

export const TripsPage: React.FC = () => {
  const { trips, createTrip, dispatchTrip, completeTrip, cancelTrip } = useTripsStore();
  const { vehicles, getAvailableVehicles } = useFleetStore();
  const { drivers, getAvailableDrivers } = useDriversStore();

  // Create Trip form
  const [source, setSource] = useState('Gandhinagar Depot');
  const [destination, setDestination] = useState('Ahmedabad Hub');
  const [selectedVehicleId, setSelectedVehicleId] = useState('');
  const [selectedDriverId, setSelectedDriverId] = useState('');
  const [cargoWeight, setCargoWeight] = useState('');
  const [plannedDistance, setPlannedDistance] = useState('');

  // Complete trip dialog
  const [showCompleteDialog, setShowCompleteDialog] = useState(false);
  const [completingTripId, setCompletingTripId] = useState('');
  const [finalOdometer, setFinalOdometer] = useState('');
  const [fuelConsumed, setFuelConsumed] = useState('');

  const availableVehicles = getAvailableVehicles();
  const availableDrivers = getAvailableDrivers();

  const selectedVehicle = vehicles.find(v => v.id === selectedVehicleId);
  const selectedDriver = drivers.find(d => d.id === selectedDriverId);

  // Validation errors
  const validationErrors = useMemo(() => {
    const errors: string[] = [];
    const weight = parseFloat(cargoWeight);

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
  }, [selectedVehicleId, selectedDriverId, cargoWeight, selectedVehicle, selectedDriver]);

  const canDispatch = source && destination && selectedVehicleId && selectedDriverId &&
    cargoWeight && plannedDistance && validationErrors.length === 0;

  const handleCreateAndDispatch = () => {
    if (!canDispatch) return;
    createTrip({
      source,
      destination,
      vehicleId: selectedVehicleId,
      driverId: selectedDriverId,
      cargoWeight: parseFloat(cargoWeight),
      plannedDistance: parseFloat(plannedDistance),
      eta: `${Math.round(parseFloat(plannedDistance) / 60 * 60)} min`,
    });
    // Dispatch the last created trip
    const lastTrip = useTripsStore.getState().trips[useTripsStore.getState().trips.length - 1];
    dispatchTrip(lastTrip.id);

    // Reset form
    setSource(''); setDestination(''); setSelectedVehicleId('');
    setSelectedDriverId(''); setCargoWeight(''); setPlannedDistance('');
  };

  const handleComplete = (tripId: string) => {
    setCompletingTripId(tripId);
    setShowCompleteDialog(true);
    setFinalOdometer('');
    setFuelConsumed('');
  };

  const handleCompleteSubmit = () => {
    if (!finalOdometer || !fuelConsumed) return;
    completeTrip(completingTripId, parseInt(finalOdometer), parseFloat(fuelConsumed));
    setShowCompleteDialog(false);
  };

  const getVehicleName = (id: string | null) => vehicles.find(v => v.id === id)?.name || 'Unassigned';
  const getDriverName = (id: string | null) => drivers.find(d => d.id === id)?.name || 'Unassigned';

  const lifecycleSteps = ['Draft', 'Dispatched', 'Completed', 'Cancelled'];

  return (
    <div>
      <h1 className="text-base font-bold mb-4">Trip Dispatcher</h1>

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

      <div className="grid grid-cols-[1.6fr_1fr] gap-4">
        {/* Create Trip Form */}
        <div className="bg-panel-2 border border-border rounded-lg p-3.5">
          <div className="text-xs text-text-dim uppercase tracking-wider mb-3 font-bold">Create Trip</div>
          <div className="flex flex-col gap-2.5">
            <div>
              <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Source</label>
              <input value={source} onChange={e => setSource(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange" />
            </div>
            <div>
              <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Destination</label>
              <input value={destination} onChange={e => setDestination(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange" />
            </div>
            <div>
              <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Vehicle (Available only)</label>
              <select value={selectedVehicleId} onChange={e => setSelectedVehicleId(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange">
                <option value="">Select vehicle...</option>
                {availableVehicles.map(v => (
                  <option key={v.id} value={v.id}>{v.name} · {v.capacityLabel} capacity</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Driver (Available only)</label>
              <select value={selectedDriverId} onChange={e => setSelectedDriverId(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange">
                <option value="">Select driver...</option>
                {availableDrivers.map(d => (
                  <option key={d.id} value={d.id}>{d.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Cargo Weight (kg)</label>
              <input type="number" value={cargoWeight} onChange={e => setCargoWeight(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange" />
            </div>
            <div>
              <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Planned Distance (km)</label>
              <input type="number" value={plannedDistance} onChange={e => setPlannedDistance(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange" />
            </div>
          </div>

          {/* Validation errors */}
          {validationErrors.length > 0 && (
            <div className="border border-red bg-[rgba(226,88,92,0.14)] text-red rounded-lg px-3.5 py-3 text-xs mt-3.5 whitespace-pre-line">
              {validationErrors.join('\n')}
            </div>
          )}

          <div className="flex gap-2.5 mt-3.5">
            <button
              onClick={handleCreateAndDispatch}
              disabled={!canDispatch}
              className={`border-none py-2 px-3.5 rounded-md font-bold text-[12.5px] cursor-pointer transition-colors ${
                canDispatch
                  ? 'bg-orange text-[#1a0f02] hover:bg-orange-hover'
                  : 'bg-transparent text-text-dim border border-border opacity-50 cursor-not-allowed'
              }`}
            >
              {canDispatch ? 'Dispatch' : 'Dispatch (disabled)'}
            </button>
            <button className="bg-panel-2 text-text-dim border border-border py-2 px-3.5 rounded-md text-[12.5px] cursor-pointer hover:text-text transition-colors">
              Cancel
            </button>
          </div>
        </div>

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
              {trip.status === 'Draft' && (
                <div className="flex gap-2 mt-2">
                  <button onClick={() => dispatchTrip(trip.id)} className="bg-blue/20 text-blue border-none py-1 px-2 rounded text-[10px] font-bold cursor-pointer hover:bg-blue/30">Dispatch</button>
                  <button onClick={() => cancelTrip(trip.id)} className="bg-red/20 text-red border-none py-1 px-2 rounded text-[10px] font-bold cursor-pointer hover:bg-red/30">Cancel</button>
                </div>
              )}
              {trip.status === 'Dispatched' && (
                <div className="flex gap-2 mt-2">
                  <button onClick={() => handleComplete(trip.id)} className="bg-green/20 text-green border-none py-1 px-2 rounded text-[10px] font-bold cursor-pointer hover:bg-green/30">Complete</button>
                  <button onClick={() => cancelTrip(trip.id)} className="bg-red/20 text-red border-none py-1 px-2 rounded text-[10px] font-bold cursor-pointer hover:bg-red/30">Cancel</button>
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
