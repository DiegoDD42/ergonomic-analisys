import { useEffect, useRef, useState } from "react";
import Webcam from "react-webcam";
import Badge from "react-bootstrap/Badge";


import { inferImage } from "../services/api";

export default function WebcamMonitor() {
    console.log("WebcamMonitor renderizado");
    function corRisco(risco) {

        switch (risco) {

            case "adequado":
                return "success";

            case "atenção":
                return "warning";

            case "critico":
            case "crítico":
                return "danger";

            default:
                return "secondary";
        }
    }

    const processandoRef = useRef(false);

    const webcamRef = useRef(null);

    const canvasRef = useRef(null);

    const [resultado, setResultado] = useState(null);

    useEffect(() => {
         console.log("Interval criado");

        const interval = setInterval(async () => {

            if (processandoRef.current)
                return;

            if (!webcamRef.current)
                return;

            const screenshot =
                webcamRef.current.getScreenshot();

            if (!screenshot)
                return;

            processandoRef.current = true;

            try {

                const blob = await fetch(screenshot)
                    .then(r => r.blob());

                const file = new File(
                    [blob],
                    "frame.jpg",
                    { type: "image/jpeg" }
                );

                const data =
                    await inferImage(file);

                setResultado(data);

                console.log(
                    "Keypoints:",
                    data.keypoints?.length
                );

            } catch (error) {

                console.error(error);

            } finally {

                processandoRef.current = false;

            }

        }, 1000);

        return () => clearInterval(interval);

    }, []);

    const skeleton = [

        [5, 7],
        [7, 9],

        [6, 8],
        [8, 10],

        [5, 6],

        [5, 11],
        [6, 12],

        [11, 12],

        [11, 13],
        [13, 15],

        [12, 14],
        [14, 16]
    ];

    useEffect(() => {

        if (!resultado)
            return;

        if (!resultado.pessoa_detectada)
            return;

        if (!resultado.keypoints)
            return;

        const canvas = canvasRef.current;

        if (!canvas)
            return;

        const ctx = canvas.getContext("2d");

        ctx.clearRect(
            0,
            0,
            canvas.width,
            canvas.height
        );


        resultado.keypoints.forEach(point => {

            if (point.confidence < 0.3)
                return;

            ctx.beginPath();

            ctx.arc(
                point.x,
                point.y,
                5,
                0,
                Math.PI * 2
            );

            ctx.fill();

        });
        skeleton.forEach(([a, b]) => {

            const p1 =
                resultado.keypoints[a];

            const p2 =
                resultado.keypoints[b];

            if (!p1 || !p2)
                return;

            if (
                p1.confidence < 0.3 ||
                p2.confidence < 0.3
            )
                return;

            ctx.beginPath();

            ctx.moveTo(
                p1.x,
                p1.y
            );

            ctx.lineTo(
                p2.x,
                p2.y
            );

            ctx.stroke();

        });

    }, [resultado]);

    return (
        <div
            style={{
                position: "relative",
                width: 800
            }}
        >

            <Webcam
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                width={800}
            />
            <canvas
                ref={canvasRef}
                width={800}
                height={600}
                style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    pointerEvents: "none"
                }}
            />

            {resultado && (
                <div className="mt-3">

                    <h4>

                        Risco Atual:

                        {" "}

                        <Badge
                            bg={corRisco(
                                resultado.risco_geral
                            )}
                        >
                            {resultado.risco_geral}
                        </Badge>

                    </h4>
                    {
                        resultado?.angulos &&
                        (
                            <div className="mt-3">

                                <h5>Ângulos</h5>

                                {
                                    Object.entries(resultado.angulos)
                                        .map(([nome, dados]) => (

                                            <div key={nome}>

                                                <strong>
                                                    {nome}
                                                </strong>

                                                {" : "}

                                                {dados.valor.toFixed(1)}°

                                                {" ("}

                                                {dados.classificacao}

                                                {")"}

                                            </div>

                                        ))
                                }

                            </div>
                        )
                    }
                </div>

            )}

        </div>
    );
}