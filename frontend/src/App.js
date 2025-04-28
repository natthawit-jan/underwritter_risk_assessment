import React, { useState } from 'react';
import './App.css';

function App() {
  const [address, setAddress] = useState('');
  const [modelType, setModelType] = useState('ollama');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:5555/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ address, model_type: modelType }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Something went wrong');
      }
      
      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message || 'An error occurred while processing your request. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Simple function to format the markdown text
  const formatMarkdown = (text) => {
    if (!text) return { __html: '' };
    
    // Format the markdown content
    let formattedText = text
      // Replace markdown bold (**text**) with HTML bold
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Add styling for headers (Risk Assessment Summary, Major Risks, etc.)
      .replace(/<strong>(Risk Assessment Summary|Major Risks|Other Potential Risks|Risk Rating|Underwriting Recommendations)<\/strong>/g, 
        '<h4 class="risk-section-title">$1</h4>')
      // Format numbered lists (1. **Item:**)
      .replace(/(\d+)\.\s+<strong>(.*?):<\/strong>/g, 
        '<div class="risk-item"><span class="risk-number">$1.</span> <span class="risk-title">$2:</span>')
      // Add paragraph breaks
      .replace(/\n\n/g, '</div>\n\n<div class="risk-paragraph">')
      // Close any open divs
      + '</div>';
    
    return { __html: formattedText };
  };

  return (
    <div className="App">
      <div className="container">
        <h1>Property Risk Assessment</h1>
        
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <input
              type="text"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              placeholder="Enter a property address"
              required
            />
            <select 
              value={modelType}
              onChange={(e) => setModelType(e.target.value)}
              className="model-select"
            >
              <option value="ollama">Ollama (Local)</option>
              <option value="openai">OpenAI</option>
            </select>
            <button type="submit" disabled={loading}>
              {loading ? 'Processing...' : 'Analyze Risk'}
            </button>
          </div>
        </form>

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Analyzing property risk...</p>
          </div>
        )}

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        {results && !loading && (
          <div className="results">
            <h2>Risk Assessment Results</h2>
            
            <div className="result-section">
              <h3>Property Details</h3>
              <p>{results.fullAddress}</p>
              <p className="coordinates">Coordinates: {results.coordinates.lat}, {results.coordinates.lon}</p>
            </div>
            
            <div className="result-section">
              <h3>FEMA Disaster History</h3>
              {results.femaDisasters.length === 0 ? (
                <p>No FEMA disasters found nearby.</p>
              ) : (
                <ul>
                  {results.femaDisasters.map((disaster, index) => (
                    <li key={index}>
                      {disaster.disasterType} at {disaster.distance_miles} miles ({disaster.date})
                    </li>
                  ))}
                </ul>
              )}
            </div>
            
            <div className="risk-summary">
              <h3>Risk Summary</h3>
              <div 
                className="risk-content"
                dangerouslySetInnerHTML={formatMarkdown(results.riskSummary)} 
              />
            </div>
          </div>
        )}

        <div className="footer">
          <p>Powered by FEMA API, DuckDuckGo Search, and {modelType === 'ollama' ? 'Ollama LLM' : 'OpenAI'}</p>
        </div>
      </div>
    </div>
  );
}

export default App;