import { useEffect, useRef } from "react";
import {
  BarController,
  BarElement,
  CategoryScale,
  Chart,
  Legend,
  LineController,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
} from "chart.js";

import type { ChartType } from "../lib/prefs";

Chart.register(
  BarController,
  BarElement,
  CategoryScale,
  Legend,
  LineController,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
);

interface Point {
  legend: string;
  value: number;
}

interface Props {
  points: Point[];
  label: string;
  type: Exclude<ChartType, "table" | "display">;
}

export default function SensorChart({ points, label, type }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const chart = new Chart(canvas, {
      type,
      data: {
        labels: points.map((point) => point.legend),
        datasets: [
          {
            label,
            pointStyle: "circle",
            pointRadius: 5,
            backgroundColor: "white",
            borderColor: "red",
            data: points.map((point) => point.value),
            fill: false,
          },
        ],
      },
      options: {
        responsive: true,
        scales: {
          x: { display: true, title: { display: true, text: label } },
          y: { display: true, title: { display: false, text: "Value" } },
        },
      },
    });

    // Chart.js keeps a canvas registry; without this a re-render throws
    // "Canvas is already in use".
    return () => chart.destroy();
  }, [points, label, type]);

  return <canvas ref={canvasRef} />;
}
