import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/Header";
import { cn } from "@/lib/utils";

export const metadata: Metadata = {
  title: "Macy's Test Data Platform",
  description: "AI-powered test data generation for eCommerce",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={cn("min-h-screen bg-white font-sans antialiased")}>
        <Header />
        <main className="container mx-auto px-4 py-6">
          {children}
        </main>
      </body>
    </html>
  );
}