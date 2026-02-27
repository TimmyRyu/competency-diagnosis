import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import axios from 'axios'
import useDiagnosisStore from '../store/useDiagnosisStore'
import CompetencyChart from '../components/CompetencyChart'
import DraggableList from '../components/DraggableList'
import { GROUP_COLORS } from '../data/constants'

export default function ResultPage() {
  const navigate = useNavigate()
  const { priorityResults, reorderPriority, respondentId } = useDiagnosisStore()
  if (!priorityResults.length) { navigate('/'); return null }

  const handleReorder = async (newOrder) => {
    const updated = newOrder.map((item, i) => ({ ...item, priority_rank: i + 1 }))
    reorderPriority(updated)
    try {
      await axios.put(`/api/diagnosis/${respondentId}`, {
        rankings: updated.map((r) => ({ competency_id: r.competency_id, priority_rank: r.priority_rank, is_active: r.is_active }))
      })
    } catch {}
  }

  const handleRemove = async (competencyId) => {
    const updated = priorityResults
      .filter((r) => r.competency_id !== competencyId)
      .map((item, i) => ({ ...item, priority_rank: i + 1 }))
    reorderPriority(updated)
    try {
      await axios.put(`/api/diagnosis/${respondentId}`, {
        rankings: [
          ...updated.map((r) => ({ competency_id: r.competency_id, priority_rank: r.priority_rank, is_active: 1 })),
          { competency_id: competencyId, priority_rank: 999, is_active: 0 },
        ]
      })
    } catch {}
  }

  return (
    <div className="space-y-6">
      <CompetencyChart results={priorityResults} />
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-1">우선순위 조정</h3>
        <p className="text-sm text-gray-500 mb-4">드래그하여 역량 우선순위를 변경하거나 필요 없는 역량을 삭제할 수 있습니다.</p>
        <DraggableList
          items={priorityResults} onReorder={handleReorder}
          getId={(item) => `comp-${item.competency_id}`}
          renderItem={(item, index) => (
            <div className="bg-gray-50 rounded-lg p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-sm font-bold text-gray-400 w-6">{index + 1}</span>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-800">{item.competency_name}</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded text-white" style={{ backgroundColor: GROUP_COLORS[item.group_name] || '#6B7280' }}>{item.group_name}</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-0.5">
                    선택 {item.selection_count}회 | 평균 {parseFloat(item.avg_likert).toFixed(1)} | 점수 {parseFloat(item.score).toFixed(1)}
                  </p>
                </div>
              </div>
              <button onClick={() => handleRemove(item.competency_id)} className="text-red-400 hover:text-red-600 px-2">✕</button>
            </div>
          )}
        />
      </div>
      <div className="flex justify-between">
        <button onClick={() => navigate('/diagnosis')} className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition">다시 진단하기</button>
        <button onClick={() => navigate('/courses')} className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition">교육과정 추천 보기</button>
      </div>
    </div>
  )
}
