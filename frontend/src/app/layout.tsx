import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import "./globals.css";
import { NotificationCenter } from "../features/notifications/compoents/notification-center";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "swap",
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "MarketPulse AI",
    template: "%s | MarketPulse AI",
  },
  description:
    "A resumable realtime stock-analysis assistant powered by durable SSE event streaming.",
  keywords: [
    "stock analysis",
    "financial research",
    "realtime streaming",
    "SSE",
    "MarketPulse AI",
  ],
  authors: [
    {
      name: "MarketPulse AI",
    },
  ],
  robots: {
    index: true,
    follow: true,
  },
};

interface RootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: Readonly<RootLayoutProps>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} min-h-screen bg-[#080b12] font-sans text-slate-100 antialiased`}
      >
        {children}
        <NotificationCenter />
      </body>
    </html>
  );
}
