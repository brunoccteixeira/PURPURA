/**
 * H3 Risk Map Component using deck.gl
 */
import { useState, useMemo } from 'react';
import DeckGL from '@deck.gl/react';
import { H3HexagonLayer } from '@deck.gl/geo-layers';
import { Map as MapGL } from 'react-map-gl';
import type { MapViewState } from '@deck.gl/core';
import { getRiskColorRGBA } from '../../lib/utils/colors';
import { formatRiskScore } from '../../lib/utils/format';
import type { H3GridData } from '../../types/risk';

interface H3RiskMapProps {
  gridData: H3GridData | null;
  initialViewState?: Partial<MapViewState>;
  onHexClick?: (h3Index: string, riskScore: number) => void;
}

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || '';

export function H3RiskMap({
  gridData,
  initialViewState,
  onHexClick,
}: H3RiskMapProps) {
  const [viewState, setViewState] = useState<MapViewState>({
    latitude: initialViewState?.latitude || -15.7801,
    longitude: initialViewState?.longitude || -47.9292,
    zoom: initialViewState?.zoom || 6,
    pitch: initialViewState?.pitch || 45,
    bearing: initialViewState?.bearing || 0,
  });

  const [hoverInfo, setHoverInfo] = useState<{
    object: any;
    x: number;
    y: number;
  } | null>(null);

  // Transform heatmap data to array format for deck.gl
  const h3Data = useMemo(() => {
    if (!gridData?.heatmap) return [];

    return Object.entries(gridData.heatmap).map(([h3_index, risk_score]) => ({
      h3_index,
      risk_score,
    }));
  }, [gridData]);

  // Create H3 Hexagon Layer
  const layers = useMemo(() => {
    if (!h3Data.length) return [];

    return [
      new H3HexagonLayer({
        id: 'h3-risk-layer',
        data: h3Data,
        pickable: true,
        wireframe: false,
        filled: true,
        extruded: true,
        elevationScale: 50,
        getHexagon: (d: any) => d.h3_index,
        getFillColor: (d: any) => getRiskColorRGBA(d.risk_score, 180),
        getElevation: (d: any) => d.risk_score * 1000,
        onHover: (info: any) => setHoverInfo(info.object ? info : null),
        onClick: (info: any) => {
          if (info.object && onHexClick) {
            onHexClick(info.object.h3_index, info.object.risk_score);
          }
        },
        updateTriggers: {
          getFillColor: [h3Data],
          getElevation: [h3Data],
        },
      }),
    ];
  }, [h3Data, onHexClick]);

  return (
    <div className="relative w-full h-full">
      <DeckGL
        viewState={viewState}
        onViewStateChange={({ viewState }: any) => setViewState(viewState)}
        controller={true}
        layers={layers}
      >
        {MAPBOX_TOKEN ? (
          <MapGL
            mapboxAccessToken={MAPBOX_TOKEN}
            mapStyle="mapbox://styles/mapbox/light-v11"
          />
        ) : (
          <div className="absolute inset-0 bg-gray-100" />
        )}
      </DeckGL>

      {/* Tooltip */}
      {hoverInfo?.object && (
        <div
          className="absolute z-10 pointer-events-none bg-white px-3 py-2 rounded-lg shadow-lg border border-gray-200"
          style={{
            left: hoverInfo.x + 10,
            top: hoverInfo.y + 10,
          }}
        >
          <div className="text-sm">
            <div className="font-semibold text-gray-900">
              Risco: {formatRiskScore(hoverInfo.object.risk_score)}
            </div>
            <div className="text-xs text-gray-600 mt-1">
              H3: {hoverInfo.object.h3_index.slice(0, 10)}...
            </div>
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="absolute bottom-4 right-4 bg-white px-4 py-3 rounded-lg shadow-lg border border-gray-200">
        <div className="text-sm font-semibold text-gray-900 mb-2">
          Nível de Risco
        </div>
        <div className="space-y-1">
          {[
            { label: 'Baixo', color: '#10b981' },
            { label: 'Moderado', color: '#f59e0b' },
            { label: 'Alto', color: '#f97316' },
            { label: 'Crítico', color: '#ef4444' },
          ].map((item) => (
            <div key={item.label} className="flex items-center gap-2">
              <div
                className="w-4 h-4 rounded"
                style={{ backgroundColor: item.color }}
              />
              <span className="text-xs text-gray-700">{item.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Loading indicator */}
      {!gridData && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-50 bg-opacity-75">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto" />
            <p className="mt-3 text-sm text-gray-600">Carregando mapa...</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default H3RiskMap;
