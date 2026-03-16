import type { MenuItem } from "../types";

const categoryEmoji: Record<string, string> = {
  pizza: "🍕",
  side: "🥖",
  drink: "🥤",
  dessert: "🍰",
};

interface Props {
  item: MenuItem;
  onAdd: (item: MenuItem) => void;
}

export default function MenuItemCard({ item, onAdd }: Props) {
  return (
    <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow p-5 flex flex-col">
      <div className="text-4xl mb-3">{categoryEmoji[item.category] || "🍽️"}</div>
      <h3 className="font-bold text-lg text-gray-900">{item.name}</h3>
      <p className="text-gray-500 text-sm mt-1 flex-1">{item.description}</p>
      <div className="flex items-center justify-between mt-4">
        <span className="text-xl font-bold text-pizza-red">
          ${item.base_price.toFixed(2)}
        </span>
        <button
          onClick={() => onAdd(item)}
          className="bg-pizza-red text-white px-4 py-2 rounded-lg hover:bg-red-700 transition font-medium text-sm"
        >
          Add to Order
        </button>
      </div>
    </div>
  );
}
