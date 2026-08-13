import { BrowserRouter, Route, Routes } from "react-router-dom";

import AuthGate from "./auth/AuthGate";
import Background from "./components/Background";
import Footer from "./components/Footer";
import Header from "./components/Header";
import LoginPage from "./views/LoginPage";
import NotFound from "./views/NotFound";
import PrivateHome from "./views/PrivateHome";
import PublicHome from "./views/PublicHome";
import SignUp from "./views/SignUp";
import ThingDetail from "./views/ThingDetail";
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
            <Route path="/" element={<PublicHome />} />
            <Route path="/home" element={<PublicHome />} />
            <Route path="/thing/detail/:uuid" element={<ThingDetail />} />
            <Route path="/users/login" element={<LoginPage />} />
            <Route path="/users/signup" element={<SignUp />} />
            <Route
              path="/home/private"
              element={
                <AuthGate>
                  <PrivateHome />
                </AuthGate>
              }
            />
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
