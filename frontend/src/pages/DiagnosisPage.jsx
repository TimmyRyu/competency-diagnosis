import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import axios from 'axios'
import useDiagnosisStore from '../store/useDiagnosisStore'
import ScenarioCard from '../components/ScenarioCard'
import LikertScale from '../components/LikertScale'

export default function DiagnosisPage() {
  const navigate = useNavigate()
  const { scenarios, currentScenarioIndex, selections, toggleCompetency, setLikertScore, nextScenario, prevScenario, respondentId, setPriorityResults } = useDiagnosisStore()
  const [submitting, setSubmitting] = useState(false)

  if (!scenarios.length) { navigate('/'); return null }

  const scenario = scenarios[currentScenarioIndex]
  const scenarioSel = selections[scenario.id] || {}
  const isLast = currentScenarioIndex === scenarios.length - 1

  const handleSubmit = async () => {
    setSubmitting(true)
    try {
      const results = []
      for (const [scenarioId, comps] of Object.entries(selections))
        for (const [competencyId, likert_score] of Object.entries(comps))
          results.push({ scenario_id: +scenarioId, competency_id: +competencyId, likert_score })

      await axios.post('/api/diagnosis', { respondent_id: respondentId, results })
      const diagRes = await axios.get(`/api/diagnosis/${respondentId}`)
      setPriorityResults(diagRes.data)
      navigate('/results')
    } catch { alert('저장 중 오류가 발생했습니다.') }
    finally { setSubmitting(false) }
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>시나리오 {currentScenarioIndex + 1} / {scenarios.length}</span>
          <span>{Math.round(((currentScenarioIndex + 1) / scenarios.length) * 100)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div className="bg-blue-600 h-2 rounded-full transition-all" style={{ width: `${((currentScenarioIndex + 1) / scenarios.length) * 100}%` }} />
        </div>
      </div>

      <ScenarioCard situation={scenario.situation} groupName={scenario.group_name} />

      <p className="mt-6 mb-4 text-gray-700 font-medium">이 상황에서 가장 필요하다고 생각하는 역량을 선택해주세요. (복수 선택 가능)</p>

      <div className="space-y-3">
        {scenario.competencies.map((comp) => {
          const isSelected = scenarioSel[comp.id] !== undefined
          return (
            <div key={comp.id} className={`border rounded-lg p-4 transition ${isSelected ? 'border-blue-400 bg-blue-50' : 'border-gray-200 bg-white'}`}>
              <div className="flex items-start gap-3">
                <input type="checkbox" checked={isSelected} onChange={() => toggleCompetency(scenario.id, comp.id)} className="mt-1 h-4 w-4 text-blue-600 rounded" />
                <div className="flex-1">
                  <span className="font-medium text-gray-800">{comp.name}</span>
                  <p className="text-sm text-gray-500 mt-0.5">{comp.description}</p>
                  {isSelected && (
                    <div className="mt-3">
                      <p className="text-xs text-gray-500 mb-1.5">해당 역량이 얼마나 필요하다고 느끼십니까?</p>
                      <LikertScale value={scenarioSel[comp.id]} onChange={(score) => setLikertScore(scenario.id, comp.id, score)} />
                    </div>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      <div className="flex justify-between mt-8">
        <button onClick={prevScenario} disabled={currentScenarioIndex === 0}
          className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-30 transition">이전</button>
        {isLast
          ? <button onClick={handleSubmit} disabled={submitting}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition">{submitting ? '제출 중...' : '진단 완료'}</button>
          : <button onClick={nextScenario}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition">다음</button>
        }
      </div>
    </div>
  )
}
