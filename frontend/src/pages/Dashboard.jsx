import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../contexts/AuthContext'
import api from '../api/client'

export default function Dashboard() {
  const { user, logout } = useAuth()
  const [todos, setTodos] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(true)
  const [fromCache, setFromCache] = useState(false)

  const fetchTodos = useCallback(() => {
    setLoading(true)
    api.get('/todos/')
      .then((r) => {
        setTodos(r.data.todos)
        setFromCache(r.data.cached)
      })
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => { fetchTodos() }, [fetchTodos])

  const addTodo = async (e) => {
    e.preventDefault()
    if (!input.trim()) return
    const { data } = await api.post('/todos/', { title: input.trim() })
    setTodos((prev) => [data.todo, ...prev])
    setInput('')
    setFromCache(false)
  }

  const toggleTodo = async (todo) => {
    const { data } = await api.patch(`/todos/${todo.id}`, { completed: !todo.completed })
    setTodos((prev) => prev.map((t) => (t.id === todo.id ? data.todo : t)))
    setFromCache(false)
  }

  const deleteTodo = async (id) => {
    await api.delete(`/todos/${id}`)
    setTodos((prev) => prev.filter((t) => t.id !== id))
    setFromCache(false)
  }

  const done = todos.filter((t) => t.completed).length

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-xl font-bold text-gray-800">My Todos</h1>
            {todos.length > 0 && (
              <p className="text-xs text-gray-400">{done}/{todos.length} done</p>
            )}
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500 hidden sm:block">{user?.email}</span>
            <button
              onClick={logout}
              className="text-sm text-red-500 hover:text-red-700 font-medium"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-8">
        <form onSubmit={addTodo} className="flex gap-2 mb-6">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Add a new todo…"
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            className="bg-blue-600 text-white px-5 py-2 rounded-lg hover:bg-blue-700 font-medium transition-colors"
          >
            Add
          </button>
        </form>

        {fromCache && (
          <p className="text-xs text-amber-500 mb-3">
            ⚡ Served from Redis cache
          </p>
        )}

        {loading ? (
          <p className="text-gray-400 text-center py-12">Loading…</p>
        ) : todos.length === 0 ? (
          <p className="text-gray-400 text-center py-12">No todos yet — add one above!</p>
        ) : (
          <ul className="space-y-2">
            {todos.map((todo) => (
              <li
                key={todo.id}
                className="bg-white rounded-xl shadow-sm px-4 py-3 flex items-center gap-3 group"
              >
                <input
                  type="checkbox"
                  checked={todo.completed}
                  onChange={() => toggleTodo(todo)}
                  className="w-5 h-5 cursor-pointer accent-blue-600"
                />
                <span
                  className={`flex-1 text-sm ${
                    todo.completed ? 'line-through text-gray-400' : 'text-gray-800'
                  }`}
                >
                  {todo.title}
                </span>
                <button
                  onClick={() => deleteTodo(todo.id)}
                  className="text-gray-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity text-lg leading-none"
                  aria-label="Delete"
                >
                  ×
                </button>
              </li>
            ))}
          </ul>
        )}
      </main>
    </div>
  )
}
