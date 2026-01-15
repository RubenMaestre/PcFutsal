/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  compress: true,
  poweredByHeader: false,

  images: {
    remotePatterns: [
      { protocol: "http", hostname: "appffcv.filesnovanet.es", pathname: "/**" },
      { protocol: "https", hostname: "appffcv.filesnovanet.es", pathname: "/**" },
    ],
    formats: ["image/avif", "image/webp"],
  },

  experimental: {
    optimizePackageImports: ["lucide-react", "framer-motion", "recharts"],
  },
};

module.exports = nextConfig;
