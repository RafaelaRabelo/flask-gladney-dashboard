// frontend/pages/index.tsx
import Head from 'next/head'

export default function Home() {
  return (
    <>
      <Head>
        <title>Gladney Dashboard</title>
      </Head>
      <main className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 p-10">
        <h1 className="text-4xl font-bold mb-4">Gladney Dashboard</h1>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="bg-white dark:bg-gray-800 shadow rounded p-6">
            <h2 className="text-xl font-semibold mb-2">Expectant Mother Dashboard</h2>
            <iframe
              src="https://lookerstudio.google.com/embed/reporting/018fe7d3-8e30-4a70-86e9-ac5b71bdb662/page/p_iv91iy4nsd"
              className="w-full h-[400px] rounded"
              loading="lazy"
            ></iframe>
          </div>

          <div className="bg-white dark:bg-gray-800 shadow rounded p-6">
            <h2 className="text-xl font-semibold mb-2">Business Performance Dashboard</h2>
            <iframe
              src="https://lookerstudio.google.com/embed/reporting/704ba1ac-c624-464f-a9f5-4f0f7ecadbfc/page/p_0cruxnlesd"
              className="w-full h-[400px] rounded"
              loading="lazy"
            ></iframe>
          </div>
        </div>
      </main>
    </>
  )
}
