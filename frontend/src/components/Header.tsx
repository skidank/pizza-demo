import { Link } from "react-router-dom";

export default function Header({ isAdmin = false }: { isAdmin?: boolean }) {
  return (
    <header className="bg-pizza-red text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3 hover:opacity-90">
          <span className="text-3xl">🍕</span>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Slice of Heaven</h1>
            <p className="text-xs text-red-200">Artisan Pizza Since 2024</p>
          </div>
        </Link>
        <nav className="flex items-center gap-4">
          {isAdmin ? (
            <Link to="/" className="text-sm bg-white/20 px-3 py-1.5 rounded hover:bg-white/30 transition">
              View Menu
            </Link>
          ) : (
            <Link to="/admin" className="text-sm bg-white/20 px-3 py-1.5 rounded hover:bg-white/30 transition">
              Admin
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
