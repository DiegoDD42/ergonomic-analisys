import {
    BrowserRouter,
    Routes,
    Route,
    Link
} from "react-router-dom";

import Navbar from "react-bootstrap/Navbar";
import Nav from "react-bootstrap/Nav";

import Monitor from "./pages/Monitor";
import Report from "./pages/Report";

function App() {

    return (
        <BrowserRouter>

            <Navbar bg="dark" data-bs-theme="dark">

                <div className="container">

                    <Navbar.Brand>
                        Ergonomic Analysis
                    </Navbar.Brand>

                    <Nav>
                        <Nav.Link as={Link} to="/">
                            Monitor
                        </Nav.Link>

                        <Nav.Link as={Link} to="/report">
                            Relatório
                        </Nav.Link>
                    </Nav>

                </div>

            </Navbar>

            <Routes>
                <Route path="/" element={<Monitor />} />
                <Route path="/report" element={<Report />} />
            </Routes>

        </BrowserRouter>
    );
}

export default App;