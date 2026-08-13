import { useNavigate } from "react-router-dom";

import { writeSession } from "../auth/session";

const GUEST_USERNAME = "visitante";

export default function LoginPage() {
  const navigate = useNavigate();

  function enter() {
    writeSession(GUEST_USERNAME);
    navigate("/home/private");
  }

  return (
    <>
      <section className="home">
        <div>
          <h1 className="font-36px">Autenticar usuário</h1>
        </div>
      </section>

      <section className="signUp">
        <p className="font-17px">
          A autenticação ainda não foi implementada. Este acesso é temporário e serve
          apenas para visualizar as telas privadas.
        </p>
        <button type="button" className="font-16px" onClick={enter}>
          <span>Entrar</span>
        </button>
      </section>
    </>
  );
}
