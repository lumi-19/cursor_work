import React, { useState, useEffect } from 'react';
import { citiesAPI, comparisonAPI } from '../../services/api';

interface ComparisonResult {
  comparison_date: string;
  cities: Array<{
    city_id: number;
    city_name: string;
    aqi_value: number;
    aqi_category: string;
    pm25: number | null;
    pm10: number | null;
    o3: number | null;
    no2: number | null;
    co: number | null;
    so2: number | null;
  }>;
  statistics: {
    highest_aqi: number;
    lowest_aqi: number;
    average_aqi: number;
  };
}

const ComparisonPanel: React.FC = () => {
  const [selectedCityIds, setSelectedCityIds] = useState<number[]>([]);
  const [cities, setCities] = useState<any[]>([]);
  const [comparison, setComparison] = useState<ComparisonResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchCities();
  }, []);

  const fetchCities = async () => {
    try {
      const response = await citiesAPI.getAll({ limit: 50 });
      if (response.success && response.data) {
        setCities(response.data);
      }
    } catch (error) {
      console.error('Error fetching cities:', error);
    }
  };

  const handleCityToggle = (cityId: number) => {
    setSelectedCityIds((prev) => {
      if (prev.includes(cityId)) {
        return prev.filter((id) => id !== cityId);
      } else if (prev.length < 5) {
        // Limit to 5 cities
        return [...prev, cityId];
      }
      return prev;
    });
  };

  const handleCompare = async () => {
    if (selectedCityIds.length < 2) {
      alert('Please select at least 2 cities to compare');
      return;
    }

    setLoading(true);
    try {
      const cityIdsString = selectedCityIds.join(',');
      const response = await comparisonAPI.compareAQI({ city_ids: cityIdsString });
      
      if (response.success) {
        setComparison(response);
      }
    } catch (error) {
      console.error('Error comparing cities:', error);
      alert('Error comparing cities. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getAQIColor = (aqi: number) => {
    if (aqi <= 50) return 'bg-green-500';
    if (aqi <= 100) return 'bg-yellow-500';
    if (aqi <= 150) return 'bg-orange-500';
    if (aqi <= 200) return 'bg-red-500';
    if (aqi <= 300) return 'bg-purple-500';
    return 'bg-red-900';
  };

  return (
    <div className="p-4 space-y-4">
      <h3 className="text-lg font-semibold">Compare Cities</h3>

      {/* City Selection */}
      <div>
        <label className="block text-sm font-medium mb-2">
          Select Cities (2-5 cities)
        </label>
        <div className="space-y-2 max-h-48 overflow-y-auto border rounded-md p-2">
          {cities.map((city) => (
            <label
              key={city.id}
              className="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 p-1 rounded"
            >
              <input
                type="checkbox"
                checked={selectedCityIds.includes(city.id)}
                onChange={() => handleCityToggle(city.id)}
                disabled={!selectedCityIds.includes(city.id) && selectedCityIds.length >= 5}
                className="rounded"
              />
              <span className="text-sm">{city.name}, {city.country}</span>
            </label>
          ))}
        </div>
        <p className="text-xs text-gray-500 mt-1">
          {selectedCityIds.length} of 5 cities selected
        </p>
      </div>

      {/* Compare Button */}
      <button
        onClick={handleCompare}
        disabled={selectedCityIds.length < 2 || loading}
        className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
      >
        {loading ? 'Comparing...' : 'Compare Cities'}
      </button>

      {/* Comparison Results */}
      {comparison && (
        <div className="space-y-4 mt-4 border-t pt-4">
          <h4 className="font-semibold">Comparison Results</h4>
          
          {/* Statistics */}
          {comparison.statistics && (
            <div className="bg-gray-50 p-3 rounded-md space-y-1 text-sm">
              <p><strong>Highest AQI:</strong> {comparison.statistics.highest_aqi}</p>
              <p><strong>Lowest AQI:</strong> {comparison.statistics.lowest_aqi}</p>
              <p><strong>Average AQI:</strong> {comparison.statistics.average_aqi.toFixed(1)}</p>
            </div>
          )}

          {/* City Comparison */}
          <div className="space-y-3">
            {comparison.cities.map((city) => (
              <div
                key={city.city_id}
                className="border rounded-md p-3 space-y-2"
              >
                <div className="flex items-center justify-between">
                  <h5 className="font-medium">{city.city_name}</h5>
                  <span
                    className={`px-3 py-1 rounded-full text-white text-sm ${getAQIColor(
                      city.aqi_value
                    )}`}
                  >
                    AQI: {city.aqi_value}
                  </span>
                </div>
                <div className="text-xs text-gray-600 space-y-1">
                  {city.pm25 && <p>PM2.5: {city.pm25.toFixed(1)} µg/m³</p>}
                  {city.pm10 && <p>PM10: {city.pm10.toFixed(1)} µg/m³</p>}
                  {city.o3 && <p>O₃: {city.o3.toFixed(1)} ppb</p>}
                  {city.no2 && <p>NO₂: {city.no2.toFixed(1)} ppb</p>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ComparisonPanel;
