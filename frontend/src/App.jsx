import "./App.css";
import { useState, useEffect } from "react";
import axios from "axios";

const API_BASE = "https://malaria-object-detection.onrender.com";

function App() {

  const [page, setPage] = useState(1);

  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [resultImage, setResultImage] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [flash, setFlash] = useState(null);

  const handleImage = (e) => {

    const file = e.target.files[0];

    if (!file) return;

    setImage(file);
    setPreview(URL.createObjectURL(file));

    setResult(null);
    setResultImage(null);
  };

  const playAlert = (type) => {

    try {

      const ctx = new (window.AudioContext || window.webkitAudioContext)();

      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.connect(gain);
      gain.connect(ctx.destination);

      if (type === "infected") {
        osc.type = "square";
        osc.frequency.setValueAtTime(440, ctx.currentTime);
        osc.frequency.setValueAtTime(220, ctx.currentTime + 0.15);
        osc.frequency.setValueAtTime(440, ctx.currentTime + 0.3);
      } else {
        osc.type = "sine";
        osc.frequency.setValueAtTime(660, ctx.currentTime);
        osc.frequency.setValueAtTime(880, ctx.currentTime + 0.15);
      }

      gain.gain.setValueAtTime(0.15, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.5);

      osc.start();
      osc.stop(ctx.currentTime + 0.5);

    } catch (e) {

      console.log("Audio not available:", e);

    }

  };

  const uploadImage = async () => {

    if (!image) {
      alert("Please select an image.");
      return;
    }

    const formData = new FormData();
    formData.append("image", image);

    try {

      setLoading(true);

      const res = await axios.post(
  `${API_BASE}/predict`,
  formData,
  {
    headers: {
      "Content-Type": "multipart/form-data"
    },
    timeout: 120000
  }
);

      if (res.data.error) {
        alert(res.data.error);
        return;
      }

      setResult(res.data);

      setResultImage(
        `${API_BASE}/results/${res.data.image}`
      );

      setPage(2);

    }

   catch (err) {

  console.log("FULL ERROR:", err);

  if (err.response) {
    alert(
      "Backend reached but prediction failed: " +
      JSON.stringify(err.response.data)
    );
  }
  else if (err.request) {
    alert("Cannot reach backend. Check CORS or internet.");
  }
  else {
    alert("Error: " + err.message);
  }

}

    finally {

      setLoading(false);

    }

  };

  const formatLabel = (label) =>
    label
      .split(" ")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");

  useEffect(() => {

    document.body.classList.remove("state-infected", "state-healthy");

    if (result?.diagnosis === "INFECTED") {
      document.body.classList.add("state-infected");
      setFlash("infected");
      playAlert("infected");
      const timer = setTimeout(() => setFlash(null), 500);
      return () => clearTimeout(timer);
    } else if (result?.diagnosis === "UNINFECTED") {
      document.body.classList.add("state-healthy");
      setFlash("healthy");
      playAlert("healthy");
      const timer = setTimeout(() => setFlash(null), 500);
      return () => clearTimeout(timer);
    }

  }, [result]);

  useEffect(() => {

    return () => {
      document.body.classList.remove("state-infected", "state-healthy");
    };

  }, []);

  return (

    <>

    {flash &&
      <div className={`flashOverlay flash-${flash}`}></div>
    }

    <div className="container">

      {/* Header */}

      <div className="header">

        <div className="headerEyebrow">Specimen analysis</div>

        <h1>Malaria diagnosis</h1>

        <p>Blood smear · Parasite Stage Identification & Automated Review · </p>

      </div>

      {/* Navigation */}

      <div className="navBar">

        <button
          className={`navButton ${page===1 ? "activeBtn" : ""}`}
          onClick={()=>setPage(1)}
        >
          Upload
        </button>

        <button
          className={`navButton ${page===2 ? "activeBtn" : ""}`}
          disabled={!result}
          onClick={()=>setPage(2)}
        >
          Detection
        </button>

        <button
          className={`navButton ${page===3 ? "activeBtn" : ""}`}
          disabled={!result}
          onClick={()=>setPage(3)}
        >
          Report
        </button>

      </div>


      {/* PAGE 1 */}

      {page===1 &&

      <div className="uploadBox">

        <div className="slideMark slideMarkTL"></div>
        <div className="slideMark slideMarkBR"></div>

        <h2>Upload blood smear image</h2>

        <label className="fileLabel">
          <input
            type="file"
            accept="image/*"
            onChange={handleImage}
          />
        </label>

        {image && (
          <p className="selectedFile">
            Selected file: {image.name}
          </p>
        )}

        <button
          className="primaryButton"
          onClick={uploadImage}
          disabled={loading}
        >
          {loading ? "Detecting..." : "Detect malaria"}
        </button>

        {loading &&

        <h3 className="loading">

          Analyzing specimen...

        </h3>

        }

      </div>

      }



      {/* PAGE 2 */}

      {page===2 && result &&

      <>

      <div className="images">

        <div className="card">

          <h2>Uploaded image</h2>

          <div className="imageBox">

            <img
              src={preview}
              className="previewImage"
              alt="Uploaded blood smear"
            />

          </div>

        </div>

        <div className="card">

          <h2>Detection overlay</h2>

          <div className="imageBox">

            <img
              src={resultImage}
              className="previewImage"
              alt="Detection result with bounding boxes"
            />

          </div>

        </div>

      </div>

      <div className="summary">

        <div className="slideMark slideMarkTL"></div>
        <div className="slideMark slideMarkBR"></div>

        <h2>Detected objects</h2>

        <table className="countTable">

          <thead>

            <tr>

              <th>Object</th>
              <th>Count</th>

            </tr>

          </thead>

          <tbody>

          {Object.entries(result.detections).map(([k,v])=>

          <tr key={k}>

            <td>{formatLabel(k)}</td>

            <td>{v}</td>

          </tr>

          )}

          </tbody>

        </table>

      </div>

      </>

      }



      {/* PAGE 3 */}

      {page===3 && result &&

      <>

      <div className="stats">

        <div className="statCard">

          <h3>Total objects</h3>

          <h1>{result.total_objects}</h1>

        </div>

        <div className="statCard">

          <h3>Parasites</h3>

          <h1>{result.parasite_count}</h1>

        </div>

        <div className="statCard">

          <h3>Infection</h3>

          <h1>{result.infection_percentage}%</h1>

        </div>

        <div className="statCard">

          <h3>Avg confidence</h3>

          <h1>{result.average_confidence}%</h1>

        </div>

      </div>


      <div className="summary">

        <div className="slideMark slideMarkTL"></div>
        <div className="slideMark slideMarkBR"></div>

        <h2>Parasite confidence log</h2>

        {result.infected_cells.length > 0 ? (

        <table className="countTable">

          <thead>

            <tr>

              <th>Parasite</th>
              <th>Confidence</th>

            </tr>

          </thead>

          <tbody>

          {result.infected_cells.map((cell,index)=>

          <tr key={index}>

            <td>{cell.type}</td>

            <td>{cell.confidence}%</td>

          </tr>

          )}

          </tbody>

        </table>

        ) : (

        <p>No parasites detected.</p>

        )}

      </div>


      <div
        className={
          result.diagnosis==="INFECTED"
          ?
          "diagnosis infected"
          :
          "diagnosis healthy"
        }
      >

        <div className="diagnosisEyebrow">Final diagnosis</div>

        <h1>{result.diagnosis}</h1>

        <p>

          {result.diagnosis==="INFECTED"
          ?
          "Malaria parasite detected."
          :
          "No malaria parasite detected."
          }

        </p>

      </div>

      </>

      }

    </div>

    </>

  );

}

export default App;
