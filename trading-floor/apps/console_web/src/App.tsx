import { Navigate, Route, Routes } from "react-router-dom";

import { Page } from "./Page";
import { ROUTES } from "./routes";
import { Shell } from "./Shell";
import type { Fetcher } from "./api";

type Props = {
  fetcher?: Fetcher;
  initialReadToken?: string;
  initialCommandToken?: string;
};

export function App({ fetcher, initialReadToken, initialCommandToken }: Props) {
  return (
    <Routes>
      <Route
        element={
          <Shell fetcher={fetcher} initialReadToken={initialReadToken} initialCommandToken={initialCommandToken} />
        }
      >
        <Route path="/" element={<Navigate to="/floor" replace />} />
        {ROUTES.map((route) => (
          <Route key={route.path} path={route.path} element={<Page path={route.path} />} />
        ))}
      </Route>
    </Routes>
  );
}
