import React, { useState, useEffect } from 'react';
//import './App.css';

function App() {
  const [files, setFiles] = useState([]);
  const [solution, setSolution] = useState(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [imagePreviews, setImagePreviews] = useState([]);

  useEffect(() => {
    if (files.length > 0) { console.log(`${files.length} file(s) added properly:`, files.map(f => f.name)); }
  }, [files]);

  // Effect to create and clean up image previews
  useEffect(() => {
    const newImagePreviews = files.map(file => URL.createObjectURL(file));
    setImagePreviews(newImagePreviews);

    return () => {
      newImagePreviews.forEach(url => URL.revokeObjectURL(url));
    };
  }, [files]);

  const handleFileChange = (event) => {
    // User can't select more than 6 files
    const selectedFiles = Array.from(event.target.files).slice(0, 6);
    setFiles(selectedFiles);
  };

  // Handle submission
  const handleSubmit = async (event) => {
    event.preventDefault();
    if (files.length !== 6) {
      setError('Please select exactly 6 images.');
      return;
    }

    // Clear previous states
    setIsLoading(true);
    setError('');
    setSolution(null);

    // Prepare data
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    try {
      // vite config proxy handles directing this to backend
      const response = await fetch('/api/solve', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      if (data.error) {
        setError(data.error);
      } else {
        setSolution(data.solution);
      }
    } catch (err) {
      setError('Failed to get solution. Is backend running?');
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Rubik's Cube Solver</h1>
        <form onSubmit={handleSubmit}>
         <div>
            <p>Upload the 6 faces of the cube ({files.length} / 6 selected):</p>
            <input type="file" multiple accept="image/*" onChange={handleFileChange} />
            <button type="submit" disabled={isLoading || files.length !== 6}>
              {isLoading ? 'Solving...' : 'Solve Cube'}
            </button>
          </div>
        </form>

        {imagePreviews.length > 0 && (
          <div className="image-previews">
            <h4>Selected Images:</h4>
            <div>
              {imagePreviews.map((preview, index) => (
                <img key={index} src={preview} alt={`preview ${index}`} width="100" />
              ))}
            </div>
          </div>
        )}

        {error && <p className="error">{error}</p>}

        {solution && (
          <div className="solution">
            <h3>Solution Steps:</h3>
            <pre>{solution.join(' ')}</pre>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
