/** @type {import('next').NextConfig} */
const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const isProd = process.env.NODE_ENV === "production";

const nextConfig = {
  reactStrictMode: true,
  output: "standalone",

  // Security headers
  async headers() {
    const connectSrc = isProd
      ? `'self' ${apiUrl}`
      : `'self' ${apiUrl} http://localhost:8000 http://localhost:18000 http://127.0.0.1:18000`;

    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "X-XSS-Protection", value: "1; mode=block" },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=()",
          },
          ...(isProd
            ? [
                {
                  key: "Strict-Transport-Security",
                  value: "max-age=31536000; includeSubDomains; preload",
                },
              ]
            : []),
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-eval' 'unsafe-inline'",
              "style-src 'self' 'unsafe-inline'",
              "img-src 'self' data: https:",
              "font-src 'self'",
              `connect-src ${connectSrc} https://opencode.ai`,
              "font-src 'self' https://fonts.gstatic.com",
              "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            ].join("; "),
          },
        ],
      },
    ];
  },

  // No root redirect — landing page at / is served directly

  // Proxy API calls to Docker backend in dev
  async rewrites() {
    return [
      {
        source: "/api/backend/:path*",
        destination: `http://localhost:18000/api/:path*`,
      },
      {
        source: "/api/v1/:path*",
        destination: `http://localhost:18000/api/v1/:path*`,
      },
    ];
  },

  images: {
    domains: ["localhost", "api.miraclebirds.ai"],
  },
};

module.exports = nextConfig;
