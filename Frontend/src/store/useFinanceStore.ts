import { create } from 'zustand';
import type { FuelLog, Expense } from '../types';
import { seedFuelLogs, seedExpenses } from '../mock-data/finance';

interface FinanceState {
  fuelLogs: FuelLog[];
  expenses: Expense[];
  addFuelLog: (log: FuelLog) => void;
  addExpense: (expense: Omit<Expense, 'id'>) => void;
}

let nextExpId = seedExpenses.length + 1;

export const useFinanceStore = create<FinanceState>((set) => ({
  fuelLogs: [...seedFuelLogs],
  expenses: [...seedExpenses],

  addFuelLog: (log) => {
    set(state => ({
      fuelLogs: [...state.fuelLogs, log],
    }));
  },

  addExpense: (expense) => {
    const id = `e${nextExpId++}`;
    set(state => ({
      expenses: [...state.expenses, { ...expense, id }],
    }));
  },
}));
