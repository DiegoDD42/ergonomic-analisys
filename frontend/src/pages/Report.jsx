import { useEffect, useState } from "react";
import Button from "react-bootstrap/Button";
import { getHistorico, resetHistorico } from "../services/api";

import RiskChart from "../components/RiskChart";
import HeatmapTimeline from "../components/HeatmapTimeline";

export default function Report() {

    const [historico, setHistorico] = useState(null);

    useEffect(() => {

        const carregar = async () => {
            try {
                const data = await getHistorico();
                setHistorico(data);
            } catch (err) {
                console.error(err);
            }
        };

        carregar();

        const interval = setInterval(
            carregar,
            2000
        );

        return () => clearInterval(interval);

    }, []);

    async function limpar() {

        await resetHistorico();

        const novoHistorico = await getHistorico();

        setHistorico(novoHistorico);
    }

    if (!historico) {
        return <p>Carregando...</p>;
    }

    return (
        <div className="container mt-4">
            <h2>Relatório</h2>

            <RiskChart data={historico} />
            <HeatmapTimeline
                timeline={historico.timeline || []}
            />
            <div className="mt-4">

                <p>
                    <strong>Tempo Adequado:</strong>
                    {" "}
                    {historico.tempo_adequado_s.toFixed(1)} s
                </p>

                <p>
                    <strong>Tempo Atenção:</strong>
                    {" "}
                    {historico.tempo_atencao_s.toFixed(1)} s
                </p>

                <p>
                    <strong>Tempo Crítico:</strong>
                    {" "}
                    {historico.tempo_critico_s.toFixed(1)} s
                </p>

                <p>
                    <strong>Total de Frames:</strong>
                    {" "}
                    {historico.total_frames}
                </p>

            </div>
            <Button
                variant="danger"
                onClick={limpar}
            >
                Reiniciar Histórico
            </Button>
        </div>
    );
}