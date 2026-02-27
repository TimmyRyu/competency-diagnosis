import { useState } from 'react'
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors, DragOverlay } from '@dnd-kit/core'
import { SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy, useSortable, arrayMove } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { PHASES } from '../data/constants'

const SEMESTER_COLOR = { '상반기': 'border-l-green-400', '하반기': 'border-l-orange-400', '상시': 'border-l-gray-400' }
const PHASE_STYLE = {
  'Phase 1': { bg: 'bg-red-50', border: 'border-red-200' },
  'Phase 2': { bg: 'bg-yellow-50', border: 'border-yellow-200' },
  'Phase 3': { bg: 'bg-green-50', border: 'border-green-200' },
}

function SortableCard({ id, item }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id })
  return (
    <div ref={setNodeRef} style={{ transform: CSS.Transform.toString(transform), transition, opacity: isDragging ? 0.3 : 1 }}
      {...attributes} {...listeners}
      className={`bg-white border border-gray-200 border-l-4 ${SEMESTER_COLOR[item.semester] || 'border-l-gray-300'} rounded-lg p-3 cursor-grab active:cursor-grabbing shadow-sm hover:shadow`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="font-medium text-sm text-gray-800">{item.course_name}</p>
          <p className="text-xs text-gray-500 mt-0.5">{item.competency_name}</p>
        </div>
        <div className="flex flex-col items-end gap-1 ml-2 shrink-0">
          <span className="text-[10px] text-gray-400">{item.duration_hours}h</span>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-600">{item.semester}</span>
        </div>
      </div>
    </div>
  )
}

export default function RoadmapTimeline({ phases, onUpdate }) {
  const [activeId, setActiveId] = useState(null)
  const sensors = useSensors(useSensor(PointerSensor), useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }))

  const findContainer = (id) => {
    for (const p of PHASES)
      if (phases[p.key]?.some((item) => `rm-${item.id}` === id)) return p.key
    return null
  }

  const handleDragStart = ({ active }) => setActiveId(active.id)

  const handleDragOver = ({ active, over }) => {
    if (!over) return
    const from = findContainer(active.id)
    let to = findContainer(over.id)
    if (!to) to = PHASES.find((p) => p.key === over.id)?.key
    if (!from || !to || from === to) return

    const newPhases = { ...phases }
    const fromItems = [...newPhases[from]]
    const toItems = [...newPhases[to]]
    const idx = fromItems.findIndex((i) => `rm-${i.id}` === active.id)
    const [moved] = fromItems.splice(idx, 1)
    moved.phase = to
    const overIdx = toItems.findIndex((i) => `rm-${i.id}` === over.id)
    overIdx >= 0 ? toItems.splice(overIdx, 0, moved) : toItems.push(moved)
    newPhases[from] = fromItems
    newPhases[to] = toItems
    onUpdate(newPhases)
  }

  const handleDragEnd = ({ active, over }) => {
    setActiveId(null)
    if (!over) return
    const from = findContainer(active.id)
    const to = findContainer(over.id) || over.id
    if (from === to && from) {
      const items = [...(phases[from] || [])]
      const oldIdx = items.findIndex((i) => `rm-${i.id}` === active.id)
      const newIdx = items.findIndex((i) => `rm-${i.id}` === over.id)
      if (oldIdx !== newIdx && oldIdx >= 0 && newIdx >= 0) {
        onUpdate({ ...phases, [from]: arrayMove(items, oldIdx, newIdx) })
      }
    }
  }

  const activeItem = activeId ? Object.values(phases).flat().find((i) => `rm-${i.id}` === activeId) : null

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragStart={handleDragStart} onDragOver={handleDragOver} onDragEnd={handleDragEnd}>
      <div className="grid gap-4 md:grid-cols-3">
        {PHASES.map((phase) => {
          const items = phases[phase.key] || []
          const s = PHASE_STYLE[phase.key]
          return (
            <div key={phase.key} id={phase.key} className={`rounded-lg border-2 ${s.border} ${s.bg} p-4`}>
              <div className="flex justify-between mb-3">
                <h4 className="font-semibold text-gray-800 text-sm">{phase.label}</h4>
                <span className="text-[10px] text-gray-500">{items.reduce((s, i) => s + (i.duration_hours || 0), 0)}시간</span>
              </div>
              <SortableContext items={items.map((i) => `rm-${i.id}`)} strategy={verticalListSortingStrategy}>
                <div className="space-y-2 min-h-[80px]">
                  {items.map((item) => <SortableCard key={item.id} id={`rm-${item.id}`} item={item} />)}
                  {items.length === 0 && (
                    <div className="text-center text-gray-400 text-sm py-6 border-2 border-dashed border-gray-300 rounded-lg">드래그하여 이동</div>
                  )}
                </div>
              </SortableContext>
            </div>
          )
        })}
      </div>
      <DragOverlay>
        {activeItem ? (
          <div className="bg-white border-2 border-blue-400 rounded-lg p-3 shadow-lg opacity-90">
            <p className="font-medium text-sm">{activeItem.course_name}</p>
            <p className="text-xs text-gray-500">{activeItem.competency_name}</p>
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  )
}
