/**
 * Loading Skeleton Components for better UX
 */

export function CardSkeleton() {
  return (
    <div className="card animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
      <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
      <div className="h-6 bg-gray-200 rounded w-1/4"></div>
    </div>
  );
}

export function ChartSkeleton() {
  return (
    <div className="card animate-pulse">
      <div className="mb-6">
        <div className="h-6 bg-gray-200 rounded w-1/2 mb-2"></div>
        <div className="h-4 bg-gray-200 rounded w-3/4"></div>
      </div>
      <div className="h-80 bg-gray-100 rounded-lg flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
          <p className="mt-2 text-sm text-gray-500">Carregando dados...</p>
        </div>
      </div>
    </div>
  );
}

export function MapSkeleton() {
  return (
    <div className="card h-full animate-pulse">
      <div className="h-full bg-gray-100 rounded-lg flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
          <p className="mt-3 text-sm text-gray-600">Carregando mapa geoespacial...</p>
        </div>
      </div>
    </div>
  );
}

export function RiskCardsSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {[1, 2, 3, 4].map((i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  );
}

export function HeaderSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="h-8 bg-gray-200 rounded w-1/4 mb-2"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2"></div>
    </div>
  );
}
