import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors } from '@dnd-kit/core'
import { SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy, useSortable, arrayMove } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'

function SortableItem({ id, children }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id })
  return (
    <div ref={setNodeRef} style={{ transform: CSS.Transform.toString(transform), transition, opacity: isDragging ? 0.5 : 1 }} {...attributes}>
      <div className="flex items-center gap-2">
        <button {...listeners} className="cursor-grab active:cursor-grabbing p-1 text-gray-400 hover:text-gray-600 text-lg">⠿</button>
        <div className="flex-1">{children}</div>
      </div>
    </div>
  )
}

export default function DraggableList({ items, onReorder, renderItem, getId }) {
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  )
  const handleDragEnd = ({ active, over }) => {
    if (!over || active.id === over.id) return
    const oldIndex = items.findIndex((i) => getId(i) === active.id)
    const newIndex = items.findIndex((i) => getId(i) === over.id)
    onReorder(arrayMove(items, oldIndex, newIndex))
  }
  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext items={items.map(getId)} strategy={verticalListSortingStrategy}>
        <div className="space-y-2">
          {items.map((item, index) => (
            <SortableItem key={getId(item)} id={getId(item)}>{renderItem(item, index)}</SortableItem>
          ))}
        </div>
      </SortableContext>
    </DndContext>
  )
}
