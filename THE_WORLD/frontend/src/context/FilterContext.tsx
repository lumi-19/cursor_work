import React, { createContext, useContext, useState, ReactNode } from 'react';

interface FilterState {
  disasterType: string[];
  dateRange: { start: string | null; end: string | null };
  aqiRange: { min: number | null; max: number | null };
  citySearch: string;
  selectedCities: number[];
}

interface FilterContextType {
  filters: FilterState;
  setFilters: (filters: Partial<FilterState>) => void;
  resetFilters: () => void;
}

const defaultFilters: FilterState = {
  disasterType: [],
  dateRange: { start: null, end: null },
  aqiRange: { min: null, max: null },
  citySearch: '',
  selectedCities: [],
};

const FilterContext = createContext<FilterContextType | undefined>(undefined);

export const FilterProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [filters, setFiltersState] = useState<FilterState>(defaultFilters);

  const setFilters = (newFilters: Partial<FilterState>) => {
    setFiltersState((prev) => ({ ...prev, ...newFilters }));
  };

  const resetFilters = () => {
    setFiltersState(defaultFilters);
  };

  return (
    <FilterContext.Provider value={{ filters, setFilters, resetFilters }}>
      {children}
    </FilterContext.Provider>
  );
};

export const useFilters = () => {
  const context = useContext(FilterContext);
  if (!context) {
    throw new Error('useFilters must be used within FilterProvider');
  }
  return context;
};
