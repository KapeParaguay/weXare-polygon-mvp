"use client";

import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../../../lib/api";

export default function WorkerFeed() {
  const { t } = useTranslation();
  const [tasks, setTasks] = useState<any[]>([]);

  useEffect(() => {
    api("/worker/feed").then((r: any) => setTasks(r.tasks || [])).catch(() => null);
  }, []);

  const accept = async (id: number) => {
    await api(`/tasks/${id}/accept`, { method: "POST" });
    setTasks((prev) => prev.filter((t) => t.id !== id));
  };

  const decline = async (id: number) => {
    await api(`/tasks/${id}/decline`, { method: "POST" });
    setTasks((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">{t("worker_feed_title")}</h1>
      <p className="text-sm text-slate-600">{t("worker_feed_note")}</p>
      <div className="mt-4 grid gap-3">
        {tasks.length === 0 && (
          <div className="text-sm text-slate-500">{t("feed_empty")}</div>
        )}
        {tasks.map((task) => (
          <div key={task.id} className="border rounded p-3">
            <div className="text-sm text-slate-500">Quest #{task.quest_id}</div>
            <div className="mt-2 flex gap-2">
              <button className="button" onClick={() => accept(task.id)}>{t("feed_accept")}</button>
              <button className="border rounded px-3 py-2" onClick={() => decline(task.id)}>{t("feed_reject")}</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
