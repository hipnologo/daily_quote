import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { LogIn, Quote, Sparkles, RefreshCw } from 'lucide-react'

// Sample quotes for the logout page - these will be shown randomly
const logoutQuotes = [
  { text: "The only way to do great work is to love what you do.", author: "Steve Jobs" },
  { text: "Success is not final, failure is not fatal: it is the courage to continue that counts.", author: "Winston Churchill" },
  { text: "In the middle of difficulty lies opportunity.", author: "Albert Einstein" },
  { text: "The future belongs to those who believe in the beauty of their dreams.", author: "Eleanor Roosevelt" },
  { text: "It does not matter how slowly you go as long as you do not stop.", author: "Confucius" },
  { text: "The best time to plant a tree was 20 years ago. The second best time is now.", author: "Chinese Proverb" },
  { text: "Your time is limited, don't waste it living someone else's life.", author: "Steve Jobs" },
  { text: "The only impossible journey is the one you never begin.", author: "Tony Robbins" },
  { text: "Believe you can and you're halfway there.", author: "Theodore Roosevelt" },
  { text: "What you get by achieving your goals is not as important as what you become by achieving your goals.", author: "Zig Ziglar" },
  { text: "The secret of getting ahead is getting started.", author: "Mark Twain" },
  { text: "Don't watch the clock; do what it does. Keep going.", author: "Sam Levenson" },
  { text: "Everything you've ever wanted is on the other side of fear.", author: "George Addair" },
  { text: "Success usually comes to those who are too busy to be looking for it.", author: "Henry David Thoreau" },
  { text: "The way to get started is to quit talking and begin doing.", author: "Walt Disney" },
]

function Logout() {
  const [quote, setQuote] = useState(logoutQuotes[0])
  const [isAnimating, setIsAnimating] = useState(false)

  const getRandomQuote = () => {
    const randomIndex = Math.floor(Math.random() * logoutQuotes.length)
    return logoutQuotes[randomIndex]
  }

  useEffect(() => {
    setQuote(getRandomQuote())
  }, [])

  const handleNewQuote = () => {
    setIsAnimating(true)
    setTimeout(() => {
      setQuote(getRandomQuote())
      setIsAnimating(false)
    }, 300)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-indigo-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute top-40 left-40 w-80 h-80 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      <div className="relative z-10 w-full max-w-lg">
        {/* Main card */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl border border-white/20 p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-green-400 to-emerald-600 mb-4">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-white mb-2">
              See You Soon!
            </h1>
            <p className="text-gray-300">
              You've been successfully logged out.
            </p>
          </div>

          {/* Quote section */}
          <div className={`bg-white/5 rounded-xl p-6 mb-6 border border-white/10 transition-opacity duration-300 ${isAnimating ? 'opacity-0' : 'opacity-100'}`}>
            <div className="flex items-start gap-3">
              <Quote className="w-6 h-6 text-purple-400 flex-shrink-0 mt-1" />
              <div>
                <p className="text-white text-lg italic leading-relaxed mb-3">
                  "{quote.text}"
                </p>
                <p className="text-purple-300 text-sm font-medium">
                  — {quote.author}
                </p>
              </div>
            </div>
          </div>

          {/* New quote button */}
          <button
            onClick={handleNewQuote}
            disabled={isAnimating}
            className="w-full flex items-center justify-center gap-2 text-gray-300 hover:text-white py-2 px-4 rounded-lg hover:bg-white/5 transition-all duration-200 mb-6 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isAnimating ? 'animate-spin' : ''}`} />
            <span className="text-sm">Get another inspiring quote</span>
          </button>

          {/* Login button */}
          <Link
            to="/login"
            className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-semibold py-3 px-6 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200"
          >
            <LogIn className="w-5 h-5" />
            <span>Back to Login</span>
          </Link>

          {/* Visit public site link */}
          <div className="mt-6 text-center">
            <a
              href="/"
              className="text-gray-400 hover:text-white text-sm transition-colors duration-200"
            >
              Or visit the public quote website →
            </a>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-gray-500 text-sm mt-6">
          Daily Quote Admin Dashboard
        </p>
      </div>

      {/* CSS for animations */}
      <style>{`
        @keyframes blob {
          0% { transform: translate(0px, 0px) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
          100% { transform: translate(0px, 0px) scale(1); }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  )
}

export default Logout
