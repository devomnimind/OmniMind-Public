/**
 * Loading skeleton components for better UX during data fetching
 */

export function CardSkeleton() {
  return (
    <div className="bg-gray-800 rounded-lg p-6 animate-pulse">
      <div className="h-6 bg-gray-700 rounded w-1/3 mb-4"></div>
      <div className="space-y-3">
        <div className="h-4 bg-gray-700 rounded w-full"></div>
        <div className="h-4 bg-gray-700 rounded w-5/6"></div>
        <div className="h-4 bg-gray-700 rounded w-4/6"></div>
      </div>
    </div>
  );
}

export function MetricsSkeleton() {
  return (
    <div className="bg-gray-800 rounded-lg p-6 animate-pulse">
      <div className="h-6 bg-gray-700 rounded w-1/2 mb-6"></div>
      <div className="space-y-6">
        {[1, 2, 3].map((i) => (
          <div key={i}>
            <div className="flex justify-between mb-2">
              <div className="h-4 bg-gray-700 rounded w-1/4"></div>
              <div className="h-4 bg-gray-700 rounded w-1/6"></div>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-3"></div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function TaskListSkeleton() {
  return (
    <div className="bg-gray-800 rounded-lg p-6 animate-pulse">
      <div className="h-6 bg-gray-700 rounded w-1/4 mb-6"></div>
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-gray-700/50 rounded-lg p-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1 space-y-2">
                <div className="h-5 bg-gray-600 rounded w-1/2"></div>
                <div className="h-4 bg-gray-600 rounded w-3/4"></div>
              </div>
              <div className="h-6 bg-gray-600 rounded w-16"></div>
            </div>
            <div className="grid grid-cols-4 gap-3">
              {[1, 2, 3, 4].map((j) => (
                <div key={j} className="h-12 bg-gray-600 rounded"></div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function AgentStatusSkeleton() {
  return (
    <div className="bg-gray-800 rounded-lg p-6 animate-pulse">
      <div className="flex items-center justify-between mb-6">
        <div className="h-6 bg-gray-700 rounded w-1/3"></div>
        <div className="h-4 bg-gray-700 rounded w-1/6"></div>
      </div>
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="border-l-4 border-gray-600 rounded-lg p-4 bg-gray-700/20">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-gray-600 rounded-full"></div>
                <div className="space-y-2">
                  <div className="h-5 bg-gray-600 rounded w-32"></div>
                  <div className="h-3 bg-gray-600 rounded w-24"></div>
                </div>
              </div>
              <div className="h-6 bg-gray-600 rounded w-16"></div>
            </div>
            <div className="grid grid-cols-4 gap-3 mb-3">
              {[1, 2, 3, 4].map((j) => (
                <div key={j} className="h-14 bg-gray-600/30 rounded"></div>
              ))}
            </div>
            <div className="grid grid-cols-3 gap-3">
              {[1, 2, 3].map((j) => (
                <div key={j} className="h-10 bg-gray-600/30 rounded"></div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function DashboardSkeleton() {
  return (
    <div className="min-h-screen bg-gray-900">
      <header className="bg-gray-800 border-b border-gray-700 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 animate-pulse">
          <div className="flex items-center justify-between">
            <div className="h-8 bg-gray-700 rounded w-64"></div>
            <div className="h-8 bg-gray-700 rounded w-32"></div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <CardSkeleton />
            <AgentStatusSkeleton />
            <TaskListSkeleton />
          </div>
          <div className="space-y-6">
            <MetricsSkeleton />
            <CardSkeleton />
          </div>
        </div>
      </main>
    </div>
  );
}
