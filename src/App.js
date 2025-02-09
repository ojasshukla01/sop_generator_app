import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './index.css'; // Optional for styles

const App = () => {
  return (
    <Router>
      <div style={{ textAlign: 'center' }}>
        <h1>SOP Generator Application</h1>
        <p>Welcome! Please register or log in to generate your SOP.</p>
        <Routes>
          <Route path="/" element={<Home />} />
          {/* More routes to be added */}
        </Routes>
      </div>
    </Router>
  );
};

const Home = () => <div>This is the Home Page!</div>;

export default App;
