/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'assets.macysassets.com',
        pathname: '/**',
      },
    ],
  },
  async rewrites() {
    return [
      {
        source: '/api/grpc/:path*',
        destination: 'http://localhost:8082/:path*', // HTTP health endpoints
      },
    ];
  },
};

module.exports = nextConfig;