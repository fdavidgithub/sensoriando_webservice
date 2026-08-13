import { Link, useNavigate } from "react-router-dom";

import { readSession, clearSession } from "../auth/session";

export default function Header() {
  const session = readSession();
  const navigate = useNavigate();

  // clearSession only touches localStorage, which React does not observe. The
  // navigation is what re-renders this component so the menu flips back to
  // "Cadastrar / Entrar" instead of still showing the username.
  function signOut() {
    clearSession();
    navigate("/", { replace: true });
  }

  return (
    <nav>
      <Link to="/" className="font-27px">
        Sensoriando
      </Link>

      <div className="dropdown">
        <img src="/img/bars.svg" alt="menu icon" />

        <div className="dropdown-content">
          {session ? (
            <>
              <Link to="/home/private" className="font-16px">
                Meus dispositivos
              </Link>
              <Link to={`/users/account/${session.username}/profile`} className="font-16px">
                {session.username}
              </Link>
              <button className="font-16px" onClick={signOut} type="button">
                Sair
              </button>
            </>
          ) : (
            <>
              <Link to="/users/signup" className="font-16px">
                Cadastrar
              </Link>
              <Link to="/users/login" className="font-16px">
                Entrar
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
