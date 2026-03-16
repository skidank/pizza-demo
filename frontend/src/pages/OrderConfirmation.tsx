import { Link } from "react-router-dom";
import Header from "../components/Header";
import { useStore } from "../store";

export default function OrderConfirmation() {
  const { orderState, orderId } = useStore();

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="max-w-lg mx-auto px-4 py-16 text-center">
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <div className="text-6xl mb-4">🎉</div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Order Placed!</h1>
          <p className="text-gray-500 mb-6">
            Your order #{orderId} has been received. Thank you for choosing Slice of Heaven!
          </p>

          {orderState.items.length > 0 && (
            <div className="border rounded-xl p-4 mb-6 text-left">
              <h3 className="font-semibold text-gray-700 mb-2">Order Summary</h3>
              {orderState.items.map((item) => (
                <div key={item.id} className="flex justify-between text-sm py-1 border-b last:border-0">
                  <span>
                    {item.quantity > 1 && `${item.quantity}x `}
                    {item.menu_item_name}
                    {item.size && ` (${item.size.name})`}
                  </span>
                  <span className="font-medium">${item.item_price.toFixed(2)}</span>
                </div>
              ))}
              <div className="flex justify-between font-bold mt-2 pt-2 border-t">
                <span>Total</span>
                <span className="text-pizza-red">${orderState.total_price.toFixed(2)}</span>
              </div>
            </div>
          )}

          <p className="text-sm text-gray-400 mb-6">
            (This is a demo — no actual order has been placed or payment charged.)
          </p>

          <Link
            to="/"
            className="inline-block bg-pizza-red text-white px-6 py-3 rounded-xl font-bold hover:bg-red-700 transition"
          >
            Order Again
          </Link>
        </div>
      </div>
    </div>
  );
}
