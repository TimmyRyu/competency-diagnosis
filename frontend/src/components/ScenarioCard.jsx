const GROUP_BG = {
  '핵심역량': 'bg-blue-50 border-blue-200',
  '리더십': 'bg-green-50 border-green-200',
  '직무역량': 'bg-amber-50 border-amber-200',
}
export default function ScenarioCard({ situation, groupName }) {
  return (
    <div className={`rounded-lg border-2 p-6 ${GROUP_BG[groupName] || 'bg-gray-50 border-gray-200'}`}>
      <span className="inline-block text-xs font-semibold px-2 py-1 rounded-full bg-white text-gray-600 mb-3">{groupName}</span>
      <p className="text-gray-800 leading-relaxed">{situation}</p>
    </div>
  )
}
