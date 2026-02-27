import { BrowserRouter, Routes, Route } from 'react-router-dom'
import IntroPage from './pages/IntroPage'
import DiagnosisPage from './pages/DiagnosisPage'
import ResultPage from './pages/ResultPage'
import CoursePage from './pages/CoursePage'
import RoadmapPage from './pages/RoadmapPage'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow-sm no-print">
          <div className="max-w-5xl mx-auto px-4 py-4">
            <h1 className="text-xl font-bold text-gray-800">
              과학기술인 필요역량 진단 시스템
            </h1>
          </div>
        </header>
        <main className="max-w-5xl mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<IntroPage />} />
            <Route path="/diagnosis" element={<DiagnosisPage />} />
            <Route path="/results" element={<ResultPage />} />
            <Route path="/courses" element={<CoursePage />} />
            <Route path="/roadmap" element={<RoadmapPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
