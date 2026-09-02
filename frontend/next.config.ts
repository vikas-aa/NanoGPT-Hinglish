import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async rewrites() {
    // In local development, proxy /api/* to the FastAPI server on port 8000.
    // In production on Vercel, this rewrite is NOT returned — Vercel automatically
    // routes /api/* to api/index.py (the Python serverless function) natively.
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
