import { useEffect, useState } from "react";
import { Route, Routes } from "react-router-dom";
import { Sidebar } from "./components/Sidebar";
import { ExerciseListPage } from "./pages/ExerciseListPage";
import { ExercisePage } from "./pages/ExercisePage";
import { RepeatQueuePage } from "./pages/RepeatQueuePage";
import { LearningNotesListPage } from "./pages/LearningNotesListPage";
import { LearningNotePage } from "./pages/LearningNotePage";
import { ThirtyDaysPage } from "./pages/ThirtyDaysPage";
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
        </Routes>
      </div>
    </div>
  );
}
