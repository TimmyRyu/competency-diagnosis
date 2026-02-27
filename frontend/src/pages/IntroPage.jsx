import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import useDiagnosisStore from '../store/useDiagnosisStore'
import { JOB_TYPES, CAREER_STAGES } from '../data/constants'

export default function IntroPage() {
  const navigate = useNavigate()
  const { setRespondentId, setRespondentInfo, setScenarios, setCompetencies, reset } = useDiagnosisStore()
  const [form, setForm] = useState({ name: '', organization: '', job_type: '', career_stage: '' })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.name || !form.job_type || !form.career_stage) {
      alert('이름, 직무, 경력단계는 필수입니다.')
      return
    }
    setLoading(true)
    try {
      reset()
      const res = await axios.post('/api/respondents', form)
      setRespondentId(res.data.id)
      setRespondentInfo(form)

      const [scenRes, compRes] = await Promise.all([
        axios.get('/api/scenarios', { params: { job_type: form.job_type, career_stage: form.career_stage } }),
        axios.get('/api/competencies', { params: { job_type: form.job_type, career_stage: form.career_stage } }),
      ])
      setScenarios(scenRes.data)
      setCompetencies(compRes.data)
      navigate('/diagnosis')
    } catch {
      alert('오류가 발생했습니다. 다시 시도해 주세요.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-lg mx-auto">
      <div className="bg-white rounded-xl shadow-sm p-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">역량 진단 시작</h2>
        <p className="text-gray-500 mb-6 text-sm">정보를 입력하면 맞춤형 역량 진단이 시작됩니다.</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">이름 <span className="text-red-500">*</span></label>
            <input
              type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="홍길동"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">소속기관</label>
            <input
              type="text" value={form.organization} onChange={(e) => setForm({ ...form, organization: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="한국과학기술연구원"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">직무 <span className="text-red-500">*</span></label>
            <select
              value={form.job_type} onChange={(e) => setForm({ ...form, job_type: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">선택해 주세요</option>
              {JOB_TYPES.map((j) => <option key={j.value} value={j.value}>{j.label}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">경력단계 <span className="text-red-500">*</span></label>
            <select
              value={form.career_stage} onChange={(e) => setForm({ ...form, career_stage: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">선택해 주세요</option>
              {CAREER_STAGES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
            </select>
          </div>
          <button
            type="submit" disabled={loading}
            className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition"
          >
            {loading ? '준비 중...' : '진단 시작하기'}
          </button>
        </form>
      </div>
    </div>
  )
}
