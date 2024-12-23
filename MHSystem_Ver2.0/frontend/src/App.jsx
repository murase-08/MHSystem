import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import Navigation from './components/Navigation';
import DifferenceDetection from './pages/DifferenceDetection';
import DifferenceList from './pages/DifferenceList';

function App() {
  return (
    <Router>
      <div>
        <Header />
        <Navigation />
        <main>
          <Routes>
            <Route path="/" element={<DifferenceDetection />} />
            <Route path="/difference-list" element={<DifferenceList />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;