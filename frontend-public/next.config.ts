import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  webpack: (config, { dev }) => {
    if (dev) {
      // Disable webpack caching in development to resolve Next.js Client Manifest mismatch issues on Windows
      config.cache = false;
    }
    return config;
  }
};

export default nextConfig;
