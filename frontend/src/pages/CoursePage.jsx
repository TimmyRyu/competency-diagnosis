import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import useDiagnosisStore from '../store/useDiagnosisStore'

const SEMESTER_BADGE = { '상반기': 'bg-green-100 text-green-700', '하반기': 'bg-orange-100 text-orange-700', '상시': 'bg-gray-100 text-gray-700' }

export default function CoursePage() {
  const navigate = useNavigate()
  const { respondentId, coursesByCompetency, setCoursesByCompetency, setRoadmapItems } = useDiagnosisStore()
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)

  useEffect(() => {
    if (!respondentId) { navigate('/'); return }
    axios.get(`/api/courses/${respondentId}`)
      .then((res) => setCoursesByCompetency(res.data))
      .catch(() => alert('교육과정 조회 중 오류가 발생했습니다.'))
      .finally(() => setLoading(false))
  }, [respondentId])

  const handleGenerate = async () => {
    setGenerating(true)
    try {
      await axios.post(`/api/roadmap/${respondentId}/generate`)
      const res = await axios.get(`/api/roadmap/${respondentId}`)
      setRoadmapItems(res.data)
      navigate('/roadmap')
    } catch { alert('로드맵 생성 중 오류가 발생했습니다.') }
    finally { setGenerating(false) }
  }

  if (loading) return <div className="text-center py-12 text-gray-500">교육과정을 불러오는 중...</div>

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-800">추천 교육과정</h2>
        <p className="text-gray-600 mt-1">우선순위 높은 역량별 교육과정을 확인하세요.</p>
      </div>
      {coursesByCompetency.map((group) => (
        <div key={group.competency_id} className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-sm font-bold text-gray-400">#{group.priority_rank}</span>
            <h3 className="text-lg font-semibold text-gray-800">{group.competency_name}</h3>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            {group.courses.map((course) => (
              <div key={course.id} className="border border-gray-200 rounded-lg p-4">
                <h4 className="font-medium text-gray-800 text-sm">{course.name}</h4>
                <p className="text-xs text-gray-500 mt-1">{course.description}</p>
                <div className="flex items-center gap-2 mt-3">
                  <span className={`text-[10px] px-2 py-0.5 rounded-full ${SEMESTER_BADGE[course.semester] || ''}`}>{course.semester}</span>
                  <span className="text-[10px] text-gray-400">{course.duration_hours}시간</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
      <div className="flex justify-between">
        <button onClick={() => navigate('/results')} className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition">결과로 돌아가기</button>
        <button onClick={handleGenerate} disabled={generating} className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition">
          {generating ? '생성 중...' : '훈련 로드맵 생성'}
        </button>
      </div>
    </div>
  )
}
