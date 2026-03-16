import { create } from "zustand";
import type { MenuData, OrderState, ChatMessage, DailySpecial, OperatingHoursEntry, HolidayClosure } from "../types";

interface AppStore {
  // Menu
  menu: MenuData | null;
  specials: DailySpecial[];
  hours: OperatingHoursEntry[];
  closures: HolidayClosure[];
  setMenu: (menu: MenuData) => void;
  setSpecials: (specials: DailySpecial[]) => void;
  setHours: (hours: OperatingHoursEntry[]) => void;
  setClosures: (closures: HolidayClosure[]) => void;

  // Order
  orderId: number | null;
  orderState: OrderState;
  setOrderId: (id: number) => void;
  setOrderState: (state: OrderState) => void;

  // Customer chat
  customerMessages: ChatMessage[];
  addCustomerMessage: (msg: ChatMessage) => void;
  customerConversationHistory: any[];
  setCustomerConversationHistory: (h: any[]) => void;

  // Admin chat
  adminMessages: ChatMessage[];
  addAdminMessage: (msg: ChatMessage) => void;
  adminConversationHistory: any[];
  setAdminConversationHistory: (h: any[]) => void;
}

export const useStore = create<AppStore>((set) => ({
  menu: null,
  specials: [],
  hours: [],
  closures: [],
  setMenu: (menu) => set({ menu }),
  setSpecials: (specials) => set({ specials }),
  setHours: (hours) => set({ hours }),
  setClosures: (closures) => set({ closures }),

  orderId: null,
  orderState: { items: [], total_price: 0 },
  setOrderId: (id) => set({ orderId: id }),
  setOrderState: (state) => set({ orderState: state }),

  customerMessages: [],
  addCustomerMessage: (msg) => set((s) => ({ customerMessages: [...s.customerMessages, msg] })),
  customerConversationHistory: [],
  setCustomerConversationHistory: (h) => set({ customerConversationHistory: h }),

  adminMessages: [],
  addAdminMessage: (msg) => set((s) => ({ adminMessages: [...s.adminMessages, msg] })),
  adminConversationHistory: [],
  setAdminConversationHistory: (h) => set({ adminConversationHistory: h }),
}));
