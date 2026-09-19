import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "恐怖如斯战队｜视觉语义注入具身导航巡检方案",
  description:
    "GOAI 2026 赛道四赛题二：面向产业园区全地形巡逻的定位建图、GoalPoint VLN 与逐站精准停车方案。",
  other: {
    "codex-preview": "development",
  },
  icons: {
    icon: `${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}/favicon.svg`,
    shortcut: `${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}/favicon.svg`,
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
