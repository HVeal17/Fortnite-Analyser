import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [feedback, setFeedback] = useState("");
  const [summary, setSummary] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);
  setLoading(true);

  try {
    const response = await axios.post<{
      feedback: string;
      summary: {
        kills: number;
        accuracy: number;
        rotation_score: number;
        positioning_score: number;
        zone_safety: number;
      };
    }>("http://localhost:5000/upload", formData);

    setFeedback(response.data.feedback);
    setSummary(response.data.summary);
  } catch (error: any) {
    setFeedback("Upload failed. " + (error.response?.data?.error || ""));
  } finally {
    setLoading(false);
  }
};


  return (
    <div className="app">
      <h1>Fortnite Replay Uploader</h1>
      <input type="file" accept=".replay" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={!file || loading}>
        {loading ? "Uploading..." : "Upload Replay"}
      </button>

      {feedback && (
        <div className="feedback">
          <h2>AI Feedback:</h2>
          <pre>{feedback}</pre>
        </div>
      )}

      {summary && (
        <div className="summary">
          <h2>Match Summary</h2>
          <ul>
            <li>Kills: {summary.kills}</li>
            <li>Accuracy: {summary.accuracy}%</li>
            <li>Rotation Score: {summary.rotation_score}</li>
            <li>Positioning Score: {summary.positioning_score}</li>
            <li>Zone Safety: {summary.zone_safety} sec</li>
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
