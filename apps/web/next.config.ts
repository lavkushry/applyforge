import type { NextConfig } from "next";

const configuredOrigins = process.env.NEXT_PUBLIC_ALLOWED_DEV_ORIGINS
  ? process.env.NEXT_PUBLIC_ALLOWED_DEV_ORIGINS.split(",").map((value) => value.trim()).filter(Boolean)
  : [];

const allowedDevOrigins = Array.from(
  new Set(["http://localhost:3000", "http://127.0.0.1:3000", "http://172.24.28.220:3000", ...configuredOrigins]),
);

const nextConfig: NextConfig = {
  typedRoutes: true,
  allowedDevOrigins,
};

export default nextConfig
