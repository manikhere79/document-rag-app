import React, { useState } from "react";
import { createRoot } from "react-dom/client";

function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [context, setContext] = useState("");
  const [loading, setLoading] = useState(false);

  const uploadFile = async (e) => {
    e.preventDefault();
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    setLoading(true);
    await fetch("http://localhost:8001/upload", {
      method: "POST",
      body: formData,
    });
    setLoading(false);
    alert("File uploaded!");
  };

  const askQuestion = async (e) => {
    e.preventDefault();
    setLoading(true);
    const formData = new FormData();
    formData.append("question", question);
    const res = await fetch("http://localhost:8001/query", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    setAnswer(data.answer);
    setContext(data.context);
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 600, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h2>Simple Knowledgebase</h2>
      <form onSubmit={uploadFile} style={{ marginBottom: 20 }}>
        <input type="file" accept=".txt" onChange={e => setFile(e.target.files[0])} />
        <button type="submit" disabled={loading}>Upload</button>
      </form>
      <form onSubmit={askQuestion}>
        <input
          type="text"
          value={question}
          onChange={e => setQuestion(e.target.value)}
          placeholder="Ask a question..."
          style={{ width: "70%" }}
        />
        <button type="submit" disabled={loading}>Ask</button>
      </form>
      {loading && <p>Loading...</p>}
      {answer && (
        <div style={{ marginTop: 20 }}>
          <strong>Answer:</strong>
          <div>{answer}</div>
          <details style={{ marginTop: 10 }}>
            <summary>Show context</summary>
            <pre>{context}</pre>
          </details>
        </div>
      )}
    </div>
  );
}

const root = createRoot(document.getElementById("root"));
root.render(<App />);
