import type { Metadata } from "next";
import ChatWidget from "@/components/ChatWidget";
import "./globals.css";

export const metadata: Metadata = {
  title: "מדריך טוקיו - Tokyo Travel Guide",
  description:
    "מדריך טיולים מקיף לטוקיו בעברית. מסעדות, אטרקציות, שכונות, תחבורה, קניות ועוד.",
  keywords: [
    "טוקיו",
    "יפן",
    "מדריך טיולים",
    "Tokyo",
    "Japan",
    "travel guide",
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="he" dir="rtl">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-white text-gray-900 min-h-screen flex flex-col">
        {children}
        <ChatWidget />
      </body>
    </html>
  );
}
