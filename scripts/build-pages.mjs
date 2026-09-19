import { spawnSync } from "node:child_process";

const result = spawnSync(process.execPath, ["node_modules/next/dist/bin/next", "build"], {
  env: {
    ...process.env,
    GITHUB_PAGES: "1",
    NEXT_PUBLIC_BASE_PATH: "/GOAI2026_kbrs",
  },
  stdio: "inherit",
});

if (result.error) throw result.error;
process.exit(result.status ?? 1);
