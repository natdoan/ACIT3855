import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://acit3855-kafka.westus2.cloudapp.azure.com/processing/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Calorie Intake</th>
							<th>Weight</th>
						</tr>
						<tr>
							<td># CI: {stats['num_ci_reports']}</td>
							<td># W: {stats['num_w_reports']}</td>
						</tr>
						<tr>
							<td colspan="2">Max Calorie-Intake Report: {stats['max_ci_report']}</td>
						</tr>
                        <tr>
							<td colspan="2">Min Calorie-Intake Report: {stats['min_ci_report']}</td>
						</tr>
                        <tr>
							<td colspan="2">Max Weight Report: {stats['max_w_report']}</td>
						</tr>
                        <tr>
							<td colspan="2">Min Weight Report: {stats['min_w_report']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>
        )
    }
}
