import React, { useEffect, useState } from 'react'
import '../App.css';

export default function Health() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [health, setHealth] = useState({});
    const [error, setError] = useState(null)

	const getHealth = () => {
	
        fetch(`http://acit3855-kafka.canadacentral.cloudapp.azure.com:8120/health`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Health")
                setHealth(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getHealth(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getHealth]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Service Health</h1>
                <table className={"HealthTable"}>
					<tbody>
						<tr>
                        <td>Receiver:   </td>
                        <td>{health['receiver']}</td>
						</tr>
						<tr>
							<td>Storage:   </td>
							<td>{health['storage']}</td>
						</tr>
						<tr>
							<td>Processing:   </td>
							<td>{health['processing']}</td>
						</tr>
						<tr>
							<td>Audit:   </td>
							<td>{health['audit']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {Math.abs(new Date() - health['last_updated'].replace(/-/g,'/'))}</h3>
            </div>
        )
    }
}
