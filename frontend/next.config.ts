import type { NextConfig } from "next";


const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/assessment/:path*',
        destination: 'http://localhost:8000/api/assessment/:path*',
      },
    ];
  },
};

export default nextConfig;
