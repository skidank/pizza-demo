import { useEffect, useState } from "react";
import Header from "../components/Header";
import { useStore } from "../store";
import {
  adminGetMenu,
  adminGetToppings,
  adminGetSpecials,
  adminGetClosures,
  getHours,
  sendAdminChat,
} from "../api";
import type { MenuItem, Topping, DailySpecial, OperatingHoursEntry, HolidayClosure, ChatMessage } from "../types";

export default function AdminPage() {
  const store = useStore();
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [toppings, setToppings] = useState<Topping[]>([]);
  const [specials, setSpecials] = useState<DailySpecial[]>([]);
  const [hours, setHours] = useState<OperatingHoursEntry[]>([]);
  const [closures, setClosures] = useState<HolidayClosure[]>([]);
  const [chatLoading, setChatLoading] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [activeTab, setActiveTab] = useState<"menu" | "toppings" | "specials" | "hours">("menu");

  const refreshAll = () => {
    adminGetMenu().then(setMenuItems);
    adminGetToppings().then(setToppings);
    adminGetSpecials().then(setSpecials);
    getHours().then((d) => { setHours(d.hours); setClosures(d.closures); });
    adminGetClosures().then(setClosures);
  };

  useEffect(() => { refreshAll(); }, []);

  const handleChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || chatLoading) return;
    const message = chatInput.trim();
    setChatInput("");
    store.addAdminMessage({ role: "user", content: message });
    setChatLoading(true);
    try {
      const res = await sendAdminChat(message, store.adminConversationHistory);
      store.addAdminMessage({ role: "assistant", content: res.reply });
      store.setAdminConversationHistory([
        ...store.adminConversationHistory,
        { role: "user", content: message },
        { role: "assistant", content: res.reply },
      ]);
      // Refresh data if mutations occurred
      if (res.mutations?.length > 0) {
        refreshAll();
      }
    } catch {
      store.addAdminMessage({ role: "assistant", content: "Sorry, something went wrong." });
    }
    setChatLoading(false);
  };

  const categoryLabel: Record<string, string> = { pizza: "Pizza", side: "Side", drink: "Drink", dessert: "Dessert" };
  const dayNames = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Header isAdmin />

      <div className="max-w-7xl mx-auto px-4 py-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Chat */}
        <div className="bg-gray-800 rounded-2xl flex flex-col h-[calc(100vh-120px)]">
          <div className="p-4 border-b border-gray-700">
            <h2 className="font-bold text-lg flex items-center gap-2">
              🤖 Admin Assistant
            </h2>
            <p className="text-xs text-gray-400">Manage your restaurant with natural language</p>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3 chat-scroll">
            {store.adminMessages.length === 0 && (
              <div className="text-gray-500 text-sm text-center py-12">
                <p className="text-3xl mb-3">👋</p>
                <p className="font-medium">Welcome, Admin!</p>
                <p className="mt-2">Try things like:</p>
                <ul className="mt-2 space-y-1 text-gray-400">
                  <li>"Show me the current menu"</li>
                  <li>"Add a new pizza called Truffle Mushroom for $18.99"</li>
                  <li>"Create a Friday special: 15% off all pizzas"</li>
                  <li>"Close the restaurant on December 25th for Christmas"</li>
                  <li>"Change the price of Pepperoni pizza to $15.99"</li>
                </ul>
              </div>
            )}
            {store.adminMessages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm whitespace-pre-wrap ${
                    msg.role === "user"
                      ? "bg-blue-600 text-white rounded-br-sm"
                      : "bg-gray-700 text-gray-100 rounded-bl-sm"
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}
            {chatLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-700 rounded-2xl rounded-bl-sm px-4 py-2.5 text-sm text-gray-400">
                  Thinking...
                </div>
              </div>
            )}
          </div>

          <form onSubmit={handleChat} className="border-t border-gray-700 p-3 flex gap-2">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="e.g., Add a new BBQ Bacon pizza for $17.99..."
              disabled={chatLoading}
              className="flex-1 bg-gray-700 border border-gray-600 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={chatLoading || !chatInput.trim()}
              className="bg-blue-600 text-white px-5 py-2.5 rounded-xl font-medium text-sm hover:bg-blue-700 transition disabled:opacity-50"
            >
              Send
            </button>
          </form>
        </div>

        {/* Right: Live data preview */}
        <div className="bg-gray-800 rounded-2xl overflow-hidden h-[calc(100vh-120px)] flex flex-col">
          {/* Tabs */}
          <div className="flex border-b border-gray-700">
            {(["menu", "toppings", "specials", "hours"] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 px-4 py-3 text-sm font-medium transition ${
                  activeTab === tab ? "bg-gray-700 text-white" : "text-gray-400 hover:text-gray-200"
                }`}
              >
                {tab === "menu" ? "🍕 Menu" : tab === "toppings" ? "🧀 Toppings" : tab === "specials" ? "⭐ Specials" : "⏰ Hours"}
              </button>
            ))}
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            {/* Menu Tab */}
            {activeTab === "menu" && (
              <div className="space-y-2">
                {menuItems.map((item) => (
                  <div key={item.id} className={`flex items-center justify-between p-3 rounded-lg ${item.is_available ? "bg-gray-700" : "bg-gray-700/50 opacity-60"}`}>
                    <div>
                      <span className="font-medium text-sm">{item.name}</span>
                      <span className="text-xs text-gray-400 ml-2">{categoryLabel[item.category]}</span>
                      {!item.is_available && <span className="text-xs text-red-400 ml-2">(unavailable)</span>}
                    </div>
                    <span className="text-sm font-bold text-green-400">${item.base_price.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Toppings Tab */}
            {activeTab === "toppings" && (
              <div className="space-y-2">
                {["meat", "veggie", "cheese"].map((cat) => {
                  const filtered = toppings.filter((t) => t.category === cat);
                  if (!filtered.length) return null;
                  return (
                    <div key={cat}>
                      <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 mt-3">{cat}</h3>
                      {filtered.map((t) => (
                        <div key={t.id} className={`flex items-center justify-between p-2 rounded-lg ${t.is_available ? "bg-gray-700" : "bg-gray-700/50 opacity-60"}`}>
                          <span className="text-sm">{t.name} {!t.is_available && <span className="text-red-400 text-xs">(unavailable)</span>}</span>
                          <span className="text-sm font-bold text-green-400">+${t.price.toFixed(2)}</span>
                        </div>
                      ))}
                    </div>
                  );
                })}
              </div>
            )}

            {/* Specials Tab */}
            {activeTab === "specials" && (
              <div className="space-y-3">
                {specials.length === 0 && <p className="text-gray-500 text-sm text-center py-8">No specials configured</p>}
                {specials.map((s) => (
                  <div key={s.id} className={`p-4 rounded-lg ${s.is_active ? "bg-yellow-900/30 border border-yellow-700/50" : "bg-gray-700/50 opacity-60"}`}>
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-bold text-sm text-yellow-300">{s.title}</h4>
                        <p className="text-xs text-gray-400 mt-1">{s.description}</p>
                      </div>
                      <div className="text-right text-xs text-gray-400">
                        {s.discount_percent && <p>{s.discount_percent}% off</p>}
                        {s.discount_amount && <p>${s.discount_amount} off</p>}
                        {s.day_of_week !== null && <p>Every {dayNames[s.day_of_week]}</p>}
                        {s.specific_date && <p>{s.specific_date}</p>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Hours Tab */}
            {activeTab === "hours" && (
              <div className="space-y-4">
                <div className="space-y-2">
                  <h3 className="text-sm font-bold text-gray-300 mb-2">Weekly Schedule</h3>
                  {hours.map((h) => (
                    <div key={h.id} className={`flex justify-between p-3 rounded-lg ${h.is_closed ? "bg-red-900/30" : "bg-gray-700"}`}>
                      <span className="text-sm font-medium">{h.day_name}</span>
                      <span className={`text-sm ${h.is_closed ? "text-red-400" : "text-green-400"}`}>
                        {h.is_closed ? "Closed" : `${h.open_time} - ${h.close_time}`}
                      </span>
                    </div>
                  ))}
                </div>

                {closures.length > 0 && (
                  <div className="mt-6">
                    <h3 className="text-sm font-bold text-gray-300 mb-2">Upcoming Closures</h3>
                    {closures.map((c) => (
                      <div key={c.id} className="flex justify-between p-3 rounded-lg bg-red-900/30 mb-2">
                        <span className="text-sm">{c.reason}</span>
                        <span className="text-sm text-red-400">{c.date}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
