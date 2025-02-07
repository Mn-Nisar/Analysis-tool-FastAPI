import logo from "./logo.svg";
import "./App.css";
import UploadFile from "./components/UploadFile";
import DragDropList from "./components/DragDropList";
function App() {
  return (
    <div className="App">
      <h1>Helloo</h1>
      <UploadFile />
      <DragDropList />
    </div>
  );
}

export default App;
