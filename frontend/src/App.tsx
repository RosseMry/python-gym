import { Route, Routes } from "react-router-dom";
import { ExerciseListPage } from "./pages/ExerciseListPage";
import { ExercisePage } from "./pages/ExercisePage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<ExerciseListPage />} />
      <Route path="/exercises/:id" element={<ExercisePage />} />
    </Routes>
  );
}
