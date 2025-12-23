import type { Metadata } from "next";
import "./globals.css";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { ClientProviders } from "@/components/providers/ClientProviders";

export const metadata: Metadata = {
  title: "QA Platform | AI-Powered Test Generation",
  description: "Accelerate your testing workflow with intelligent agents for test cases, test data, and domain expertise",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="flex flex-col min-h-screen">
        <ClientProviders>
          <Header />
          <div className="pt-16 flex-1 flex flex-col">
            {children}
          </div>
          <Footer />
        </ClientProviders>
      </body>
    </html>
  );
}
