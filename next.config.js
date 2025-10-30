/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  experimental: {
    turbo: {
      root: __dirname,
    },
  },
};

module.exports = nextConfig;
