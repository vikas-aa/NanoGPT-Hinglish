import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async rewrites() {
    // In local development, proxy /api/* to the FastAPI server on port 8000.
    // In production (Vercel), no rewrites — the frontend calls the
    // Hugging Face Space backend directly via NEXT_PUBLIC_API_URL.
    if (process.env.NODE_ENV === "development") {
      return [
        {
          source: "/api/:path*",
          destination: "http://127.0.0.1:8000/api/:path*",
        },
      ];
    }
    return [];
  },
};

export default nextConfig;
