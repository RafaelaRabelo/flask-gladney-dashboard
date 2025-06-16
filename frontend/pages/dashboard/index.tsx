import DarkModeToggle from '../components/DarkModeToggle';

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-100 p-6">
      <div className="flex justify-end">
        <DarkModeToggle />
      </div>

      <h1 className="text-3xl font-bold mt-4">Gladney Dashboard</h1>

      {/* Aqui você coloca seus iframes ou qualquer conteúdo da dashboard */}
      <div className="mt-8 space-y-6">
        <section>
          <h2 className="text-xl mb-2">Expectant Mother Dashboard</h2>
          <iframe
            src="https://lookerstudio.google.com/embed/reporting/018fe7d3-8e30-4a70-86e9-ac5b71bdb662/page/p_iv91iy4nsd"
            className="w-full h-[500px] rounded shadow"
          ></iframe>
        </section>

        <section>
          <h2 className="text-xl mb-2">Business Performance Dashboard</h2>
          <iframe
            src="https://lookerstudio.google.com/embed/reporting/704ba1ac-c624-464f-a9f5-4f0f7ecadbfc/page/p_0cruxnlesd"
            className="w-full h-[500px] rounded shadow"
          ></iframe>
        </section>
      </div>
    </main>
  );
}
