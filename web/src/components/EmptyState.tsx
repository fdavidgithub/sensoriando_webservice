interface Props {
  message?: string;
}

export default function EmptyState({ message = "Não há dispositivos para exibir." }: Props) {
  return (
    <ul>
      <li>
        <div>
          <img src="/img/nosensor.png" alt="Icon" />
        </div>
        <h3 className="font-22px">Ops...</h3>
        <p className="font-17px">{message}</p>
      </li>
    </ul>
  );
}
