import { useStore } from "../store";
import { removeOrderItem, placeOrder } from "../api";
import { useNavigate } from "react-router-dom";

export default function OrderSidebar() {
  const { orderId, orderState, setOrderState } = useStore();
  const navigate = useNavigate();

  const handleRemove = async (itemId: number) => {
    if (!orderId) return;
    const updated = await removeOrderItem(orderId, itemId);
    setOrderState({ items: updated.items, total_price: updated.total_price, status: updated.status });
  };

  const handlePlace = async () => {
    if (!orderId) return;
    await placeOrder(orderId);
    navigate("/order-confirmed");
  };

  const items = orderState.items;

  return (
    <div className="bg-white rounded-xl shadow-md p-5 h-fit sticky top-4">
      <h2 className="font-bold text-lg text-gray-900 mb-4 flex items-center gap-2">
        🛒 Your Order
      </h2>

      {items.length === 0 ? (
        <p className="text-gray-400 text-sm py-8 text-center">
          Your order is empty. Add items from the menu or use the chat assistant!
        </p>
      ) : (
        <>
          <div className="space-y-3 max-h-[400px] overflow-y-auto">
            {items.map((item) => (
              <div key={item.id} className="flex justify-between items-start border-b pb-3">
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm text-gray-900 truncate">
                    {item.quantity > 1 && `${item.quantity}x `}
                    {item.menu_item_name}
                  </p>
                  {item.size && (
                    <p className="text-xs text-gray-400">{item.size.name}</p>
                  )}
                  {item.toppings.length > 0 && (
                    <p className="text-xs text-gray-400">
                      +{item.toppings.map((t) => t.name).join(", ")}
                    </p>
                  )}
                </div>
                <div className="flex items-center gap-2 ml-2">
                  <span className="text-sm font-semibold">${item.item_price.toFixed(2)}</span>
                  <button
                    onClick={() => handleRemove(item.id)}
                    className="text-red-400 hover:text-red-600 text-xs"
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="border-t mt-4 pt-4">
            <div className="flex justify-between items-center mb-4">
              <span className="font-bold text-gray-900">Total</span>
              <span className="text-xl font-bold text-pizza-red">
                ${orderState.total_price.toFixed(2)}
              </span>
            </div>
            <button
              onClick={handlePlace}
              className="w-full bg-green-600 text-white py-3 rounded-xl font-bold hover:bg-green-700 transition"
            >
              Place Order
            </button>
          </div>
        </>
      )}
    </div>
  );
}
