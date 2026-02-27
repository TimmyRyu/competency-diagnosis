import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import { GROUP_COLORS } from '../data/constants'

export default function CompetencyChart({ results }) {
  if (!results.length) return null
  const data = results.map((r) => ({ competency: r.competency_name, score: parseFloat((r.score || 0).toFixed(1)) }))
  const groups = [...new Set(results.map((r) => r.group_name))]
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-3">역량 진단 결과</h3>
      <div className="flex gap-2 mb-4">
        {groups.map((g) => (
          <span key={g} className="text-xs px-2 py-1 rounded-full text-white" style={{ backgroundColor: GROUP_COLORS[g] || '#6B7280' }}>{g}</span>
        ))}
      </div>
      <ResponsiveContainer width="100%" height={380}>
        <RadarChart data={data}>
          <PolarGrid />
          <PolarAngleAxis dataKey="competency" tick={{ fontSize: 11 }} />
          <PolarRadiusAxis angle={90} domain={[0, 'auto']} tick={{ fontSize: 10 }} />
          <Radar name="역량 점수" dataKey="score" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.3} />
          <Tooltip />
          <Legend />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}
