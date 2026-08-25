import { useEffect, useState } from "react";
import { Route, Routes } from "react-router-dom";
import { Sidebar } from "./components/Sidebar";
import { ExerciseListPage } from "./pages/ExerciseListPage";
import { ExercisePage } from "./pages/ExercisePage";
import { RepeatQueuePage } from "./pages/RepeatQueuePage";
import { LearningNotesListPage } from "./pages/LearningNotesListPage";
import { LearningNotePage } from "./pages/LearningNotePage";
import { ThirtyDaysPage } from "./pages/ThirtyDaysPage";
import { SqlExerciseListPage } from "./pages/SqlExerciseListPage";
import { SqlExercisePage } from "./pages/SqlExercisePage";
import { SqlNotesListPage } from "./pages/SqlNotesListPage";
import { SqlNotePage } from "./pages/SqlNotePage";
import { ExamStartPage } from "./pages/ExamStartPage";
import { ExamPage } from "./pages/ExamPage";
import { api } from "./services/api";

export default function App() {
  const [repeatCount, setRepeatCount] = useState(0);

  useEffect(() => {
    refreshRepeatCount();
  }, []);

  function refreshRepeatCount() {
    api.getRepeatQueue().then((items) => setRepeatCount(items.length));
  }

  return (
    <div style={{ display: "flex" }}>
      <Sidebar repeatCount={repeatCount} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <Routes>
          <Route path="/" element={<ExerciseListPage />} />
          <Route
            path="/exercises/:id"
            element={<ExercisePage onRepeatChanged={refreshRepeatCount} />}
          />
          <Route path="/repeat" element={<RepeatQueuePage />} />
          <Route path="/notes" element={<LearningNotesListPage />} />
          <Route path="/notes/:id" element={<LearningNotePage />} />
          <Route path="/thirty-days" element={<ThirtyDaysPage />} />
          <Route path="/sql" element={<SqlExerciseListPage />} />
          <Route path="/sql/exercises/:id" element={<SqlExercisePage />} />
          <Route path="/sql/notes" element={<SqlNotesListPage />} />
          <Route path="/sql/notes/:id" element={<SqlNotePage />} />
          <Route path="/exam" element={<ExamStartPage />} />
          <Route path="/exam/:sessionId" element={<ExamPage />} />
        </Routes>
      </div>
    </div>
  );
}
