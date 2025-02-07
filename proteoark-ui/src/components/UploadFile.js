import React, { useState } from "react";
import axios from "axios";

const UploadFile = () => {
  const [file, setFile] = useState(null);
  const [noOfSample, setNoOfSample] = useState("");
  const [noOfControl, setNoOfControl] = useState("");
  const [expType, setExpType] = useState("");
  const [uploadStatus, setUploadStatus] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async () => {
    if (!file || !noOfSample || !noOfControl || !expType) {
      return alert("Please fill all fields and select a file.");
    }

    try {
      const formData = new FormData();
      formData.append("file", file);

      const { data } = await axios.post(
        "http://localhost:8000/aws/upload-file",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      const fileUrl = data.file_url;
      console.log(fileUrl);
      const response = await axios.post(
        "http://localhost:8000/analysis/pre-analysis",
        {
          noOfTest: noOfSample,
          noOfControl: noOfControl,
          expType,
          fileUrl,
        }
      );

      setUploadStatus("File and metadata saved successfully!");
    } catch (err) {
      console.error(err);
      setUploadStatus("An error occurred while uploading.");
    }
  };

  return (
    <div>
      <input
        type="number"
        placeholder="No. of Samples"
        value={noOfSample}
        onChange={(e) => setNoOfSample(e.target.value)}
      />
      <input
        type="number"
        placeholder="No. of Controls"
        value={noOfControl}
        onChange={(e) => setNoOfControl(e.target.value)}
      />
      <input
        type="text"
        placeholder="Experiment Type"
        value={expType}
        onChange={(e) => setExpType(e.target.value)}
      />
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleSubmit}>Upload File and Submit</button>
      <p>{uploadStatus}</p>
    </div>
  );
};

export default UploadFile;
