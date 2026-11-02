import { ROUTES } from "./routes";

export function Page({ path }: { path: string }) {
  const route = ROUTES.find((item) => item.path === path);
  return (
    <article>
      <h1 className="text-2xl font-semibold text-neon">{route?.title}</h1>
      <p className="mt-3 max-w-prose text-zinc-300">{route?.body}</p>
    </article>
  );
}
