/// <reference types="vite/client" />

declare namespace JSX {
  interface IntrinsicElements {
    font: React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement> & {
      color?: string;
      face?: string;
      size?: string | number;
    };
  }
}
