import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NanoGPT — Hinglish AI",
  description: "Chat with NanoGPT, a custom-trained Hinglish language model.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="font-sans">
        <ThemeInitializer />
        {children}
      </body>
    </html>
  );
}

/**
 * Injects a small inline script that sets the dark-mode class
 * before the page renders to avoid flash-of-unstyled-content.
 */
function ThemeInitializer() {
  return (
    <script
      dangerouslySetInnerHTML={{
        __html: `
          try {
            var t = localStorage.getItem('nanogpt_theme');
            if (t === 'dark' || (!t && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
              document.documentElement.classList.add('dark');
            }
          } catch {}
        `,
      }}
    />
  );
}
