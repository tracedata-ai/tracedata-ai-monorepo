import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-900 text-white">
      <h1 className="text-6xl font-bold mb-8">TraceData.ai</h1>
      <p className="text-xl mb-12 text-gray-300">
        Intelligent Fleet Operations Platform
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Link
          href="/dashboard"
          className="group block rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100/10 hover:dark:border-neutral-700 hover:dark:bg-neutral-800/30"
        >
          <h2 className="mb-3 text-2xl font-semibold">
            Fleet Dashboard{" "}
            <span className="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
              -&gt;
            </span>
          </h2>
          <p className="m-0 max-w-[30ch] text-sm opacity-50">
            Monitor vehicle health, routes, and driver performance in real-time.
          </p>
        </Link>

        <Link
          href="/chatbot"
          className="group block rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100/10 hover:dark:border-neutral-700 hover:dark:bg-neutral-800/30"
        >
          <h2 className="mb-3 text-2xl font-semibold">
            Fleet Assistant{" "}
            <span className="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
              -&gt;
            </span>
          </h2>
          <p className="m-0 max-w-[30ch] text-sm opacity-50">
            Ask questions about policies, regulations, and fleet data.
          </p>
        </Link>
      </div>
    </main>
  );
}
