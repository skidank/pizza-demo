const API = "/api";

async function fetchJSON(url: string, options?: RequestInit) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

// Menu
export const getMenu = () => fetchJSON(`${API}/menu`);
export const getSpecials = () => fetchJSON(`${API}/menu/specials`);
export const getHours = () => fetchJSON(`${API}/hours`);

// Orders
export const createOrder = (name = "Guest") =>
  fetchJSON(`${API}/orders`, { method: "POST", body: JSON.stringify({ customer_name: name }) });

export const getOrder = (id: number) => fetchJSON(`${API}/orders/${id}`);

export const addOrderItem = (orderId: number, item: {
  menu_item_id: number;
  size_id?: number;
  quantity?: number;
  topping_ids?: number[];
}) =>
  fetchJSON(`${API}/orders/${orderId}/items`, { method: "POST", body: JSON.stringify(item) });

export const removeOrderItem = (orderId: number, itemId: number) =>
  fetchJSON(`${API}/orders/${orderId}/items/${itemId}`, { method: "DELETE" });

export const placeOrder = (orderId: number) =>
  fetchJSON(`${API}/orders/${orderId}/place`, { method: "POST" });

// Chat
export const sendCustomerChat = (message: string, conversationHistory: any[], orderId: number | null) =>
  fetchJSON(`${API}/chat/customer`, {
    method: "POST",
    body: JSON.stringify({ message, conversation_history: conversationHistory, order_id: orderId }),
  });

export const sendAdminChat = (message: string, conversationHistory: any[]) =>
  fetchJSON(`${API}/chat/admin`, {
    method: "POST",
    body: JSON.stringify({ message, conversation_history: conversationHistory }),
  });

// Admin
export const adminGetMenu = () => fetchJSON(`${API}/admin/menu`);
export const adminGetToppings = () => fetchJSON(`${API}/admin/toppings`);
export const adminGetSpecials = () => fetchJSON(`${API}/admin/specials`);
export const adminGetClosures = () => fetchJSON(`${API}/admin/closures`);
