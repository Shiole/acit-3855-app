import logo from './logo.png';
import './App.css';

import Health from './components/Health'
import EndpointAudit from './components/EndpointAudit'
import AppStats from './components/AppStats'

function App() {

    const endpoints = ["order", "delivery"]

    const rendered_endpoints = endpoints.map((endpoint) => {
        return <EndpointAudit key={endpoint} endpoint={endpoint}/>
    })

    return (
        <div className="App">
            <img src={logo} className="App-logo" alt="logo" height="200px" width="200px"/>
            <div>
                <AppStats/>
                <h1>Audit Endpoints</h1>
                {rendered_endpoints}
                <br></br>
                <Health/>
            </div>
        </div>
    );

}



export default App;
