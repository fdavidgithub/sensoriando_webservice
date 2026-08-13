import { BrowserRouter, Route, Routes } from "react-router-dom";

import Background from "./components/Background";
import Footer from "./components/Footer";
import Header from "./components/Header";
import NotFound from "./views/NotFound";
import { config } from "./config";

function ConfigurationNotice() {
  return (
    <section className="home">
      <div>
        <h1 className="font-36px">Aplicação sem configuração</h1>
        <p className="font-17px">
          A URL da API não foi resolvida durante o build. Refaça o build com acesso à
          conta AWS do ambiente.
        </p>
      </div>
    </section>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Background />
      <header>
        <Header />
      </header>

      <main>
        {config.apiConfigured ? (
          <Routes>
            <Route path="/" element={<NotFound />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        ) : (
          <ConfigurationNotice />
        )}
      </main>

      <footer>
        <Footer />
      </footer>
    </BrowserRouter>
  );
}
