import { useState } from 'react'
import { 
  FaEnvelope, FaMapMarkerAlt, FaPaperPlane, FaGithub, 
  FaLinkedin, FaTwitter, FaHeart, FaCode 
} from 'react-icons/fa'

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  })
  const [isSending, setIsSending] = useState(false)
  const [sent, setSent] = useState(false)

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSending(true)
    
    // Simulate sending (replace with actual API call)
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    setIsSending(false)
    setSent(true)
    setFormData({ name: '', email: '', subject: '', message: '' })
    
    setTimeout(() => setSent(false), 5000)
  }

  return (
    <div className="min-h-screen py-12 px-4">
      {/* Hero Section */}
      <div className="max-w-4xl mx-auto text-center mb-12">
        <div className="inline-flex items-center gap-2 bg-primary/10 px-4 py-2 rounded-full mb-6">
          <FaHeart className="text-pink-500 animate-pulse" />
          <span className="text-sm text-gray-400">Let's Connect</span>
        </div>
        
        <h1 className="text-4xl md:text-5xl font-bold mb-4">
          <span className="bg-gradient-to-r from-primary via-pink-500 to-purple-500 bg-clip-text text-transparent">
            Get In Touch
          </span>
        </h1>
        <p className="text-gray-400 max-w-2xl mx-auto text-lg">
          Have a question, feedback, or just want to say hi? 
          I'd love to hear from you. Drop me a message!
        </p>
      </div>

      <div className="max-w-6xl mx-auto grid lg:grid-cols-5 gap-8">
        {/* Contact Info Cards */}
        <div className="lg:col-span-2 space-y-6">
          {/* Email Card */}
          <div className="group bg-gradient-to-br from-secondary to-dark rounded-2xl p-6 border border-primary/10 hover:border-primary/30 transition-all hover:shadow-lg hover:shadow-primary/5">
            <div className="flex items-start gap-4">
              <div className="p-4 bg-primary/20 rounded-xl group-hover:scale-110 transition-transform">
                <FaEnvelope className="text-2xl text-primary" />
              </div>
              <div>
                <h3 className="text-white font-semibold mb-1">Email Me</h3>
                <a 
                  href="mailto:bothackerr03@gmail.com"
                  className="text-primary hover:underline text-sm"
                >
                  bothackerr03@gmail.com
                </a>
                <p className="text-gray-500 text-xs mt-2">
                  I'll respond within 24-48 hours
                </p>
              </div>
            </div>
          </div>

          {/* Location Card */}
          <div className="group bg-gradient-to-br from-secondary to-dark rounded-2xl p-6 border border-primary/10 hover:border-primary/30 transition-all hover:shadow-lg hover:shadow-primary/5">
            <div className="flex items-start gap-4">
              <div className="p-4 bg-pink-500/20 rounded-xl group-hover:scale-110 transition-transform">
                <FaMapMarkerAlt className="text-2xl text-pink-500" />
              </div>
              <div>
                <h3 className="text-white font-semibold mb-1">Location</h3>
                <p className="text-gray-300 text-sm">Hindupur</p>
                <p className="text-gray-500 text-xs mt-2">
                  Andhra Pradesh, India 🇮🇳
                </p>
              </div>
            </div>
          </div>

          {/* Social Links Card */}
          <div className="bg-gradient-to-br from-secondary to-dark rounded-2xl p-6 border border-primary/10">
            <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
              <FaCode className="text-primary" />
              Connect With Me
            </h3>
            <div className="flex gap-3">
              <a 
                href="https://github.com/kumarg0605"
                target="_blank"
                rel="noopener noreferrer"
                className="p-3 bg-dark rounded-xl hover:bg-gray-700 transition-colors group"
              >
                <FaGithub className="text-xl text-gray-400 group-hover:text-white" />
              </a>
              <a 
                href="https://linkedin.com/kumarg"
                target="_blank"
                rel="noopener noreferrer"
                className="p-3 bg-dark rounded-xl hover:bg-blue-600 transition-colors group"
              >
                <FaLinkedin className="text-xl text-gray-400 group-hover:text-white" />
              </a>
              {/* <a 
                href="https://twitter.com"
                target="_blank"
                rel="noopener noreferrer"
                className="p-3 bg-dark rounded-xl hover:bg-sky-500 transition-colors group"
              >
                <FaTwitter className="text-xl text-gray-400 group-hover:text-white" />
              </a> */}
            </div>
          </div>

          {/* Fun Quote */}
          <div className="bg-gradient-to-r from-primary/10 via-pink-500/10 to-purple-500/10 rounded-2xl p-6 border border-primary/20">
            <p className="text-gray-400 italic text-sm">
              "The best way to predict the future is to create it."
            </p>
            <p className="text-primary text-xs mt-2">— Peter Drucker</p>
          </div>
        </div>

        {/* Contact Form */}
        <div className="lg:col-span-3">
          <div className="bg-gradient-to-br from-secondary to-dark rounded-2xl p-8 border border-primary/10">
            <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
              <FaPaperPlane className="text-primary" />
              Send a Message
            </h2>

            {sent ? (
              <div className="text-center py-12">
                <div className="w-20 h-20 mx-auto bg-green-500/20 rounded-full flex items-center justify-center mb-4">
                  <FaHeart className="text-3xl text-green-500" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">Message Sent!</h3>
                <p className="text-gray-400">Thank you for reaching out. I'll get back to you soon!</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-5">
                <div className="grid md:grid-cols-2 gap-5">
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Your Name</label>
                    <input
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      required
                      className="w-full bg-dark border border-gray-700 rounded-xl px-4 py-3 text-white
                               focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
                      placeholder="John Doe"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Email Address</label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      className="w-full bg-dark border border-gray-700 rounded-xl px-4 py-3 text-white
                               focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
                      placeholder="john@example.com"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm text-gray-400 mb-2">Subject</label>
                  <input
                    type="text"
                    name="subject"
                    value={formData.subject}
                    onChange={handleChange}
                    required
                    className="w-full bg-dark border border-gray-700 rounded-xl px-4 py-3 text-white
                             focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
                    placeholder="How can I help you?"
                  />
                </div>

                <div>
                  <label className="block text-sm text-gray-400 mb-2">Message</label>
                  <textarea
                    name="message"
                    value={formData.message}
                    onChange={handleChange}
                    required
                    rows={5}
                    className="w-full bg-dark border border-gray-700 rounded-xl px-4 py-3 text-white
                             focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all resize-none"
                    placeholder="Write your message here..."
                  />
                </div>

                <button
                  type="submit"
                  disabled={isSending}
                  className="w-full bg-gradient-to-r from-primary to-pink-500 text-white font-semibold
                           py-4 rounded-xl hover:opacity-90 transition-all disabled:opacity-50
                           flex items-center justify-center gap-2 group"
                >
                  {isSending ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Sending...
                    </>
                  ) : (
                    <>
                      <FaPaperPlane className="group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                      Send Message
                    </>
                  )}
                </button>
              </form>
            )}
          </div>
        </div>
      </div>

      {/* Decorative elements */}
      <div className="fixed top-20 left-10 w-72 h-72 bg-primary/5 rounded-full blur-3xl pointer-events-none" />
      <div className="fixed bottom-20 right-10 w-96 h-96 bg-pink-500/5 rounded-full blur-3xl pointer-events-none" />
    </div>
  )
}
