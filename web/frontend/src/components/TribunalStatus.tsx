import { useEffect, useState } from 'react';
import { apiService } from '../services/api';

interface TribunalData {
  status: string;
  activity_score: number;
  proposals: Array<{
    id: string;
    title: string;
    description: string;
    severity: 'info' | 'success' | 'warning' | 'error';
  }>;
  metrics: {
    attacks_count: number;
    duration_hours: number;
  };
}

export function TribunalStatus() {
  const [data, setData] = useState<TribunalData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTribunal = async () => {
      try {
        const result = await apiService.getTribunalActivity();
        setData(result);
      } catch (err) {
        setError('Failed to load Tribunal status');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchTribunal();
    const interval = setInterval(fetchTribunal, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="glass-card p-6 animate-pulse">Loading Tribunal...</div>;
  if (error) return <div className="glass-card p-6 text-red-500">{error}</div>;
  if (!data) return null;

  return (
    <div className="glass-card p-6 relative overflow-hidden group hover:shadow-neon-red transition-all duration-300">
      <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
        <span className="text-6xl">⚖️</span>
      </div>

      <h2 className="text-xl font-bold text-gradient-neon mb-4 flex items-center gap-2">
        <span>⚖️</span> Tribunal do Diabo
      </h2>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-dark-200/50 p-3 rounded-lg">
          <div className="text-sm text-gray-400">Status</div>
          <div className={`font-mono font-bold ${data.status === 'running' ? 'text-yellow-400 animate-pulse' : 'text-green-400'}`}>
            {data.status.toUpperCase()}
          </div>
        </div>
        <div className="bg-dark-200/50 p-3 rounded-lg">
          <div className="text-sm text-gray-400">Activity Score</div>
          <div className="font-mono font-bold text-neon-blue">
            {(data.activity_score * 100).toFixed(0)}%
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-gray-300">Proposals</h3>
        {data.proposals.length === 0 ? (
          <div className="text-sm text-gray-500 italic">No active proposals</div>
        ) : (
          data.proposals.map((prop) => (
            <div key={prop.id} className={`p-3 rounded border ${
              prop.severity === 'success' ? 'border-green-500/30 bg-green-500/10' :
              prop.severity === 'warning' ? 'border-yellow-500/30 bg-yellow-500/10' :
              'border-blue-500/30 bg-blue-500/10'
            }`}>
              <div className="font-bold text-sm mb-1">{prop.title}</div>
              <div className="text-xs text-gray-400">{prop.description}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
