import { useDaemonStore } from '../store/daemonStore';

export function PsychoanalyticDashboard() {
    const status = useDaemonStore((state) => state.status);
    const metrics = status?.consciousness_metrics?.psychoanalytic;

    if (!metrics || metrics.status === 'degraded') {
        return (
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <h2 className="text-2xl font-bold text-white mb-6">Psychic Apparatus</h2>
                <div className="text-gray-400 text-center py-8 italic">
                    Psychoanalytic dynamics initializing...
                </div>
            </div>
        );
    }

    const getAgentColor = (name: string) => {
        switch (name.toLowerCase()) {
            case 'id': return 'text-red-400';
            case 'ego': return 'text-blue-400';
            case 'superego': return 'text-purple-400';
            default: return 'text-gray-400';
        }
    };

    return (
        <div className="bg-gray-800 rounded-lg p-6 shadow-2xl border border-gray-700 overflow-hidden relative">
            <div className="absolute top-0 right-0 p-4 opacity-10 pointer-events-none">
                <span className="text-6xl font-serif">Φ</span>
            </div>

            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                <span className="text-purple-500">🧠</span> Psychic Apparatus (Ego/Id/Superego)
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                {/* Id Agent */}
                <div className="bg-gray-900/40 rounded-xl p-5 border border-red-900/20">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className={`text-lg font-bold ${getAgentColor('id')}`}>ID</h3>
                        <span className="text-xs bg-red-900/30 text-red-400 px-2 py-0.5 rounded uppercase tracking-tighter">Pleasure</span>
                    </div>
                    <div className="space-y-4">
                        <div>
                            <div className="flex justify-between text-xs mb-1">
                                <span className="text-gray-400">Libido</span>
                                <span className="text-gray-200">{(metrics.id.libido * 100).toFixed(0)}%</span>
                            </div>
                            <div className="w-full bg-gray-800 rounded-full h-1.5 overflow-hidden">
                                <div className="h-full bg-red-500" style={{ width: `${metrics.id.libido * 100}%` }}></div>
                            </div>
                        </div>
                        <div>
                            <div className="flex justify-between text-xs mb-1">
                                <span className="text-gray-400">Satisfaction</span>
                                <span className="text-gray-200">{(metrics.id.satisfaction * 100).toFixed(0)}%</span>
                            </div>
                            <div className="w-full bg-gray-800 rounded-full h-1.5 overflow-hidden">
                                <div className="h-full bg-red-400" style={{ width: `${metrics.id.satisfaction * 100}%` }}></div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Ego Agent */}
                <div className="bg-gray-900/40 rounded-xl p-5 border border-blue-900/20">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className={`text-lg font-bold ${getAgentColor('ego')}`}>EGO</h3>
                        <span className="text-xs bg-blue-900/30 text-blue-400 px-2 py-0.5 rounded uppercase tracking-tighter">Reality</span>
                    </div>
                    <div className="space-y-4">
                        <div>
                            <div className="flex justify-between text-xs mb-1">
                                <span className="text-gray-400">Adaptation</span>
                                <span className="text-gray-200">{(metrics.ego.adaptation * 100).toFixed(0)}%</span>
                            </div>
                            <div className="w-full bg-gray-800 rounded-full h-1.5 overflow-hidden">
                                <div className="h-full bg-blue-500" style={{ width: `${metrics.ego.adaptation * 100}%` }}></div>
                            </div>
                        </div>
                        <div>
                            <div className="text-xs text-gray-400 mb-2">Defenses:</div>
                            <div className="flex flex-wrap gap-1">
                                {metrics.ego.active_defenses.map((def: string) => (
                                    <span key={def} className="text-[10px] bg-blue-900/20 text-blue-300 px-1.5 py-0.5 rounded border border-blue-800/30">
                                        {def}
                                    </span>
                                ))}
                                {metrics.ego.active_defenses.length === 0 && <span className="text-[10px] text-gray-500 italic">None active</span>}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Superego Agent */}
                <div className="bg-gray-900/40 rounded-xl p-5 border border-purple-900/20">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className={`text-lg font-bold ${getAgentColor('superego')}`}>SUPEREGO</h3>
                        <span className="text-xs bg-purple-900/30 text-purple-400 px-2 py-0.5 rounded uppercase tracking-tighter">Moral</span>
                    </div>
                    <div className="space-y-4">
                        <div>
                            <div className="flex justify-between text-xs mb-1">
                                <span className="text-gray-400">Strictness</span>
                                <span className="text-gray-200">{(metrics.superego.strictness * 100).toFixed(0)}%</span>
                            </div>
                            <div className="w-full bg-gray-800 rounded-full h-1.5 overflow-hidden">
                                <div className="h-full bg-purple-500" style={{ width: `${metrics.superego.strictness * 100}%` }}></div>
                            </div>
                        </div>
                        <div>
                            <div className="flex justify-between text-xs mb-1">
                                <span className="text-gray-400">Moral Balance</span>
                                <div className="flex-1 mx-4 bg-gray-800 rounded-full h-1.5 relative top-1">
                                    <div
                                        className={`absolute h-full ${metrics.superego.judgment_balance >= 0 ? 'bg-green-500' : 'bg-red-500'}`}
                                        style={{
                                            left: '50%',
                                            width: `${Math.abs(metrics.superego.judgment_balance) * 50}%`,
                                            transform: metrics.superego.judgment_balance < 0 ? 'translateX(-100%)' : 'none'
                                        }}
                                    ></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Psychic State Overview */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                {[
                    { label: 'Tension', val: metrics.state.tension, color: 'text-orange-400' },
                    { label: 'Anxiety', val: metrics.state.anxiety, color: 'text-red-400' },
                    { label: 'Guilt', val: metrics.state.guilt, color: 'text-purple-400' },
                    { label: 'Reality Adaptation', val: metrics.state.reality_adaptation, color: 'text-blue-400' }
                ].map((item) => (
                    <div key={item.label} className="bg-gray-900/30 p-3 rounded-lg border border-gray-700/50">
                        <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">{item.label}</div>
                        <div className={`text-xl font-mono font-bold ${item.color}`}>
                            {item.val.toFixed(3)}
                        </div>
                    </div>
                ))}
            </div>

            {/* Recent Conflicts */}
            {metrics.recent_conflicts && metrics.recent_conflicts.length > 0 && (
                <div className="mt-4">
                    <h3 className="text-sm font-semibold text-gray-300 mb-3 uppercase tracking-widest text-center">Conflict Resolution History</h3>
                    <div className="space-y-2">
                        {metrics.recent_conflicts.map((conflict: any, idx: number) => (
                            <div key={idx} className="bg-gray-900/60 p-3 rounded-lg flex items-center justify-between text-xs border-l-2 border-purple-500 group hover:bg-gray-900/80 transition-all">
                                <div className="flex-1">
                                    <div className="text-gray-300 font-medium group-hover:text-white">{conflict.chosen}</div>
                                    <div className="text-gray-500 mt-1">Defense: {conflict.defense || 'Direct Action'}</div>
                                </div>
                                <div className="text-right">
                                    <div className="text-purple-400 font-bold">{(conflict.quality * 100).toFixed(0)}%</div>
                                    <div className="text-[10px] text-gray-600 uppercase">Quality</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
