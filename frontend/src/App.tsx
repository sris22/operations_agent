import { BrowserRouter, Routes, Route } from 'react-router-dom'

function App() {
  return (
    <BrowserRouter>
      <div style={{ fontFamily: 'system-ui, sans-serif', padding: '2rem' }}>
        <h1>AI Customer Operations Agent</h1>
        <Routes>
          <Route path="/" element={<div>Dashboard - Coming Soon</div>} />
          <Route path="/login" element={<div>Login - Coming Soon</div>} />
          <Route path="/chat" element={<div>Chat - Coming Soon</div>} />
          <Route path="/approvals" element={<div>Approvals - Coming Soon</div>} />
          <Route path="/documents" element={<div>Documents - Coming Soon</div>} />
          <Route path="/evaluations" element={<div>Evaluations - Coming Soon</div>} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
