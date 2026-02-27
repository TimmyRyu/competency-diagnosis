import { create } from 'zustand'

const useDiagnosisStore = create((set) => ({
  respondentId: null,
  respondentInfo: { name: '', organization: '', job_type: '', career_stage: '' },
  scenarios: [],
  competencies: [],
  currentScenarioIndex: 0,
  selections: {},
  priorityResults: [],
  roadmapItems: { 'Phase 1': [], 'Phase 2': [], 'Phase 3': [] },
  coursesByCompetency: [],

  setRespondentInfo: (info) => set({ respondentInfo: info }),
  setRespondentId: (id) => set({ respondentId: id }),
  setScenarios: (s) => set({ scenarios: s }),
  setCompetencies: (c) => set({ competencies: c }),
  nextScenario: () => set((s) => ({ currentScenarioIndex: s.currentScenarioIndex + 1 })),
  prevScenario: () => set((s) => ({ currentScenarioIndex: Math.max(0, s.currentScenarioIndex - 1) })),

  toggleCompetency: (scenarioId, competencyId) => set((state) => {
    const sel = { ...state.selections[scenarioId] }
    if (sel[competencyId] !== undefined) delete sel[competencyId]
    else sel[competencyId] = 3
    return { selections: { ...state.selections, [scenarioId]: sel } }
  }),
  setLikertScore: (scenarioId, competencyId, score) => set((state) => ({
    selections: { ...state.selections, [scenarioId]: { ...state.selections[scenarioId], [competencyId]: score } }
  })),

  setPriorityResults: (r) => set({ priorityResults: r }),
  reorderPriority: (newOrder) => set({ priorityResults: newOrder }),
  setCoursesByCompetency: (c) => set({ coursesByCompetency: c }),
  setRoadmapItems: (items) => set({ roadmapItems: items }),

  reset: () => set({
    respondentId: null,
    respondentInfo: { name: '', organization: '', job_type: '', career_stage: '' },
    scenarios: [], competencies: [], currentScenarioIndex: 0,
    selections: {}, priorityResults: [],
    roadmapItems: { 'Phase 1': [], 'Phase 2': [], 'Phase 3': [] },
    coursesByCompetency: [],
  }),
}))

export default useDiagnosisStore
