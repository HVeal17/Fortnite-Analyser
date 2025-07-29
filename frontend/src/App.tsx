import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

// Define the expected structure of the backend response
type UploadResponse = {
  results: string | {
    edit_speed?: string;
    eliminations?: number;
    feedback?: string;
  };
};

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [link, setLink] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  const handleUpload = async () => {
    const formData = new FormData();
    if (file) {
      formData.append('video', file);
    } else if (link) {
      formData.append('link', link);
    } else {
      alert('Please upload a file or paste a link.');
      return;
    }

    setLoading(true);
    try {
      const res = await axios.post<UploadResponse>('http://127.0.0.1:5000/upload', formData);
      
      // Convert result object to string if needed
      const formatted =
        typeof res.data.results === 'string'
          ? res.data.results
          : JSON.stringify(res.data.results, null, 2);
          
      setResult(formatted);
    } catch (err) {
      console.error('Upload failed:', err);
      alert('Upload failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-container">
      <h1 className="upload-title">Fortnite Analyzer</h1>

      <div className="upload-box">
        <label>Upload a video</label>
        <input
          type="file"
          accept="video/*"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />

        <label>Or paste a VOD link</label>
        <input
          type="text"
          placeholder="https://youtube.com/..."
          value={link}
          onChange={(e) => setLink(e.target.value)}
        />

        <button onClick={handleUpload} disabled={loading}>
          {loading ? 'Uploading...' : 'Analyze'}
        </button>

        {result && (
          <div className="result-box">
            <h2>Analysis Result</h2>
            <pre>{result}</pre>
          </div>
        )}
      </div>
    </div>
  );
}
