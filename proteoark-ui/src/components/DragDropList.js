import React, { useState } from "react";

const DragDropList = () => {
  const [list1, setList1] = useState(["Item 1", "Item 2", "Item 3"]);
  const [list2, setList2] = useState([]);
  const [draggedItem, setDraggedItem] = useState(null);

  const handleDragStart = (item, source) => {
    setDraggedItem({ item, source });
  };

  const handleDrop = (targetList, setTargetList, sourceList, setSourceList) => {
    if (draggedItem) {
      // Remove item from source list
      const updatedSourceList = sourceList.filter(
        (i) => i !== draggedItem.item
      );
      setSourceList(updatedSourceList);

      // Add item to target list
      setTargetList([...targetList, draggedItem.item]);

      // Reset dragged item
      setDraggedItem(null);
    }
  };

  return (
    <div className="flex gap-6 p-6">
      {/* First List */}
      <div
        className="w-48 min-h-40 p-4 bg-gray-100 border-2 border-dashed border-gray-400"
        onDragOver={(e) => e.preventDefault()}
        onDrop={() => handleDrop(list1, setList1, list2, setList2)}
      >
        <h3 className="text-center font-semibold">List 1</h3>
        <ul>
          {list1.map((item) => (
            <li
              key={item}
              className="p-2 m-2 bg-blue-200 cursor-pointer text-center"
              draggable
              onDragStart={() => handleDragStart(item, list1)}
            >
              {item}
            </li>
          ))}
        </ul>
      </div>

      {/* Second List */}
      <div
        className="w-48 min-h-40 p-4 bg-gray-100 border-2 border-dashed border-gray-400"
        onDragOver={(e) => e.preventDefault()}
        onDrop={() => handleDrop(list2, setList2, list1, setList1)}
      >
        <h3 className="text-center font-semibold">List 2</h3>
        <ul>
          {list2.map((item) => (
            <li
              key={item}
              className="p-2 m-2 bg-green-200 cursor-pointer text-center"
              draggable
              onDragStart={() => handleDragStart(item, list2)}
            >
              {item}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default DragDropList;
