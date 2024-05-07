// Cuando se elige un tipo de comparación, se actualiza el dropdown
document.addEventListener('DOMContentLoaded', function () {
    const dropdownMenu = document.getElementById('comparisonTypeDropdown');
    const seasonChoices = document.querySelectorAll('.comparison-choice');

    seasonChoices.forEach(function (choice) {
        choice.addEventListener('click', function () {
            dropdownMenu.textContent = choice.textContent;
        });
    });
});

// Cambia la vista de tarjetas según el dropdown de comparaciones
document.addEventListener('DOMContentLoaded', () => {
    const comparisonChoices = document.querySelectorAll('.comparison-choice');
    comparisonChoices.forEach(choice => {
        choice.addEventListener('click', event => {
            event.preventDefault();
            const value = choice.getAttribute('data-value');
            if (value === 'conference') {
                document.getElementById('totalView').classList.add('d-none');
                document.getElementById('conferenceView').classList.remove('d-none');
            } else {
                document.getElementById('totalView').classList.remove('d-none');
                document.getElementById('conferenceView').classList.add('d-none');
            }
        });
    });
});

// Cuando se elige una temporada, se actualiza el dropdown y las tablas
document.addEventListener('DOMContentLoaded', function () {
    const dropdownMenu = document.getElementById('seasonDropdown');
    const seasonChoices = document.querySelectorAll('.season-choice');

    seasonChoices.forEach(function (choice) {
        choice.addEventListener('click', function () {
            event.preventDefault();
            dropdownMenu.textContent = choice.textContent;
            const selectedSeason = choice.getAttribute('data-value');
            // Función que actualiza las tablas, pasando la temporada seleccionada
            fetchClassifications(selectedSeason);

        });
    });
});

// Actualiza las tablas de clasificación al cambiar la temporada del dropdown
function fetchClassifications(season) {
    fetch(`/classifications?season=${season}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => response.json())
        .then(data => {
            // Asumiendo que tienes funciones updateTable() para actualizar cada tabla
            console.log(data);
            updateTable('norm_classif_table', data.norm_classif, "All"); // Actualiza la tabla normal
            updateTable('new_classif_table', data.new_classif, "All"); // Actualiza la nueva tabla

            updateTableConference('norm_classif_east', data.norm_classif, "East"); // Actualiza la tabla normal de la conferencia este
            updateTableConference('new_classif_east', data.new_classif, "East"); // Actualiza la tabla nueva de la conferencia este
            updateTableConference('norm_classif_west', data.norm_classif, "West"); // Actualiza la tabla normal de la conferencia oeste
            updateTableConference('new_classif_west', data.new_classif, "West"); // Actualiza la tabla nueva de la conferencia oeste
        })
        .catch(error => console.error('Error:', error));
}


//Borra la tabla y vuelve a actualizarla equipo a equipo ya que no se refresca la página y el bucle for no puede volver a ejecutarse
function updateTable(tableId, classifData, conference) {
    const tableBody = document.querySelector(`#${tableId} tbody`);
    tableBody.innerHTML = ''; // Limpia la tabla actual

    classifData.forEach((team, index) => {
        // Usamos index + 1 para comenzar la numeración desde 1 en lugar de 0
        const position = index + 1;
        const row = `<tr class="team-row">
                        <td>${position}</td>
                        <td>${team.name}</td>
                        <td><img src="${team.logo}" alt="Logo" style="width: 35px; height: 35px;"></td>
                        <td>
                        <button class="btn" onclick="toggleTeamVisibility('${team.name}', this)">
                            <i class="far fa-square"></i>
                        </button>
                        </td>
                    </tr>`;
        tableBody.innerHTML += row; // Agrega la fila a la tabla
    });
}


//Borra la tabla y vuelve a actualizarla equipo a equipo ya que no se refresca la página y el bucle for no puede volver a ejecutarse
//Especial para tablas de conferencia
function updateTableConference(tableId, classifData, conference) {
    const tableBody = document.querySelector(`#${tableId} tbody`);
    tableBody.innerHTML = ''; // Limpia la tabla actual
    let contador = 0;

    classifData.forEach((team, index) => {
        if (conference === `${team.conference}`) {
            // Usamos index + 1 para comenzar la numeración desde 1 en lugar de 0
            contador++; 
            const row = `<tr class="team-row">
                            <td>${contador}</td>
                            <td>${team.name}</td>
                            <td><img src="${team.logo}" alt="Logo" style="width: 35px; height: 35px;"></td>
                            <td>
                                <button class="btn" onclick="toggleTeamVisibility('${team.name}', this)">
                                <i class="far fa-square"></i>
                            </button>
                            </td>
                        </tr>`;
            tableBody.innerHTML += row; // Agrega la fila a la tabla
        }
    });
}

function toggleTeamVisibility(teamName, button) {
    var isChecked = button.querySelector('i').classList.contains('fa-check-square');
    // Toggle icon
    if (isChecked) {
        button.querySelector('i').classList.remove('fa-check-square');
        button.querySelector('i').classList.add('fa-square');
        resetView(); // Restablecer la visualización de todas las filas
    } else {
        button.querySelector('i').classList.remove('fa-square');
        button.querySelector('i').classList.add('fa-check-square');
        // Filtrar filas
        var tables = document.querySelectorAll('.table');
        tables.forEach(table => {
            var rows = table.querySelectorAll('.team-row');
            rows.forEach(row => {
                var currentTeam = row.cells[1].textContent;
                var rowButton = row.querySelector('button i');
                if (currentTeam !== teamName) {
                    row.style.visibility = 'hidden'; // Ocultar las filas que no coinciden
                } else {
                    row.style.visibility = 'visible'; // Mostrar la fila que coincide
                    rowButton.classList.remove('fa-square');
                    rowButton.classList.add('fa-check-square');
                }
            });
        });
    }
}
    
// Cuando se elige un equipo para ver sus gráficos, se actualiza el dropdown y se dibujan los gráficos.
document.addEventListener('DOMContentLoaded', () => {
    const teamChoices = document.querySelectorAll('.team-choice');
    teamChoices.forEach(choice => {
        choice.addEventListener('click', event => {
            event.preventDefault();
            const selectedTeam = choice.getAttribute('data-value');
            document.getElementById('teamDropdown').textContent = selectedTeam;
            drawCharts(selectedTeam);
        });
    });
});

function resetView() {
    var rows = document.querySelectorAll('.team-row');
    rows.forEach(row => {
        row.style.visibility = 'visible'; // Restablecer la visualización de todas las filas
        var rowButton = row.querySelector('button i');
        rowButton.classList.remove('fa-check-square');
        rowButton.classList.add('fa-square'); // Desmarcar todos los botones
    });
}

function drawCharts(selectedTeam) {
    // Filtra las posiciones del equipo seleccionado
    const normalPositions = allClassifications
        .filter(item => item.name === selectedTeam && item.season.includes("normal"))
        .map(item => ({ season: item.season.split('_')[0], position: item.position }));

    const newPositions = allClassifications
        .filter(item => item.name === selectedTeam && item.season.includes("new"))
        .map(item => ({ season: item.season.split('_')[0], position: item.position }));

    console.log(normalPositions);
    console.log(newPositions);

    // Destruye los gráficos si ya existen
    if (normalChart !== null) {
        normalChart.destroy();
    }
    if (newChart !== null) {
        newChart.destroy();
    }

    // Dibuja los gráficos
    normalChart = drawChart('normalChart', normalPositions, 'Clasificación Normal');
    newChart = drawChart('newChart', newPositions, 'Clasificación Nueva');
}

function drawChart(chartId, positions, title) {
    const ctx = document.getElementById(chartId).getContext('2d');
    // Calcular la Media de las Posiciones
    // Reduce recorre cada elemento y realiza una operación en cada uno de ellos reduciendo el array a un único valor.
    const average = positions.reduce((acc, pos) => acc + pos.position, 0) / positions.length;

    //Opciones de gráfico
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: positions.map(pos => pos.season),
            datasets: [{
                label: title,
                data: positions.map(pos => pos.position),
                borderColor: 'rgba(230, 126, 34, 0.5)',
                backgroundColor: 'rgba(230, 126, 34, 0.5)',
                pointRadius: 5,
                pointHoverRadius: 7,
                borderWidth: 2,
                lineTension: 0.3
            }]
        },
        options: {
            scales: {
                y: {
                    reverse: true,
                    min: 1,
                    ticks: {
                        callback: function(value, index, values) {
                            return value + 'º'; // Agregar "º" al valor del eje y
                        },
                        font: {
                            size: 15, // Tamaño de la fuente de la leyenda
                            weight: 'bold', // Grosor de la fuente (normal, bold)
                        },
                        stepSize: 5,
                        precision: 0
                    }
                },
                x: {
                    ticks: {
                        font: {
                            size: 15, // Tamaño de la fuente de la leyenda
                            weight: 'bold', // Grosor de la fuente (normal, bold)
                        }
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: title,
                    font: {
                        size: 20
                    }
                },
                legend: {
                    display: false,
                    position: 'bottom'
                }
            }
        }
    });

    // Crear el texto con la media debajo del gráfico
    const parentElement = ctx.canvas.parentElement;

    // Eliminar cualquier texto de media existente
    const previousMediaText = parentElement.querySelector('.media-text');
    if (previousMediaText) {
        parentElement.removeChild(previousMediaText);
    }

    // Añadir el nuevo texto de media
    const mediaText = document.createElement('p');
    mediaText.textContent = `Media: ${average.toFixed(0)}`;
    // Clase para identificarlo
    mediaText.className = 'media-text'; 
    mediaText.style.fontSize = '20px';
    mediaText.style.textAlign = 'center';
    mediaText.style.fontFamily = 'Arial, sans-serif';
    mediaText.style.marginTop = '20px';
    mediaText.style.fontWeight = 'bold';

    parentElement.appendChild(mediaText);

    return chart;
}

teamDropdown.addEventListener("click", function () {

    const loadingIndicator = document.getElementById("loadingIndicator");
    const teamDropdownWrapper = document.getElementById("teamDropdownWrapper");
    
    if (!isInitialized) {

        teamDropdownWrapper.style.visibility = "hidden"; // Ocultar el dropdown
        loadingIndicator.style.visibility = "visible"; // Mostrar el spinner

        fetch("/initialize_seasons", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        })
        .then(response => response.json())
        .then(data => {
            allClassifications = data.all_classif;
            console.log(allClassifications);
        })
        .catch(error => {
            console.error("Error:", error);
            alert("An error occurred while initializing seasons.");
        })
        .finally(() => {
            teamDropdownWrapper.style.visibility = "visible"; // Mostrar el dropdown
            loadingIndicator.style.visibility = "hidden"; // Ocultar el spinner
            isInitialized = true; // Establecer que ya está inicializado

        });
    }
});