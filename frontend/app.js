// frontend/app.js
const { createApp, ref, nextTick } = Vue;

createApp({
    setup() {
        const userPrompt = ref("");
        const latestPayload = ref(null);
        const loading = ref(false);
        let chartInstance = null; // Reference pointer to handle Chart.js lifecycles

        const submitQuery = async () => {
            if (!userPrompt.value.trim()) return;

            loading.value = true;
            latestPayload.value = null; // Clear previous state to show skeleton loader

            try {
                const response = await fetch("http://127.0.0.1:8000/api/v1/analytics/query", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ prompt: userPrompt.value })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || "Server connection error.");
                }

                const data = await response.json();
                console.log("📦 Data intercepted by Vue App:", data);

                // EXPLICIT REACTIVE STATE CORRECTION:
                // Forces Vue to intercept, deep-watch, and bind the parameters to the UI template
                latestPayload.value = {
                    insights_narrative: data.insights_narrative || "No narrative compiled.",
                    executed_sql: data.executed_sql || "SELECT NULL;",
                    dataset: Array.isArray(data.dataset) ? data.dataset : [],
                    visualization_config: data.visualization_config || { chart_type: "table", chart_title: "Data Matrix View" }
                };

                // Kill the loading indicator BEFORE triggering visual canvas draws
                loading.value = false;

                // Wait for Vue's Virtual DOM to finish drawing the elements, then render the graph
                await nextTick();
                renderVisualization(latestPayload.value);

            } catch (err) {
                loading.value = false;
                alert(`Pipeline Processing Exception: ${err.message}`);
                console.error(err);
            }
        };

        const renderVisualization = (payload) => {
            const config = payload.visualization_config;
            const dataset = payload.dataset;
            const canvasElement = document.getElementById("agentRenderedChartCanvas");

            // 1. Defensively wipe out old Chart instances to prevent canvas freezing
            if (chartInstance) {
                chartInstance.destroy();
                chartInstance = null;
            }

            // 2. Halt if no canvas context is mounted or if the layout requires a raw table
            if (!canvasElement || !config || config.chart_type === 'table' || !dataset.length) {
                console.log("ℹ️ Rendering engine falling back to dynamic HTML table layout.");
                return; 
            }

            try {
                // 3. Map dynamic case-insensitive row properties from database payload columns
                const xKey = config.x_axis_key;
                const yKey = config.y_axis_key;

                const labels = dataset.map(row => row[xKey] !== undefined ? row[xKey] : "N/A");
                const dataValues = dataset.map(row => {
                    const val = row[yKey];
                    return typeof val === 'number' ? val : parseFloat(val) || 0;
                });

                const chartMappingType = ['line', 'pie', 'bar'].includes(config.chart_type) ? config.chart_type : 'bar';

                // 4. Initialize Chart.js with dark-themed configurations
                chartInstance = new Chart(canvasElement, {
                    type: chartMappingType,
                    data: {
                        labels: labels,
                        datasets: [{
                            label: config.chart_title || "Metrics Breakdown",
                            data: dataValues,
                            backgroundColor: chartMappingType === 'line' ? 'rgba(16, 185, 129, 0.15)' : [
                                'rgba(16, 185, 129, 0.75)',
                                'rgba(59, 130, 246, 0.75)',
                                'rgba(245, 158, 11, 0.75)',
                                'rgba(239, 68, 68, 0.75)',
                                'rgba(139, 92, 246, 0.75)'
                            ],
                            borderColor: '#10b981',
                            borderWidth: 2,
                            tension: 0.35
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { 
                                display: chartMappingType === 'pie', 
                                labels: { color: '#9ca3af', font: { family: 'monospace' } } 
                            }
                        },
                        scales: chartMappingType !== 'pie' ? {
                            y: { grid: { color: '#374151' }, ticks: { color: '#9ca3af' } },
                            x: { grid: { color: '#374151' }, ticks: { color: '#9ca3af' } }
                        } : {}
                    }
                });
                console.log("🎯 Chart.js graph successfully plotted.");
            } catch (chartError) {
                console.error("❌ Chart.js compiler crashed: ", chartError);
            }
        };

        return {
            userPrompt,
            latestPayload,
            loading,
            submitQuery
        };
    }
}).mount("#app");