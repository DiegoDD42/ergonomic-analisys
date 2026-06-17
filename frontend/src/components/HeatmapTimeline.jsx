import Card from "react-bootstrap/Card";

export default function HeatmapTimeline({ timeline }) {

    function cor(risco) {

        switch (risco) {

            case "adequado":
                return "#198754";

            case "atencao":
                return "#ffc107";

            case "critico":
                return "#dc3545";

            default:
                return "#6c757d";
        }
    }

    return (
        <Card className="mt-4">

            <Card.Body>

                <Card.Title>
                    Heatmap Temporal
                </Card.Title>

                <div
                    className="d-flex flex-wrap"
                    style={{
                        gap: "2px"
                    }}
                >

                    {timeline.map((risco, index) => (

                        <div
                            key={index}
                            title={`${index}s - ${risco}`}
                            style={{
                                width: "12px",
                                height: "30px",
                                backgroundColor: cor(risco),
                                borderRadius: "2px"
                            }}
                        />

                    ))}

                </div>

                <div className="mt-3 d-flex gap-3">

                    <span>
                        🟩 Adequado
                    </span>

                    <span>
                        🟨 Atenção
                    </span>

                    <span>
                        🟥 Crítico
                    </span>

                </div>

            </Card.Body>

        </Card>
    );
}