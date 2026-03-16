export interface MenuItem {
  id: number;
  name: string;
  description: string;
  category: "pizza" | "side" | "drink" | "dessert";
  base_price: number;
  image_url: string | null;
  sort_order: number;
  is_available?: boolean;
  max_toppings?: number | null;
  included_toppings?: number;
}

export interface PizzaSize {
  id: number;
  name: string;
  price_multiplier: number;
}

export interface Topping {
  id: number;
  name: string;
  category: "meat" | "veggie" | "cheese";
  price: number;
  is_available?: boolean;
}

export interface MenuData {
  items: MenuItem[];
  sizes: PizzaSize[];
  toppings: Topping[];
}

export interface OrderItemTopping {
  id: number;
  name: string;
  price: number;
}

export interface OrderItem {
  id: number;
  menu_item_id: number;
  menu_item_name: string;
  category: string;
  size: { id: number; name: string } | null;
  quantity: number;
  item_price: number;
  toppings: OrderItemTopping[];
}

export interface OrderState {
  items: OrderItem[];
  total_price: number;
  status?: string;
}

export interface Order {
  id: number;
  customer_name: string;
  status: string;
  total_price: number;
  items: OrderItem[];
}

export interface DailySpecial {
  id: number;
  title: string;
  description: string;
  discount_percent: number | null;
  discount_amount: number | null;
  day_of_week: number | null;
  specific_date: string | null;
  menu_item_id: number | null;
  is_active?: boolean;
}

export interface OperatingHoursEntry {
  id: number;
  day_of_week: number;
  day_name: string;
  open_time: string;
  close_time: string;
  is_closed: boolean;
}

export interface HolidayClosure {
  id: number;
  date: string;
  reason: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}
