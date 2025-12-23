/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'assets.macysassets.com',
        pathname: '/**',
      },
    ],
  },
};

export default nextConfig;
