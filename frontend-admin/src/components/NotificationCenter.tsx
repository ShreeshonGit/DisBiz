import React, { useState, useEffect } from "react";
import { Check, CheckSquare, BellOff, Info, AlertOctagon, CheckCircle } from "lucide-react";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

interface Notification {
  id: string;
  event_type: string;
  message: string;
  brand_id?: string;
  created_at: string;
  read: boolean;
  brands?: {
    name: string;
  };
}

export default function NotificationCenter() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchNotifications = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/notifications?limit=50`);
      if (res.ok) {
        const data = await res.json();
        setNotifications(data);
      }
    } catch (e) {
      console.error("Failed to fetch notifications", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
    // Poll notifications every 10 seconds for real-time dashboard notifications
    const interval = setInterval(fetchNotifications, 10000);
    return () => clearInterval(interval);
  }, []);

  const markAsRead = async (id: string) => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/notifications/${id}/read`, {
        method: "POST"
      });
      if (res.ok) {
        setNotifications((prev) =>
          prev.map((n) => (n.id === id ? { ...n, read: true } : n))
        );
      }
    } catch (e) {
      console.error("Failed to mark read", e);
    }
  };

  const markAllAsRead = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/notifications/read-all`, {
        method: "POST"
      });
      if (res.ok) {
        setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
      }
    } catch (e) {
      console.error("Failed to mark all read", e);
    }
  };

  const unreadCount = notifications.filter((n) => !n.read).length;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-zinc-800 pb-5">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-zinc-50 mb-1">
            Notifications Center
          </h1>
          <p className="text-sm text-slate-500 dark:text-zinc-400">
            Platform event logs, crawler alerts, and scraper execution reports.
          </p>
        </div>

        {unreadCount > 0 && (
          <button
            onClick={markAllAsRead}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-50 border border-slate-250 dark:bg-zinc-800 dark:border-zinc-700 hover:bg-slate-100 dark:hover:bg-zinc-700 text-xs font-semibold rounded-lg text-slate-700 dark:text-zinc-300"
          >
            <CheckSquare className="h-3.5 w-3.5" />
            Mark All as Read
          </button>
        )}
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400 dark:text-zinc-600">Loading alerts logs...</div>
      ) : notifications.length === 0 ? (
        <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-16 text-center max-w-xl mx-auto shadow-sm animate-fade-in">
          <BellOff className="h-12 w-12 text-slate-300 dark:text-zinc-750 mx-auto mb-4" />
          <h3 className="font-semibold text-slate-800 dark:text-zinc-200 mb-1">No Alerts Logged</h3>
          <p className="text-sm text-slate-500 dark:text-zinc-500">Notifications will be fired when scraper runs complete or fail.</p>
        </div>
      ) : (
        <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl overflow-hidden shadow-xs divide-y divide-slate-150 dark:divide-zinc-800 animate-fade-in">
          {notifications.map((n) => {
            let Icon = Info;
            let iconColor = "text-sky-500 bg-sky-50 dark:bg-sky-500/10";
            
            if (n.event_type === "job_failed" || n.event_type === "schedule_failed" || n.event_type === "retry_exhausted") {
              Icon = AlertOctagon;
              iconColor = "text-red-500 bg-red-50 dark:bg-red-500/10";
            } else if (n.event_type === "job_completed" || n.event_type === "new_dealers_discovered") {
              Icon = CheckCircle;
              iconColor = "text-emerald-500 bg-emerald-50 dark:bg-emerald-500/10";
            }

            return (
              <div
                key={n.id}
                className={`p-4 flex items-start justify-between gap-4 transition-colors duration-150 ${
                  !n.read ? "bg-slate-50/50 dark:bg-zinc-800/20" : ""
                }`}
              >
                <div className="flex items-start gap-3.5">
                  <div className={`h-8 w-8 rounded-lg flex items-center justify-center ${iconColor}`}>
                    <Icon className="h-4.5 w-4.5" />
                  </div>
                  <div className="space-y-1">
                    <p className={`text-sm ${!n.read ? "font-semibold text-slate-900 dark:text-zinc-150" : "text-slate-700 dark:text-zinc-450"}`}>
                      {n.message}
                    </p>
                    <div className="flex items-center gap-2 text-xs text-slate-400 dark:text-zinc-500">
                      <span>{n.brands?.name || "Global System"}</span>
                      <span>•</span>
                      <span>{new Date(n.created_at).toLocaleString()}</span>
                    </div>
                  </div>
                </div>

                {!n.read && (
                  <button
                    onClick={() => markAsRead(n.id)}
                    className="p-1 rounded-md hover:bg-slate-100 dark:hover:bg-zinc-800 text-slate-400 hover:text-slate-700 dark:text-zinc-650 dark:hover:text-zinc-400"
                    title="Mark as read"
                  >
                    <Check className="h-4 w-4" />
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
