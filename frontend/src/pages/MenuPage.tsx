import { useEffect, useState } from "react";
import Header from "../components/Header";
import MenuItemCard from "../components/MenuItemCard";
import PizzaCustomizer from "../components/PizzaCustomizer";
import OrderSidebar from "../components/OrderSidebar";
import ChatPanel from "../components/ChatPanel";
import { useStore } from "../store";
import { getMenu, getSpecials, getHours, createOrder, addOrderItem, sendCustomerChat } from "../api";
import type { MenuItem, DailySpecial, OperatingHoursEntry } from "../types";

const CATEGORY_LABELS: Record<string, string> = {
  pizza: "🍕 Pizzas",
  side: "🥖 Sides",
  drink: "🥤 Drinks",
  dessert: "🍰 Desserts",
};

export default function MenuPage() {
  const store = useStore();
  const [customizing, setCustomizing] = useState<MenuItem | null>(null);
  const [chatLoading, setChatLoading] = useState(false);
  const [specials, setSpecials] = useState<DailySpecial[]>([]);
  const [hours, setHours] = useState<OperatingHoursEntry[]>([]);

  useEffect(() => {
    getMenu().then(store.setMenu);
    getSpecials().then(setSpecials);
    getHours().then((data) => setHours(data.hours));
  }, []);

  const ensureOrder = async () => {
    if (!store.orderId) {
      const order = await createOrder();
      store.setOrderId(order.id);
      return order.id;
    }
    return store.orderId;
  };

  const handleAddItem = async (item: MenuItem) => {
    if (item.category === "pizza") {
      setCustomizing(item);
    } else {
      const oid = await ensureOrder();
      const updated = await addOrderItem(oid, { menu_item_id: item.id });
      store.setOrderState({ items: updated.items, total_price: updated.total_price });
    }
  };

  const handleCustomizerConfirm = async (sizeId: number, toppingIds: number[], quantity: number) => {
    if (!customizing) return;
    const oid = await ensureOrder();
    const updated = await addOrderItem(oid, {
      menu_item_id: customizing.id,
      size_id: sizeId,
      topping_ids: toppingIds,
      quantity,
    });
    store.setOrderState({ items: updated.items, total_price: updated.total_price });
    setCustomizing(null);
  };

  const handleChat = async (message: string) => {
    store.addCustomerMessage({ role: "user", content: message });
    setChatLoading(true);
    try {
      const oid = await ensureOrder();
      const res = await sendCustomerChat(message, store.customerConversationHistory, oid);
      store.addCustomerMessage({ role: "assistant", content: res.reply });
      store.setCustomerConversationHistory([
        ...store.customerConversationHistory,
        { role: "user", content: message },
        { role: "assistant", content: res.reply },
      ]);
      if (res.order_id) store.setOrderId(res.order_id);
      if (res.order_state) store.setOrderState(res.order_state);
    } catch {
      store.addCustomerMessage({ role: "assistant", content: "Sorry, something went wrong. Please try again!" });
    }
    setChatLoading(false);
  };

  const menu = store.menu;
  if (!menu) return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-400">Loading menu...</div>;

  const categories = ["pizza", "side", "drink", "dessert"];
  const itemsByCategory = Object.fromEntries(
    categories.map((cat) => [cat, menu.items.filter((i) => i.category === cat)])
  );

  const today = new Date().getDay();
  const todayDow = today === 0 ? 6 : today - 1; // JS: 0=Sun, our model: 0=Mon
  const todaySpecials = specials.filter((s) => s.day_of_week === todayDow || s.specific_date === new Date().toISOString().split("T")[0]);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      {/* Hero */}
      <section className="bg-gradient-to-br from-pizza-red to-pizza-orange text-white py-16 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-5xl font-extrabold mb-4">Welcome to Slice of Heaven</h2>
          <p className="text-xl text-red-100 mb-6">Handcrafted pizzas made with love. Order online or chat with our AI assistant!</p>
          {todaySpecials.length > 0 && (
            <div className="bg-white/20 backdrop-blur rounded-xl p-4 inline-block">
              <p className="font-bold text-yellow-200">Today's Special</p>
              {todaySpecials.map((s) => (
                <p key={s.id} className="text-sm">{s.title} — {s.description}</p>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Menu + Order */}
      <div className="max-w-7xl mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Menu */}
        <div className="lg:col-span-3">
          {categories.map((cat) => {
            const items = itemsByCategory[cat];
            if (!items?.length) return null;
            return (
              <section key={cat} className="mb-10">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">{CATEGORY_LABELS[cat]}</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {items.map((item) => (
                    <MenuItemCard key={item.id} item={item} onAdd={handleAddItem} />
                  ))}
                </div>
              </section>
            );
          })}

          {/* Hours */}
          {hours.length > 0 && (
            <section className="mt-12 bg-white rounded-xl shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">⏰ Operating Hours</h2>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {hours.map((h) => (
                  <div key={h.id} className={`p-3 rounded-lg text-sm ${h.is_closed ? "bg-red-50 text-red-600" : "bg-green-50 text-green-700"}`}>
                    <p className="font-semibold">{h.day_name}</p>
                    <p>{h.is_closed ? "Closed" : `${h.open_time} - ${h.close_time}`}</p>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>

        {/* Order sidebar */}
        <div className="lg:col-span-1">
          <OrderSidebar />
        </div>
      </div>

      {/* Pizza customizer modal */}
      {customizing && (
        <PizzaCustomizer
          item={customizing}
          sizes={menu.sizes}
          toppings={menu.toppings}
          onConfirm={handleCustomizerConfirm}
          onCancel={() => setCustomizing(null)}
        />
      )}

      {/* Chat */}
      <ChatPanel
        messages={store.customerMessages}
        onSend={handleChat}
        isLoading={chatLoading}
        title="🍕 Pizza Ordering Assistant"
        placeholder="e.g., I'd like a large pepperoni pizza..."
      />
    </div>
  );
}
