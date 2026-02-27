import { LIKERT_LABELS } from '../data/constants'
export default function LikertScale({ value, onChange }) {
  return (
    <div className="flex items-center gap-1 sm:gap-2">
      {LIKERT_LABELS.map((item) => (
        <button key={item.value} type="button" onClick={() => onChange(item.value)}
          className={`flex flex-col items-center px-2 py-1.5 rounded-md text-xs transition ${value === item.value ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
          <span className="font-bold text-sm">{item.value}</span>
          <span className="hidden sm:block text-[10px] mt-0.5 whitespace-nowrap">{item.label}</span>
        </button>
      ))}
    </div>
  )
}
