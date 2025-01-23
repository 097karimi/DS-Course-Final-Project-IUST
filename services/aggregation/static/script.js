document.getElementById('fetchData').addEventListener('click', async () => {
    const container = document.getElementById('stockContainer');
    container.innerHTML = '<p>Loading...</p>';

    try {
        const response = await fetch('/api/stock_data/');
        const data = await response.json();

        container.innerHTML = data.map(stock => `
            <div class="stockCard">
                <h3>${stock.stock_symbol}</h3>
                <p><strong>Topic:</strong> ${stock.topic}</p>
                <p><strong>Signal:</strong> ${stock.signal}</p>
                <p><strong>Local Time:</strong> ${new Date(stock.local_time).toLocaleString()}</p>
                <p><strong>Open:</strong> ${stock.open}</p>
                <p><strong>Close:</strong> ${stock.close}</p>
                <p><strong>Volume:</strong> ${stock.volume}</p>
            </div>
        `).join('');
    } catch (error) {
        container.innerHTML = '<p>Error loading data.</p>';
    }
});