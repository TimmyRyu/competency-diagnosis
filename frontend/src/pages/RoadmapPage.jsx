import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import axios from 'axios'
import useDiagnosisStore from '../store/useDiagnosisStore'
import RoadmapTimeline from '../components/RoadmapTimeline'

export default function RoadmapPage() {
  const navigate = useNavigate()
  const { respondentId, roadmapItems, setRoadmapItems, respondentInfo } = useDiagnosisStore()
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  if (!respondentId) { navigate('/'); return null }

  const totalCourses = Object.values(roadmapItems).flat().length
  const totalHours = Object.values(roadmapItems).flat().reduce((s, i) => s + (i.duration_hours || 0), 0)

  const handleSave = async () => {
    setSaving(true)
    try {
      const items = []
      let idx = 0
      for (const [phase, phaseItems] of Object.entries(roadmapItems))
        for (const item of phaseItems)
          items.push({ id: item.id, order_index: idx++, phase })
      await axios.put(`/api/roadmap/${respondentId}`, { items })
      setSaved(true)
    } catch { alert('저장 중 오류가 발생했습니다.') }
    finally { setSaving(false) }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">훈련 로드맵</h2>
          <p className="text-gray-600 mt-1">교육과정을 드래그하여 단계 간 이동하거나 순서를 변경할 수 있습니다.</p>
        </div>
        <div className="text-right text-sm text-gray-500">
          <p>{respondentInfo.name} ({respondentInfo.organization || '-'})</p>
          <p>총 {totalCourses}개 | {totalHours}시간</p>
        </div>
      </div>
      <RoadmapTimeline phases={roadmapItems} onUpdate={(p) => { setRoadmapItems(p); setSaved(false) }} />
      <div className="flex justify-between items-center no-print">
        <button onClick={() => navigate('/courses')} className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition">교육과정으로 돌아가기</button>
        <div className="flex gap-3">
          <button onClick={() => window.print()} className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition">인쇄</button>
          <button onClick={handleSave} disabled={saving}
            className={`px-6 py-2 rounded-md text-white transition disabled:opacity-50 ${saved ? 'bg-green-600 hover:bg-green-700' : 'bg-blue-600 hover:bg-blue-700'}`}>
            {saving ? '저장 중...' : saved ? '저장 완료 ✓' : '저장'}
          </button>
        </div>
      </div>
    </div>
  )
}
