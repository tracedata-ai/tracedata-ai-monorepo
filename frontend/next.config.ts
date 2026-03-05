import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Emit a self-contained server.js used by the Docker runner stage.
  // See: https://nextjs.org/docs/app/api-reference/config/next-config-js/output
  output: "standalone",
};

export default nextConfig;
