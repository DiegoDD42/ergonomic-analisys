import {
    PieChart,
    Pie,
    Tooltip,
    Cell,
    Legend
} from "recharts";

export default function RiskChart({ data }) {

    const chartData = [
        {
            name: "Adequado",
            value: data.tempo_adequado_s || 0
        },
        {
            name: "Atenção",
            value: data.tempo_atencao_s || 0
        },
        {
            name: "Crítico",
            value: data.tempo_critico_s || 0
        }
    ];

    const colors = [
        "#28a745",
        "#ffc107",
        "#dc3545"
    ];

    return (
        <PieChart width={500} height={300}>
            <Pie
                data={chartData}
                dataKey="value"
                nameKey="name"
                outerRadius={100}
                label
            >
                {chartData.map((entry, index) => (
                    <Cell
                        key={index}
                        fill={colors[index]}
                    />
                ))}
            </Pie>

            <Tooltip />
            <Legend />
        </PieChart>
    );
}