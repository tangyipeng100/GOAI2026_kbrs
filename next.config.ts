import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  ...(process.env.GITHUB_PAGES === "1"
    ? {
        output: "export" as const,
        basePath: "/GOAI2026_kbrs",
        images: { unoptimized: true },
      }
    : {}),
};

export default nextConfig;
