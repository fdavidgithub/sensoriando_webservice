interface Props {
  message: string;
}

export default function ErrorBanner({ message }: Props) {
  return (
    <p className="font-17px" role="alert">
      {message}
    </p>
  );
}
