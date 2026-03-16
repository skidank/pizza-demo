import { useState } from "react";
import type { MenuItem, PizzaSize, Topping } from "../types";

interface Props {
  item: MenuItem;
  sizes: PizzaSize[];
  toppings: Topping[];
  onConfirm: (sizeId: number, toppingIds: number[], quantity: number) => void;
  onCancel: () => void;
}

export default function PizzaCustomizer({ item, sizes, toppings, onConfirm, onCancel }: Props) {
  const [selectedSize, setSelectedSize] = useState(sizes.find((s) => s.price_multiplier === 1.0)?.id || sizes[0]?.id);
  const [selectedToppings, setSelectedToppings] = useState<number[]>([]);
  const [quantity, setQuantity] = useState(1);

  const size = sizes.find((s) => s.id === selectedSize);
  const basePrice = item.base_price * (size?.price_multiplier || 1);
  const toppingsPrice = selectedToppings.reduce((sum, tid, idx) => {
    if (idx < includedToppings) return sum; // free topping
    const t = toppings.find((tp) => tp.id === tid);
    return sum + (t?.price || 0);
  }, 0);
  const totalPrice = (basePrice + toppingsPrice) * quantity;

  const maxToppings = item.max_toppings ?? null;
  const includedToppings = item.included_toppings ?? 0;
  const atLimit = maxToppings !== null && selectedToppings.length >= maxToppings;

  const toggleTopping = (id: number) => {
    setSelectedToppings((prev) => {
      if (prev.includes(id)) return prev.filter((t) => t !== id);
      if (maxToppings !== null && prev.length >= maxToppings) return prev;
      return [...prev, id];
    });
  };

  const toppingsByCategory = {
    meat: toppings.filter((t) => t.category === "meat"),
    veggie: toppings.filter((t) => t.category === "veggie"),
    cheese: toppings.filter((t) => t.category === "cheese"),
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">🍕 {item.name}</h2>
              <p className="text-gray-500 text-sm">{item.description}</p>
            </div>
            <button onClick={onCancel} className="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
          </div>

          {/* Size selection */}
          <div className="mb-6">
            <h3 className="font-semibold text-gray-700 mb-2">Choose Size</h3>
            <div className="grid grid-cols-2 gap-2">
              {sizes.map((s) => (
                <button
                  key={s.id}
                  onClick={() => setSelectedSize(s.id)}
                  className={`p-3 rounded-lg border-2 text-sm font-medium transition ${
                    selectedSize === s.id
                      ? "border-pizza-red bg-red-50 text-pizza-red"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  {s.name}
                  <span className="block text-xs mt-1">
                    ${(item.base_price * s.price_multiplier).toFixed(2)}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Toppings */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-gray-700">
                {includedToppings > 0 ? `Toppings (${includedToppings} included free)` : "Extra Toppings"}
              </h3>
              {maxToppings !== null && (
                <span className={`text-xs font-medium px-2 py-1 rounded-full ${atLimit ? "bg-red-100 text-red-600" : "bg-gray-100 text-gray-500"}`}>
                  {selectedToppings.length}/{maxToppings} max
                </span>
              )}
            </div>
            {Object.entries(toppingsByCategory).map(([cat, tops]) => (
              <div key={cat} className="mb-3">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">
                  {cat}
                </p>
                <div className="flex flex-wrap gap-2">
                  {tops.map((t) => {
                    const isSelected = selectedToppings.includes(t.id);
                    const isDisabled = !isSelected && atLimit;
                    return (
                    <button
                      key={t.id}
                      onClick={() => toggleTopping(t.id)}
                      disabled={isDisabled}
                      className={`px-3 py-1.5 rounded-full text-xs font-medium transition ${
                        isSelected
                          ? "bg-pizza-red text-white"
                          : isDisabled
                          ? "bg-gray-50 text-gray-300 cursor-not-allowed"
                          : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                      }`}
                    >
                      {t.name} (+${t.price.toFixed(2)})
                    </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          {/* Quantity */}
          <div className="flex items-center gap-4 mb-6">
            <span className="font-semibold text-gray-700">Quantity:</span>
            <button
              onClick={() => setQuantity(Math.max(1, quantity - 1))}
              className="w-8 h-8 rounded-full bg-gray-200 hover:bg-gray-300 font-bold"
            >
              -
            </button>
            <span className="text-lg font-bold w-8 text-center">{quantity}</span>
            <button
              onClick={() => setQuantity(quantity + 1)}
              className="w-8 h-8 rounded-full bg-gray-200 hover:bg-gray-300 font-bold"
            >
              +
            </button>
          </div>

          {/* Total and confirm */}
          <div className="flex items-center justify-between border-t pt-4">
            <div>
              <p className="text-sm text-gray-500">Total</p>
              <p className="text-2xl font-bold text-pizza-red">${totalPrice.toFixed(2)}</p>
            </div>
            <button
              onClick={() => onConfirm(selectedSize, selectedToppings, quantity)}
              className="bg-pizza-red text-white px-6 py-3 rounded-xl font-bold hover:bg-red-700 transition"
            >
              Add to Order
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
